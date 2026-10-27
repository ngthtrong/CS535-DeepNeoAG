$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$build=Join-Path $root 'tmp\presentation_v4_visual'
New-Item -ItemType Directory -Force $build | Out-Null
$source=Join-Path $root 'presentation\DeepNeoAG_Operating_Review_2026-10-26_v4_EN.pptx'
$candidate=Join-Path $build 'authored.pptx'
$ppt=New-Object -ComObject PowerPoint.Application
$deck=$null
$script:diagramNames=@()
function Color($hex) {
    return [Convert]::ToInt32($hex.Substring(4,2)+$hex.Substring(2,2)+$hex.Substring(0,2),16)
}
$navy=Color '133356'; $blue=Color '005CFF'; $gray=Color '72859B'
$pale=Color 'DDEAFB'; $mut=Color 'C45E00'; $orange=Color 'E58524'
$soft=Color 'C4CCD6'; $ink=Color '161616'; $white=Color 'FFFFFF'
function Track($sh,$name) {
    $sh.Name=$name
    $script:diagramNames+=$name
    return $sh
}
function Txt($name,$text,$x,$y,$w,$h,$size,$color,$bold=$false,$align=1) {
    $s=$slide.Shapes.AddTextbox(1,$x,$y,$w,$h)
    $s.TextFrame.MarginLeft=0; $s.TextFrame.MarginRight=0
    $s.TextFrame.MarginTop=0; $s.TextFrame.MarginBottom=0
    $s.TextFrame.WordWrap=-1
    $r=$s.TextFrame.TextRange; $r.Text=$text
    $r.Font.Name='Helvetica Neue'; $r.Font.Size=[single]$size
    $r.Font.Color.RGB=$color; $r.Font.Bold=$(if($bold){-1}else{0})
    $r.ParagraphFormat.Alignment=$align
    return Track $s $name
}
function Line($name,$x1,$y1,$x2,$y2,$color,$weight=1.5,$arrow=$false,$dash=$false) {
    $s=$slide.Shapes.AddLine($x1,$y1,$x2,$y2)
    $s.Line.ForeColor.RGB=$color; $s.Line.Weight=[single]$weight
    if($arrow){$s.Line.EndArrowheadStyle=2}
    if($dash){$s.Line.DashStyle=4}
    return Track $s $name
}
function Circle($name,$x,$y,$diameter,$fill,$stroke,$weight=1) {
    $s=$slide.Shapes.AddShape(9,$x,$y,$diameter,$diameter)
    $s.Fill.ForeColor.RGB=$fill; $s.Line.ForeColor.RGB=$stroke
    $s.Line.Weight=[single]$weight
    return Track $s $name
}
function Chain($name,$x,$y,$mutated) {
    $points=@(@(0,14),@(14,0),@(29,-8),@(44,-4),@(56,10),@(59,25),@(47,38),@(30,45),@(14,43),@(2,56),@(8,72),@(25,78),@(42,74),@(55,61),@(70,52),@(84,55),@(98,69),@(115,72),@(129,63),@(141,49),@(154,44),@(168,50),@(182,47),@(195,34))
    for($i=1;$i -lt $points.Count;$i++) {
        $c=$soft
        if($i -ge 10 -and $i -le 17){$c=$blue}
        [void](Line ($name+'_link_'+$i) ($x+$points[$i-1][0]) ($y+$points[$i-1][1]) ($x+$points[$i][0]) ($y+$points[$i][1]) $c 2)
    }
    for($i=0;$i -lt $points.Count;$i++) {
        $c=$soft; $d=8
        if($i -ge 9 -and $i -le 17){$c=$blue}
        if($mutated -and $i -eq 13){$c=$orange; $d=13}
        [void](Circle ($name+'_residue_'+$i) ($x+$points[$i][0]-$d/2) ($y+$points[$i][1]-$d/2) $d $c $white 0.6)
    }
}
function Peptide($name,$x,$y,$mutated) {
    $letters=@('A','C','D','E','F','G','H','I','K')
    if($mutated){$letters[4]='V'}
    [void](Line ($name+'_backbone') ($x+12) ($y+12) ($x+228) ($y+12) $gray 2)
    for($i=0;$i -lt 9;$i++) {
        $c=$pale; $stroke=$blue; $font=$navy
        if($mutated -and $i -eq 4){$c=$orange; $stroke=$orange; $font=$white}
        $s=Circle ($name+'_residue_'+$i) ($x+$i*27) $y 24 $c $stroke 1
        $s.TextFrame.MarginLeft=0; $s.TextFrame.MarginRight=0
        $s.TextFrame.MarginTop=0; $s.TextFrame.MarginBottom=0
        $s.TextFrame.VerticalAnchor=3
        $r=$s.TextFrame.TextRange; $r.Text=$letters[$i]
        $r.Font.Name='Helvetica Neue'; $r.Font.Size=12; $r.Font.Bold=-1
        $r.Font.Color.RGB=$font; $r.ParagraphFormat.Alignment=2
    }
}
function HLA($name,$x,$y,$mutated) {
    $vertices=@(@(0,0),@(14,0),@(23,14),@(68,14),@(77,0),@(91,0),@(80,29),@(56,36),@(56,52),@(35,52),@(35,36),@(11,29),@(0,0))
    $f=$slide.Shapes.BuildFreeform(1,$x,$y)
    for($i=1;$i -lt $vertices.Count;$i++){$f.AddNodes(0,0,($x+$vertices[$i][0]),($y+$vertices[$i][1]))}
    $s=$f.ConvertToShape(); $s.Fill.ForeColor.RGB=$pale
    $s.Line.ForeColor.RGB=$navy; $s.Line.Weight=[single]1.5
    [void](Track $s ($name+'_HLA'))
    for($i=0;$i -lt 9;$i++) {
        $c=$blue
        if($mutated -and $i -eq 4){$c=$orange}
        [void](Circle ($name+'_presented_residue_'+$i) ($x+17+$i*6) ($y+3) 5 $c $c 0.5)
    }
    [void](Line ($name+'_membrane') ($x-16) ($y+55) ($x+111) ($y+55) $gray 3)
    [void](Txt ($name+'_HLA_label') 'HLA' ($x+23) ($y+29) 45 18 12 $navy $true 2)
    $cell=Circle ($name+'_T_cell') 844 ($y-20) 60 $navy $navy 0.5
    $cell.TextFrame.MarginLeft=0; $cell.TextFrame.MarginRight=0
    $cell.TextFrame.MarginTop=0; $cell.TextFrame.MarginBottom=0
    $cell.TextFrame.WordWrap=0
    $cell.TextFrame.VerticalAnchor=3
    $cell.TextFrame.TextRange.Text='T cell'
    $cell.TextFrame.TextRange.Font.Name='Helvetica Neue'
    $cell.TextFrame.TextRange.Font.Size=14
    $cell.TextFrame.TextRange.Font.Color.RGB=$white
    $cell.TextFrame.TextRange.ParagraphFormat.Alignment=2
    [void](Line ($name+'_receptor_stem') 834 ($y+10) 844 ($y+10) $navy 2)
    [void](Line ($name+'_receptor') 834 ($y-1) 834 ($y+21) $navy 2)
    $contact=$soft
    if($mutated){$contact=$orange}
    [void](Line ($name+'_possible_contact') ($x+96) ($y+10) 826 ($y+10) $contact 1.7 $false $true)
}
try {
    $deck=$ppt.Presentations.Open($source,0,0,0)
    $deck.SaveAs($candidate,24)
    if($deck.Slides.Count -ne 38){throw 'Expected 38 slides.'}
    $slide=$deck.Slides.Item(3)
    $slide.Export((Join-Path $build 'slide3_before.png'),'PNG',1600,900)
    for($i=$slide.Shapes.Count;$i -ge 1;$i--) {
        $sh=$slide.Shapes.Item($i)
        if($sh.Name -like 'Slide Number Placeholder*'){continue}
        if($sh.Name -like 'Google Shape*'){$sh.TextFrame.TextRange.Text='Protein, peptide and neoantigen'}
        elseif($sh.Name -eq 'TextBox 7'){$sh.TextFrame.TextRange.Text='A tumor mutation can change a peptide and create a new immune target'}
        else{$sh.Delete()}
    }
    [void](Txt 'STAGE_PROTEIN' '1  PROTEIN' 31 143 220 26 16 $blue $true)
    [void](Txt 'STAGE_PEPTIDE' '2  PEPTIDE' 348 143 245 26 16 $blue $true)
    [void](Txt 'STAGE_IMMUNE' '3  IMMUNE RECOGNITION' 679 143 250 26 16 $blue $true)
    [void](Txt 'NORMAL_PROTEIN_LABEL' 'Normal protein' 31 183 220 30 19 $ink $true)
    [void](Txt 'NORMAL_PEPTIDE_LABEL' 'Normal peptide' 348 183 247 30 19 $ink $true)
    [void](Txt 'MUTANT_PROTEIN_LABEL' 'Mutated tumor protein' 31 341 240 30 19 $ink $true)
    [void](Txt 'MUTANT_PEPTIDE_LABEL' 'Mutation-derived peptide' 348 341 285 30 19 $ink $true)
    Chain 'NORMAL_PROTEIN' 46 219 $false
    Chain 'MUTANT_PROTEIN' 46 377 $true
    [void](Line 'PROCESSING_NORMAL' 269 251 325 251 $gray 2 $true)
    [void](Line 'PROCESSING_MUTANT' 269 409 325 409 $gray 2 $true)
    [void](Txt 'PROCESSING_NORMAL_LABEL' 'processing' 250 224 95 20 12 $gray $false 2)
    [void](Txt 'PROCESSING_MUTANT_LABEL' 'processing' 250 382 95 20 12 $gray $false 2)
    Peptide 'NORMAL_PEPTIDE' 348 239 $false
    Peptide 'MUTANT_PEPTIDE' 348 397 $true
    [void](Txt 'NORMAL_PEPTIDE_CAPTION' 'Unaltered sequence' 348 282 246 28 17 $gray $false 2)
    [void](Txt 'NEOANTIGEN_CAPTION' 'Candidate neoantigen' 348 441 246 28 18 $mut $true 2)
    [void](Line 'PRESENTATION_NORMAL' 612 251 658 251 $gray 2 $true)
    [void](Line 'PRESENTATION_MUTANT' 612 409 658 409 $gray 2 $true)
    [void](Txt 'PRESENTATION_NORMAL_LABEL' 'presentation' 590 224 91 20 11.5 $gray $false 2)
    [void](Txt 'PRESENTATION_MUTANT_LABEL' 'presentation' 590 382 91 20 11.5 $gray $false 2)
    HLA 'NORMAL_IMMUNE' 688 241 $false
    HLA 'MUTANT_IMMUNE' 688 399 $true
    [void](Txt 'NORMAL_OUTCOME' 'Usually tolerated as self' 679 309 250 28 17 $gray $false 2)
    [void](Txt 'MUTANT_OUTCOME' 'Possible T-cell recognition' 679 459 250 28 17 $mut $true 2)

    # Group the requested diagram so every residue, arrow and label remains editable.
    $group=$slide.Shapes.Range([object[]]$script:diagramNames).Group()
    $group.Name='NEOANTIGEN_PATHWAY_EDITABLE'
    foreach($sh in $slide.NotesPage.Shapes) {
        if($sh.Type -eq 14 -and $sh.PlaceholderFormat.Type -eq 2) {
            $old=$sh.TextFrame.TextRange.Text
            $sh.TextFrame.TextRange.Text=$old+"`r`rDIAGRAM NOTES`rThe diagram is schematic. Residue letters are illustrative, not measured peptide sequences. Orange marks the same altered residue in the protein, peptide and HLA-presented fragment. HLA presentation and T-cell recognition are conditional biological steps. The sequence classifier does not establish them. All diagram elements are editable PowerPoint objects."
        }
    }
    $deck.Save()
    $slide.Export((Join-Path $build 'slide3_after.png'),'PNG',1600,900)
    $deck.PrintOptions.Ranges.ClearAll()
    $range=$deck.PrintOptions.Ranges.Add(1,27)
    $deck.ExportAsFixedFormat((Join-Path $build 'main.pdf'),2,2,0,1,1,0,$range,4)
    $fit=@()
    function InspectShapes($shapes) {
        foreach($sh in $shapes) {
            if($sh.Type -eq 6){InspectShapes $sh.GroupItems}
            elseif($sh.HasTextFrame -eq -1 -and $sh.TextFrame.HasText -eq -1) {
                $script:fit += [pscustomobject]@{name=$sh.Name;x=$sh.Left;y=$sh.Top;width=$sh.Width;height=$sh.Height;text=$sh.TextFrame.TextRange.Text;bound_width=$sh.TextFrame.TextRange.BoundWidth;bound_height=$sh.TextFrame.TextRange.BoundHeight}
            }
        }
    }
    InspectShapes $slide.Shapes
    $fit | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 (Join-Path $build 'fit.json')
    Write-Output 'Created editable visual diagram on slide 3.'
} finally {
    if($null -ne $deck){$deck.Close()}
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($ppt)
}
