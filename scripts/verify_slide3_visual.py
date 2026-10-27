"""Keep the English v4 package intact except for slide 3 and its notes."""
import hashlib
import json
import posixpath
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'tmp/presentation_v4_visual'
OUT=ROOT/'presentation'
SOURCE=OUT/'DeepNeoAG_Operating_Review_2026-10-26_v4_EN.pptx'
NS={'p':'http://schemas.openxmlformats.org/presentationml/2006/main',
    'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
    'r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}

def parts(z):
    root=ET.fromstring(z.read('ppt/presentation.xml'))
    rels={r.get('Id'):r.get('Target') for r in ET.fromstring(z.read('ppt/_rels/presentation.xml.rels'))}
    return [(s.get('id'),posixpath.normpath('ppt/'+rels[s.get('{'+NS['r']+'}id')]))
            for s in root.find('p:sldIdLst',NS)]

def notes_part(z,slide):
    relpart=posixpath.dirname(slide)+'/_rels/'+posixpath.basename(slide)+'.rels'
    links=[r for r in ET.fromstring(z.read(relpart)) if r.get('Type','').endswith('/notesSlide')]
    assert len(links)==1
    return posixpath.normpath(posixpath.dirname(slide)+'/'+links[0].get('Target'))

def main():
    candidate=BUILD/'candidate.pptx'
    with ZipFile(SOURCE) as source,ZipFile(BUILD/'authored.pptx') as authored:
        old_parts=parts(source); new_parts=parts(authored)
        assert len(old_parts)==38 and [a for a,b in old_parts]==[a for a,b in new_parts]
        old_slide=old_parts[2][1]; new_slide=new_parts[2][1]
        old_notes=notes_part(source,old_slide); new_notes=notes_part(authored,new_slide)
        replacements={old_slide:authored.read(new_slide),old_notes:authored.read(new_notes)}
        diagram=ET.fromstring(replacements[old_slide])
        # Native objects only: the requested diagram remains editable.
        assert len(diagram.findall('.//p:pic',NS))==0
        assert len(diagram.findall('.//p:grpSp',NS))==1
        group=diagram.find('.//p:grpSp',NS)
        assert group.find('p:nvGrpSpPr/p:cNvPr',NS).get('name')=='NEOANTIGEN_PATHWAY_EDITABLE'
        assert len([g for g in group.findall('.//a:prstGeom',NS) if g.get('prst')=='ellipse'])==86
        assert len(group.findall('p:cxnSp',NS))>=54
        text='\n'.join(t.text or '' for t in diagram.findall('.//a:t',NS))
        for required in ('Normal protein','Mutated tumor protein','Normal peptide',
                         'Mutation-derived peptide','Candidate neoantigen','Possible T-cell recognition'):
            assert required in text
        assert not list(diagram.iterfind('.//*[@r:embed]',NS)), 'Unexpected external visual dependency'
        note_text='\n'.join(t.text or '' for t in ET.fromstring(replacements[old_notes]).findall('.//a:t',NS))
        assert 'PRESENTATION SCRIPT' in note_text
        assert 'Residue letters are illustrative' in note_text
        assert 'https://www.cancer.gov/' in note_text and 'https://clinicalinfo.hiv.gov/' in note_text
        with ZipFile(candidate,'w') as output:
            for info in source.infolist(): output.writestr(info,replacements.get(info.filename,source.read(info.filename)))
    with ZipFile(SOURCE) as source,ZipFile(candidate) as candidate_zip:
        changed=[p for p in source.namelist() if source.read(p)!=candidate_zip.read(p)]
        assert sorted(changed)==sorted(replacements)
        for part in candidate_zip.namelist():
            if part.endswith('.xml'): ET.fromstring(candidate_zip.read(part))
    fit=json.loads((BUILD/'fit.json').read_text(encoding='utf-8-sig'))
    assert not [f for f in fit if f['bound_width']>f['width']+2 or f['bound_height']>f['height']+2]
    from pypdf import PdfReader
    pdf=PdfReader(BUILD/'main.pdf')
    assert len(pdf.pages)==27
    pdftext=pdf.pages[2].extract_text()
    assert 'Mutation-derived peptide' in pdftext and 'Candidate neoantigen' in pdftext
    skill=Path('C:/Users/jhiny/.codex/plugins/cache/openai-primary-runtime/presentations/26.1025.11240/skills/presentations/container_tools')
    integrity=subprocess.run([sys.executable,str(skill/'inspect_presentation_package_integrity.py'),str(candidate),'--fail-on-findings'],capture_output=True,text=True)
    assert integrity.returncode==0,integrity.stdout+integrity.stderr
    (BUILD/'integrity.json').write_text(integrity.stdout,encoding='utf-8')
    layout=subprocess.run([sys.executable,str(skill/'inspect_presentation_layout_geometry.py'),str(candidate),
                           '--expected-slide-size-emu','12192000,6858000','--expected-slide-count','38'],capture_output=True,text=True)
    assert layout.returncode==0,layout.stderr
    (BUILD/'layout.json').write_text(layout.stdout,encoding='utf-8')
    receipt={'status':'pass','changed_parts':changed,'unchanged_other_slides':37,
             'diagram_native_shapes':len(group.findall('p:sp',NS)),'main_pdf_pages':27,
             'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
             'output_sha256':hashlib.sha256(candidate.read_bytes()).hexdigest()}
    (BUILD/'verification.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps(receipt))
    if '--deliver' in sys.argv:
        final=OUT/'DeepNeoAG_Operating_Review_2026-10-26_v4_EN_visual.pptx'
        assert not final.exists(),'Do not overwrite an existing delivered revision.'
        shutil.copy2(candidate,final)
        shutil.copy2(BUILD/'main.pdf',OUT/'DeepNeoAG_Operating_Review_2026-10-26_v4_EN_visual.pdf')
        shutil.copy2(BUILD/'slide3_after.png',OUT/'DeepNeoAG_Slide_03_visual.png')
        print('Delivered the updated English v4, PDF and slide 3 preview.')

if __name__=='__main__':main()
