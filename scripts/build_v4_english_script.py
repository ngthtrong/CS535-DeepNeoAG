"""Create an English script and update only the notes in a copy of the open v4."""
import json
import posixpath
import re
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape
from zipfile import ZipFile

from presentation_v4_english import SCRIPT_EN

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT/'tmp/presentation_v4_english'
OUT = ROOT/'presentation'
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
RID='{'+NS['r']+'}id'

def body_text(xml):
    root=ET.fromstring(xml)
    for shape in root.findall('p:cSld/p:spTree/p:sp',NS):
        ph=shape.find('p:nvSpPr/p:nvPr/p:ph',NS)
        if ph is not None and ph.get('type')=='body':
            return '\n'.join(''.join(t.text or '' for t in p.findall('.//a:t',NS))
                             for p in shape.findall('p:txBody/a:p',NS))
    raise AssertionError('Missing notes body')

def rewrite_notes(xml, speech):
    original=body_text(xml)
    assert original.startswith('SCRIPT TRÌNH BÀY'), original[:80]
    marker=re.search(r'\n(?:GHI CHÚ DIỄN GIẢI|SOURCE NOTES FROM V3|SOURCES)\n',original)
    remainder=original[marker.start():] if marker else ''
    remainder=remainder.replace('GHI CHÚ DIỄN GIẢI','INTERPRETATION NOTES')
    content='PRESENTATION SCRIPT\n'+speech+remainder
    paragraphs=''.join('<a:p><a:pPr><a:buNone/></a:pPr><a:r><a:rPr lang="en-US"/>'
                       '<a:t>'+escape(line)+'</a:t></a:r></a:p>' for line in content.split('\n'))
    changed=0
    def change_shape(match):
        nonlocal changed
        block=match.group(0)
        if not re.search(r'<p:ph\b[^>]*\btype="body"',block):
            return block
        changed+=1
        return re.sub(r'(<p:txBody>.*?<a:lstStyle\s*/>).*?(</p:txBody>)',
                      lambda m:m.group(1)+paragraphs+m.group(2),block,count=1,flags=re.S)
    result=re.sub(r'<p:sp\b[^>]*>.*?</p:sp>',change_shape,xml,flags=re.S)
    assert changed==1
    assert body_text(result)==content
    return result.encode('utf-8')

def main():
    source=BUILD/'source.pptx'
    candidate=BUILD/'candidate_EN.pptx'
    old_map=json.loads((ROOT/'tmp/presentation_v4/slide_map.json').read_text(encoding='utf-8-sig'))
    by_id={m['slide_id']:m for m in old_map}
    script=['# DeepNeoAG v4 Presentation Script', '',
            'Slide numbers follow v4. The main presentation covers slides 1–27. '
            'Section divider slides have no spoken script. The same English script is included in the PowerPoint speaker notes.', '',
            '## Main presentation', '']
    patches={}
    with ZipFile(source) as z:
        presentation=ET.fromstring(z.read('ppt/presentation.xml'))
        rels={r.get('Id'):r.get('Target') for r in ET.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
        ids=list(presentation.find('p:sldIdLst',NS))
        assert len(ids)==38
        for number,sld in enumerate(ids,1):
            m=by_id[int(sld.get('id'))]
            speech=SCRIPT_EN[m['source_number']]
            part=posixpath.normpath('ppt/'+rels[sld.get(RID)])
            slide=ET.fromstring(z.read(part))
            title=m['title']
            for shape in slide.findall('p:cSld/p:spTree/p:sp',NS):
                prop=shape.find('p:nvSpPr/p:cNvPr',NS)
                if prop is not None and (prop.get('name','').startswith('Title') or prop.get('name','').startswith('Google Shape')):
                    title=' '.join(t.text or '' for t in shape.findall('.//a:t',NS))
                    break
            if number==28:
                script+=['## Reference appendix, outside the main presentation', '']
            if number==34:
                script+=['## Hidden slides, excluded from the main presentation', '',
                         'Use only if needed during questions. Original slide numbers: 20, 21, 26, 30, 31.', '']
            label=f'Slide {number} — {title}'
            if number>=28: label+=f" (original slide {m['source_number']})"
            script+=['### '+label, '', speech or '*No spoken script.*', '']
            relpart=posixpath.dirname(part)+'/_rels/'+posixpath.basename(part)+'.rels'
            notes_rels=[r for r in ET.fromstring(z.read(relpart)) if r.get('Type','').endswith('/notesSlide')]
            assert len(notes_rels)==1
            notes_part=posixpath.normpath(posixpath.dirname(part)+'/'+notes_rels[0].get('Target'))
            patches[notes_part]=rewrite_notes(z.read(notes_part).decode('utf-8'),speech)
        with ZipFile(candidate,'w') as out:
            for info in z.infolist():
                out.writestr(info,patches.get(info.filename,z.read(info.filename)))
    assert len(patches)==38
    with ZipFile(source) as before,ZipFile(candidate) as after:
        assert before.namelist()==after.namelist()
        changed=[n for n in before.namelist() if before.read(n)!=after.read(n)]
        assert sorted(changed)==sorted(patches)
        for name in after.namelist():
            if name.endswith('.xml'): ET.fromstring(after.read(name))
        for notes_part in patches:
            body=body_text(after.read(notes_part))
            assert body.startswith('PRESENTATION SCRIPT\n')
            assert 'SCRIPT TRÌNH BÀY' not in body and 'GHI CHÚ DIỄN GIẢI' not in body
    validator=Path('C:/Users/jhiny/.codex/plugins/cache/openai-primary-runtime/presentations/26.1025.11240/skills/presentations/container_tools/inspect_presentation_package_integrity.py')
    result=subprocess.run([sys.executable,str(validator),str(candidate),'--fail-on-findings'],capture_output=True,text=True)
    (BUILD/'integrity.json').write_text(result.stdout,encoding='utf-8')
    assert result.returncode==0,result.stdout+result.stderr
    receipt={'english_note_bodies':38,'changed_parts':changed,
             'all_non_notes_parts_unchanged':True,'integrity':json.loads(result.stdout)}
    (BUILD/'verification.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    (BUILD/'script_EN.md').write_text('\n'.join(script),encoding='utf-8')
    print('Verified 38 English note bodies; every non-notes part is byte-for-byte unchanged.')
    if '--deliver' in sys.argv:
        import shutil
        final=OUT/'DeepNeoAG_Operating_Review_2026-10-26_v4_EN.pptx'
        assert not final.exists(),'Do not overwrite an existing delivery.'
        shutil.copy2(candidate,final)
        shutil.copy2(BUILD/'script_EN.md',OUT/'PRESENTATION_SCRIPT_v4_EN.md')
        # Keep the familiar script path current as well.
        shutil.copy2(BUILD/'script_EN.md',OUT/'SCRIPT_TRINH_BAY_v4.md')
        print('Delivered English script and PowerPoint with English speaker notes.')

if __name__=='__main__':main()
