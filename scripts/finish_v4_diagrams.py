"""Assemble three native diagrams and keep script-only notes on all slides."""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZipFile

from verify_slide3_visual import parts, notes_part, NS

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'tmp/presentation_v4_diagrams'
OUT=ROOT/'presentation'
SOURCE=OUT/'DeepNeoAG_Operating_Review_2026-10-26_v4_EN_visual.pptx'
CHANGED=(4,9,11)
GROUPS={4:'PREDICTION_THRESHOLD_EDITABLE',9:'EVALUATION_PROTOCOL_EDITABLE',11:'COMPOSITION_CLASSIFIER_EDITABLE'}

def note_body(xml):
    root=ET.fromstring(xml)
    for shape in root.findall('p:cSld/p:spTree/p:sp',NS):
        ph=shape.find('p:nvSpPr/p:nvPr/p:ph',NS)
        if ph is not None and ph.get('type')=='body':
            return '\n'.join(''.join(t.text or '' for t in p.findall('.//a:t',NS))
                             for p in shape.findall('p:txBody/a:p',NS))
    raise AssertionError('Missing notes body')

def script_only(xml,number):
    body=note_body(xml)
    assert body.startswith('PRESENTATION SCRIPT\n')
    body=body.removeprefix('PRESENTATION SCRIPT\n')
    body=re.split(r'\n(?:INTERPRETATION NOTES|SOURCE NOTES FROM V3|SOURCES|DIAGRAM NOTES)\n',body,maxsplit=1)[0].strip()
    if number==9:
        body=body.replace('We select configurations by mean cross-validation AP',
            'Logistic regression uses the full outer-training partition and has no early-stopping step. '
            'We select configurations by mean cross-validation AP',1)
    assert 'https://' not in body and 'PRESENTATION SCRIPT' not in body
    paragraph=('<a:p><a:pPr><a:buNone/></a:pPr><a:r><a:rPr lang="en-US"/><a:t>'
               +escape(body)+'</a:t></a:r></a:p>') if body else '<a:p/>'
    count=0
    def change_shape(match):
        nonlocal count
        block=match.group(0)
        if not re.search(r'<p:ph\b[^>]*\btype="body"',block):return block
        count+=1
        return re.sub(r'(<p:txBody>.*?<a:lstStyle\s*/>).*?(</p:txBody>)',
                      lambda m:m.group(1)+paragraph+m.group(2),block,count=1,flags=re.S)
    patched=re.sub(r'<p:sp\b[^>]*>.*?</p:sp>',change_shape,xml,flags=re.S)
    assert count==1 and note_body(patched)==body
    return patched.encode('utf-8'),body

def text(node):return '\n'.join(t.text or '' for t in node.findall('.//a:t',NS))

def metric_table(slide):
    for gf in slide.findall('p:cSld/p:spTree/p:graphicFrame',NS):
        name=gf.find('p:nvGraphicFramePr/p:cNvPr',NS).get('name')
        if name=='EDITABLE_TABLE_39_17':return gf
    raise AssertionError('Original evidence table missing')

def main():
    candidate=BUILD/'candidate.pptx'
    with ZipFile(SOURCE) as source,ZipFile(BUILD/'authored.pptx') as authored:
        old=parts(source); new=parts(authored)
        assert len(old)==38 and [i for i,p in old]==[i for i,p in new]
        replacements={}
        for number in CHANGED:
            old_part=old[number-1][1]; new_part=new[number-1][1]
            replacements[old_part]=authored.read(new_part)
            slide=ET.fromstring(replacements[old_part])
            group=slide.find('p:cSld/p:spTree/p:grpSp',NS)
            assert group is not None
            assert group.find('p:nvGrpSpPr/p:cNvPr',NS).get('name')==GROUPS[number]
            assert not slide.findall('.//p:pic',NS)
        before_table=metric_table(ET.fromstring(source.read(old[10][1])))
        after_table=metric_table(ET.fromstring(replacements[old[10][1]]))
        assert text(before_table)==text(after_table)
        assert ET.tostring(before_table.find('p:xfrm',NS))==ET.tostring(after_table.find('p:xfrm',NS))
        vector=ET.fromstring(replacements[old[10][1]]).findall('.//a:tbl',NS)
        assert len(vector)==2
        assert any(text(t)=='A\nC\nD\nL\n0.25\n0.25\n0.25\n0.25' for t in vector)
        scripts={}
        for number,(sid,part) in enumerate(old,1):
            np=notes_part(source,part)
            replacements[np],scripts[number]=script_only(source.read(np).decode('utf-8'),number)
        with ZipFile(candidate,'w') as output:
            for info in source.infolist():output.writestr(info,replacements.get(info.filename,source.read(info.filename)))
    with ZipFile(SOURCE) as source,ZipFile(candidate) as output:
        changed=[p for p in source.namelist() if source.read(p)!=output.read(p)]
        assert sorted(changed)==sorted(replacements)
        assert source.read(old[2][1])==output.read(old[2][1]),'Preserve the redesigned slide 3'
        for number,(sid,part) in enumerate(old,1):
            assert note_body(output.read(notes_part(output,part)))==scripts[number]
        for p in output.namelist():
            if p.endswith('.xml'):ET.fromstring(output.read(p))
    fit=json.loads((BUILD/'fit.json').read_text(encoding='utf-8-sig'))
    overflows=[f for f in fit if f['bound_width']>f['width']+2 or f['bound_height']>f['height']+2]
    assert not overflows,overflows
    skill=Path('C:/Users/jhiny/.codex/plugins/cache/openai-primary-runtime/presentations/26.1025.11240/skills/presentations/container_tools')
    for kind,args in [('integrity',['--fail-on-findings']),('layout',['--expected-slide-size-emu','12192000,6858000','--expected-slide-count','38','--require-native-table-slide','11'])]:
        tool=skill/('inspect_presentation_package_integrity.py' if kind=='integrity' else 'inspect_presentation_layout_geometry.py')
        run=subprocess.run([sys.executable,str(tool),str(candidate),*args],capture_output=True,text=True)
        assert run.returncode==0,run.stdout+run.stderr
        (BUILD/f'{kind}.json').write_text(run.stdout,encoding='utf-8')
    from pypdf import PdfReader
    pdf=PdfReader(BUILD/'main.pdf');assert len(pdf.pages)==27
    assert 'Highest OOF MCC' in pdf.pages[8].extract_text()
    assert '0.0714' in pdf.pages[10].extract_text()
    receipt={'status':'pass','redrawn_slides':list(CHANGED),'script_only_notes':38,
             'unchanged_other_slide_xml':35,'slide3_unchanged':True,'metrics_table_unchanged':True,
             'main_pdf_pages':27,'changed_parts':changed,'sha256':hashlib.sha256(candidate.read_bytes()).hexdigest()}
    (BUILD/'verification.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k!='changed_parts'}))
    if '--deliver' in sys.argv:
        final=OUT/'DeepNeoAG_Operating_Review_2026-10-26_v4_EN_visual_v2.pptx'
        assert not final.exists(),'Do not overwrite an existing delivery'
        shutil.copy2(candidate,final)
        shutil.copy2(BUILD/'main.pdf',OUT/'DeepNeoAG_Operating_Review_2026-10-26_v4_EN_visual_v2.pdf')
        for n in CHANGED:shutil.copy2(BUILD/f'after-{n:02d}.png',OUT/f'DeepNeoAG_Slide_{n:02d}_visual.png')
        # Keep the separate English speaking script consistent with the notes.
        for filename in ['PRESENTATION_SCRIPT_v4_EN.md','SCRIPT_TRINH_BAY_v4.md']:
            path=OUT/filename
            content=path.read_text(encoding='utf-8')
            content,count=re.subn(r'(### Slide 9 .*?\n\n).*?(?=\n\n### Slide 10 )',
                lambda m:m.group(1)+scripts[9],content,count=1,flags=re.S)
            assert count==1
            path.write_text(content,encoding='utf-8')
        print('Delivered the deck and PDF with redesigned slides 4, 9, 11 and script-only notes.')

if __name__=='__main__':main()
