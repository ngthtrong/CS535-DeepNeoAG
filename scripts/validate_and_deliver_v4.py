"""Verify v4 against the retained source, then publish the local deliverables."""
import hashlib
import json
import posixpath
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'tmp/presentation_v4'
OUT = ROOT / 'presentation'
SKILL = Path('C:/Users/jhiny/.codex/plugins/cache/openai-primary-runtime/presentations/26.1025.11240/skills/presentations')
NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
R = '{' + NS['r'] + '}'

def read_json(name):
    return json.loads((BUILD / name).read_text(encoding='utf-8-sig'))

def slides(z):
    p = ET.fromstring(z.read('ppt/presentation.xml'))
    rels = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
    return [(int(s.get('id')), posixpath.normpath('ppt/' + rels[s.get(R+'id')]))
            for s in p.find('p:sldIdLst', NS)]

def text(node):
    return '\n'.join(t.text or '' for t in node.findall('.//a:t', NS))

def notes(z, part):
    relpath = posixpath.dirname(part) + '/_rels/' + posixpath.basename(part) + '.rels'
    for rel in ET.fromstring(z.read(relpath)):
        if rel.get('Type', '').endswith('/notesSlide'):
            path = posixpath.normpath(posixpath.dirname(part) + '/' + rel.get('Target'))
            return text(ET.fromstring(z.read(path)))
    return ''

def verify():
    mapping = read_json('slide_map.json')
    removed = read_json('removed_footnotes.json')
    assert len(mapping) == 38
    assert [(m['slide'], m['source_number']) for m in mapping if m['hidden']] == [
        (34, 20), (35, 21), (36, 26), (37, 30), (38, 31)]
    assert mapping[26]['source_number'] == 32
    assert [m['source_number'] for m in mapping[27:33]] == list(range(33, 39))
    with ZipFile(OUT / 'DeepNeoAG_Operating_Review_2026-10-26_v3.pptx') as source, ZipFile(BUILD / 'candidate.pptx') as output:
        source_by_id = {i: ET.fromstring(source.read(p)) for i,p in slides(source)}
        candidate_slides = slides(output)
        assert [i for i,p in candidate_slides] == [m['slide_id'] for m in mapping]
        assert len({i for i,p in candidate_slides}) == 38
        for m, (sid, part) in zip(mapping, candidate_slides):
            slide = ET.fromstring(output.read(part))
            assert (slide.get('show') == '0') == m['hidden']
            body = notes(output, part)
            assert 'SCRIPT TRÌNH BÀY' in body
            if m['script']:
                assert m['script'] in body, ('missing speaking script',m['slide'])
            for shape in slide.findall('.//p:sp', NS):
                prop = shape.find('p:nvSpPr/p:cNvPr', NS)
                name = prop.get('name', '') if prop is not None else ''
                off = shape.find('p:spPr/a:xfrm/a:off', NS)
                ext = shape.find('p:spPr/a:xfrm/a:ext', NS)
                if off is not None and ext is not None and text(shape):
                    assert not (int(off.get('y')) >= 470*12700 and int(ext.get('cy')) <= 40*12700
                                and not name.startswith('Slide Number Placeholder')), ('footer remains',m['slide'],name)
            if m['source_number'] != 32:
                source_tables = source_by_id[sid].findall('.//a:tbl',NS)
                final_tables = slide.findall('.//a:tbl',NS)
                assert [text(t) for t in source_tables] == [text(t) for t in final_tables], ('table changed',m['slide'])
            if m['source_number'] in (12,13,14):
                assert len(slide.findall('.//p:grpSp',NS)) == len(source_by_id[sid].findall('.//p:grpSp',NS))
            for footnote in [r for r in removed if r['original_slide'] == m['source_number']]:
                assert footnote['text'] not in text(slide), ('footnote remains',m['slide'])
                # Newlines in PPT text are represented as separate paragraphs.
                assert footnote['text'].replace('\r','\n') in body
        cover = text(ET.fromstring(output.read(candidate_slides[0][1])))
        for name in ('Nguyễn Thanh Trọng','Võ Trần Vũ Khoa','Mai Nhật Minh','CS535'):
            assert name in cover
        show = ET.fromstring(output.read('ppt/presProps.xml')).find('p:showPr',NS)
        showrange = show.find('p:sldRg',NS)
        assert showrange.get('st') == '1' and showrange.get('end') == '27'
        assert len(ET.fromstring(output.read(candidate_slides[26][1])).findall('.//a:tbl/a:tr',NS)) == 6
        source_media = {hashlib.sha256(source.read(n)).hexdigest() for n in source.namelist() if n.startswith('ppt/media/')}
        final_media = {hashlib.sha256(output.read(n)).hexdigest() for n in output.namelist() if n.startswith('ppt/media/')}
        assert final_media <= source_media, 'Unexpected image substitution'
    fit = read_json('text_fit.json')
    overflows = [f for f in fit if f['bound_height'] > f['height']+2 or f['bound_width'] > f['width']+2]
    assert not overflows, overflows
    import fitz
    pdf=fitz.open(BUILD/'main.pdf')
    assert len(pdf) == 27
    assert 'Answers to the five research questions' in pdf[-1].get_text()
    assert 'Nguyễn Thanh Trọng' in pdf[0].get_text()
    assert len(list((BUILD/'rendered').glob('slide-*.png'))) == 38
    results = {'slide_count':38,'main_slide_count':27,'hidden_slide_count':5,
               'removed_footer_objects':len(removed),'script_in_notes':38,
               'unchanged_evidence_tables':'pass','editable_diagram_groups':'pass',
               'text_fit':'pass','main_pdf_pages':len(pdf),'status':'pass'}
    for kind, args in (
        ('integrity', []),
        ('layout', ['--expected-slide-size-emu','12192000,6858000','--expected-slide-count','38',
                    '--validate-bullet-geometry','--validate-heading-fit','--require-native-table-slide','27'])
    ):
        validator = SKILL/'container_tools'/('inspect_presentation_package_integrity.py' if kind=='integrity' else 'inspect_presentation_layout_geometry.py')
        run=subprocess.run([sys.executable,str(validator),str(BUILD/'candidate.pptx'),*args],capture_output=True,text=True,encoding='utf-8')
        (BUILD/f'{kind}.json').write_text(run.stdout,encoding='utf-8')
        assert run.returncode==0,run.stderr
        results[kind] = json.loads(run.stdout)
    (BUILD/'verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    return mapping, results

def deliver(mapping):
    script = ['# Script trình bày DeepNeoAG v4', '',
              'Số slide dưới đây theo bản v4. Phần trình bày chính: slide 1–27. '
              'Slide phân phần không có lời thoại. Script cũng nằm trong speaker notes của PowerPoint.', '',
              '## Phần trình bày chính', '']
    for m in mapping:
        if m['slide']==28:
            script += ['## Phụ lục tham khảo, ngoài luồng trình bày chính', '']
        if m['slide']==34:
            script += ['## Các slide đã chuyển xuống cuối và ẩn', '',
                       'Chỉ dùng khi cần trả lời câu hỏi. Số cũ: 20, 21, 26, 30, 31.', '']
        label = f"Slide {m['slide']} — {m['title']}"
        if m['slide']>=28: label+=f" (số cũ: {m['source_number']})"
        script += ['### '+label, '', m['script'] or '*Không có lời thoại.*', '']
    (OUT/'SCRIPT_TRINH_BAY_v4.md').write_text('\n'.join(script),encoding='utf-8')
    guide = ['# DeepNeoAG v4', '',
             'Luồng trình chiếu mặc định và PDF gồm slide 1–27, kết thúc ở phần trả lời 5 câu hỏi. '
             'Phụ lục gốc ở 28–33 vẫn truy cập được trong PowerPoint. '
             'Năm slide được yêu cầu loại khỏi phần trình bày nằm ở 34–38 và được đặt Hide Slide.', '',
             'Script tiếng Việt ở `SCRIPT_TRINH_BAY_v4.md` và speaker notes. '
             'Các footnote đã bỏ khỏi mặt slide. Những lưu ý cần diễn giải được giữ trong notes.', '',
             '| Số v4 | Số in trên v3 | Nội dung | Trạng thái |',
             '|---|---|---|---|']
    for m in mapping:
        status='Ẩn' if m['hidden'] else ('Phụ lục' if m['slide']>=28 else 'Trình bày chính')
        guide.append(f"| {m['slide']} | {m['source_number']} | {m['title']} | {status} |")
    (OUT/'SLIDE_GUIDE_v4.md').write_text('\n'.join(guide)+'\n',encoding='utf-8')
    final = OUT/'DeepNeoAG_Operating_Review_2026-10-26_v4.pptx'
    pdf = OUT/'DeepNeoAG_Operating_Review_2026-10-26_v4.pdf'
    assert not final.exists() and not pdf.exists(), 'Do not overwrite an existing delivery.'
    shutil.copy2(BUILD/'candidate.pptx', final)
    shutil.copy2(BUILD/'main.pdf', pdf)
    print('Delivered v4 PPTX, main-deck PDF and Vietnamese speaking script.')

if __name__=='__main__':
    mapping, results=verify()
    print(json.dumps({k:v for k,v in results.items() if k not in ('integrity','layout')},ensure_ascii=False))
    if '--deliver' in sys.argv: deliver(mapping)
