$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$build=Join-Path $root 'tmp\presentation_v4_diagrams'
$ppt=New-Object -ComObject PowerPoint.Application
$deck=$null
$script:names=@()
function Color($hex){return [Convert]::ToInt32($hex.Substring(4,2)+$hex.Substring(2,2)+$hex.Substring(0,2),16)}
$navy=Color '133356'; $blue=Color '005CFF'; $gray=Color '72859B'
$pale=Color 'DDEAFB'; $light=Color 'F3F6FA'; $white=Color 'FFFFFF'
$orange=Color 'E58524'; $mut=Color 'B75B00'; $teal=Color '008C95'; $violet=Color '7858AF'
$ink=Color '161616'; $soft=Color 'C4CCD6'
function Track($s,$name){$s.Name=$name; $script:names+=$name; return $s}
function Txt($name,$text,$x,$y,$w,$h,$size,$color,$bold=$false,$align=1){
    $s=$slide.Shapes.AddTextbox(1,$x,$y,$w,$h)
    $s.TextFrame.MarginLeft=0; $s.TextFrame.MarginRight=0
    $s.TextFrame.MarginTop=0; $s.TextFrame.MarginBottom=0; $s.TextFrame.WordWrap=-1
    $r=$s.TextFrame.TextRange; $r.Text=$text; $r.Font.Name='Helvetica Neue'
    $r.Font.Size=[single]$size; $r.Font.Color.RGB=$color
    $r.Font.Bold=$(if($bold){-1}else{0}); $r.ParagraphFormat.Alignment=$align
    return Track $s $name
}
function Line($name,$x1,$y1,$x2,$y2,$color,$weight=1.5,$arrow=$false,$dash=$false){
    $s=$slide.Shapes.AddLine($x1,$y1,$x2,$y2)
    $s.Line.ForeColor.RGB=$color; $s.Line.Weight=[single]$weight
    if($arrow){$s.Line.EndArrowheadStyle=2}; if($dash){$s.Line.DashStyle=4}
    return Track $s $name
}
function Shape($name,$kind,$x,$y,$w,$h,$fill,$stroke,$weight=1){
    $s=$slide.Shapes.AddShape($kind,$x,$y,$w,$h)
    $s.Fill.ForeColor.RGB=$fill; $s.Line.ForeColor.RGB=$stroke; $s.Line.Weight=[single]$weight
    return Track $s $name
}
function LabelShape($s,$text,$size,$color,$bold=$false){
    $s.TextFrame.MarginLeft=4; $s.TextFrame.MarginRight=4
    $s.TextFrame.MarginTop=2; $s.TextFrame.MarginBottom=2
    $s.TextFrame.VerticalAnchor=3; $s.TextFrame.WordWrap=-1
    $r=$s.TextFrame.TextRange; $r.Text=$text; $r.Font.Name='Helvetica Neue'
    $r.Font.Size=[single]$size; $r.Font.Color.RGB=$color
    $r.Font.Bold=$(if($bold){-1}else{0}); $r.ParagraphFormat.Alignment=2
}
function CleanSlide($n,$keepTable=$false){
    $script:slide=$deck.Slides.Item($n); $script:names=@()
    for($i=$slide.Shapes.Count;$i -ge 1;$i--){
        $sh=$slide.Shapes.Item($i)
        if($sh.Name -like 'Google Shape*' -or $sh.Name -like 'Slide Number Placeholder*' -or $sh.Name -eq 'TextBox 7'){continue}
        if($keepTable -and $sh.HasTable -eq -1){continue}
        $sh.Delete()
    }
}
function GroupDiagram($name){$g=$slide.Shapes.Range([object[]]$script:names).Group(); $g.Name=$name}
function AddResidueChain($name,$letters,$x,$y,$d,$step,$colors,$size){
    [void](Line ($name+'_backbone') ($x+$d/2) ($y+$d/2) ($x+($letters.Length-1)*$step+$d/2) ($y+$d/2) $gray 1.6)
    for($i=0;$i -lt $letters.Length;$i++){
        $c=$blue; if($null -ne $colors){$c=$colors[[string]$letters[$i]]}
        $s=Shape ($name+'_residue_'+$i) 9 ($x+$i*$step) $y $d $d $white $c 1.3
        LabelShape $s ([string]$letters[$i]) $size $c $true
        $s.TextFrame.MarginLeft=0; $s.TextFrame.MarginRight=0
        $s.TextFrame.MarginTop=0; $s.TextFrame.MarginBottom=0; $s.TextFrame.WordWrap=0
    }
}
try{
    $deck=$ppt.Presentations.Open((Join-Path $build 'source.pptx'),0,0,0)
    $deck.SaveAs((Join-Path $build 'authored.pptx'),24)

    # Slide 4: sequence input, model, score and an explicit threshold branch.
    CleanSlide 4
    [void](Txt 'INPUT_LABEL' 'Peptide sequence' 31 181 230 30 20 $ink $true)
    AddResidueChain 'INPUT_SEQUENCE' 'ACDEFGHIKLM' 35 250 18 20 $null 9.5
    [void](Line 'INPUT_TO_MODEL' 263 259 291 259 $gray 2 $true)
    $s=Shape 'SEQUENCE_CLASSIFIER' 1 306 217 167 84 $navy $navy
    LabelShape $s "Sequence`rclassifier" 22 $white
    [void](Line 'MODEL_TO_SCORE' 483 259 508 259 $gray 2 $true)
    [void](Txt 'SCORE_LABEL' 'Score' 518 181 74 28 20 $ink $true 2)
    $s=Shape 'SCORE_VALUE' 9 523 227 64 64 $pale $blue 1.5
    LabelShape $s 's' 28 $blue $true
    [void](Line 'SCORE_TO_THRESHOLD' 596 259 629 259 $gray 2 $true)
    $s=Shape 'LOCKED_THRESHOLD' 4 641 210 99 99 $white $orange 2
    LabelShape $s ([string]('s '+[char]0x2265+' t?')) 20 $navy $true
    $s.TextFrame.WordWrap=0
    $s.TextFrame.MarginLeft=0; $s.TextFrame.MarginRight=0
    [void](Line 'BRANCH_MAIN' 740 259 789 259 $gray 2)
    [void](Line 'BRANCH_UP' 789 259 789 209 $blue 2)
    [void](Line 'BRANCH_YES' 789 209 818 209 $blue 2 $true)
    [void](Line 'BRANCH_DOWN' 789 259 789 324 $gray 2)
    [void](Line 'BRANCH_NO' 789 324 818 324 $gray 2 $true)
    [void](Txt 'YES' 'YES' 745 176 49 22 14 $blue $true)
    [void](Txt 'POSITIVE_LABEL' "Label 1`rNeoantigen" 831 184 104 65 17 $blue $true)
    [void](Txt 'NO' 'NO' 747 334 43 21 14 $gray $true)
    [void](Txt 'OTHER_LABEL' "Label 0`rDataset other" 831 302 115 67 17 $gray)
    [void](Txt 'NO_HLA' 'No explicit HLA allele input' 31 321 280 29 17 $gray)
    [void](Line 'THRESHOLD_POINTER' 690 317 690 347 $orange 1.5)
    [void](Txt 'OOF_POLICY' "t selected from training OOF predictions`rand locked before testing" 587 359 324 69 17 $mut $false 2)
    GroupDiagram 'PREDICTION_THRESHOLD_EDITABLE'

    # Slide 9: a fold matrix, training-only choices, and a separate test input.
    CleanSlide 9
    [void](Txt 'TRAINING_BOUNDARY' 'Training only: 5,608 records' 31 140 650 30 19 $blue $true)
    [void](Line 'TRAINING_RULE' 31 176 929 176 $soft 1)
    [void](Txt 'CV_STAGE' '1  CROSS-VALIDATION' 31 190 270 25 16 $blue $true)
    [void](Txt 'SHARED_STRATIFIED_FOLDS' 'Shared stratified folds' 31 212 260 17 12 $gray)
    [void](Txt 'SELECT_STAGE' '2  SELECT AND LOCK' 371 190 256 25 16 $blue $true)
    [void](Txt 'REFIT_STAGE' '3  FINAL REFIT' 711 190 220 25 16 $blue $true)
    for($r=0;$r -lt 5;$r++){
        [void](Txt ('FOLD_'+$r) ('Fold '+($r+1)) 31 (228+$r*18) 47 16 11.5 $gray)
        for($c=0;$c -lt 5;$c++){
            $fill=$pale; if($r -eq $c){$fill=$orange}
            [void](Shape ('FOLD_'+$r+'_PART_'+$c) 1 (84+$c*34) (228+$r*18) 29 13 $fill $fill 0.3)
        }
    }
    [void](Shape 'TRAIN_LEGEND_SWATCH' 1 31 323 11 11 $pale $pale)
    [void](Txt 'TRAIN_LEGEND' 'Outer train' 48 319 94 21 13 $gray)
    [void](Shape 'VALIDATION_LEGEND_SWATCH' 1 153 323 11 11 $orange $orange)
    [void](Txt 'VALIDATION_LEGEND' 'Validation' 170 319 106 21 13 $gray)
    [void](Txt 'INNER_SPLIT_LABEL' 'Neural: split outer-training portion' 31 349 270 22 14 $ink)
    [void](Shape 'INNER_FIT' 1 31 375 196 14 $blue $blue 0.3)
    [void](Shape 'INNER_EARLY_STOP' 1 227 375 35 14 $teal $teal 0.3)
    [void](Txt 'INNER_FIT_LABEL' '85% fit' 31 394 96 18 12.5 $blue)
    [void](Txt 'INNER_STOP_LABEL' '15% early stop' 153 394 126 18 12.5 $teal)
    [void](Line 'CV_TO_SELECTION' 286 266 351 266 $gray 2 $true)
    [void](Txt 'OOF_SCORE_LABEL' 'OOF scores' 270 239 87 21 12.5 $gray $false 2)
    [void](Txt 'CONFIG_SELECTION_LABEL' 'Configuration' 371 229 237 26 19 $ink $true)
    [void](Txt 'CONFIG_SELECTION_VALUE' 'Highest mean CV AP' 371 258 237 24 17 $gray)
    [void](Txt 'THRESHOLD_SELECTION_LABEL' 'Threshold t' 371 296 237 26 19 $ink $true)
    [void](Txt 'THRESHOLD_SELECTION_VALUE' 'Highest OOF MCC' 371 325 237 24 17 $gray)
    [void](Shape 'LOCK_SHACKLE' 9 374 362 18 21 $white $orange 2)
    [void](Shape 'LOCK_BODY' 1 370 374 26 20 $orange $orange)
    [void](Txt 'LOCK_POLICY' 'Locked before testing' 408 371 229 28 17 $mut $true)
    [void](Line 'SELECTION_TO_REFIT' 624 266 691 266 $gray 2 $true)
    [void](Shape 'REFIT_NODE' 1 711 229 207 111 $pale $blue 1)
    [void](Txt 'REFIT_ALL_DATA' 'All 5,608' 723 246 183 28 22 $navy $true 2)
    [void](Txt 'REFIT_DATA_LABEL' 'training records' 723 277 183 25 18 $navy $false 2)
    [void](Txt 'REFIT_SEEDS' 'Neural seeds: 535, 536, 537' 718 310 194 21 12 $navy $false 2)
    [void](Line 'REFIT_TO_EVALUATION' 814 350 814 407 $gray 2 $true)
    [void](Txt 'LOCKED_MODEL_LABEL' "Locked`rmodels + t" 831 359 98 43 14.5 $navy)
    $s=Shape 'INDEPENDENT_TEST' 1 31 429 254 48 $light $gray 1
    LabelShape $s "Independent test`r1,404 records" 17 $navy
    [void](Line 'TEST_TO_EVALUATION' 296 453 692 453 $gray 2 $true)
    [void](Txt 'TEST_HOLDOUT_LABEL' 'Held out until final evaluation' 335 422 325 24 17 $gray $false 2)
    $s=Shape 'FINAL_EVALUATION' 1 711 419 207 58 $navy $navy
    LabelShape $s 'Final evaluation' 20 $white
    GroupDiagram 'EVALUATION_PROTOCOL_EDITABLE'

    # Slide 11: permutation examples merge into the same frequency vector.
    CleanSlide 11 $true
    [void](Txt 'SEQUENCES_STAGE' '1  SEQUENCES' 31 145 225 25 16 $blue $true)
    [void](Txt 'FREQUENCIES_STAGE' '2  FREQUENCIES' 330 145 250 25 16 $blue $true)
    [void](Txt 'CLASSIFIER_STAGE' '3  CLASSIFIER' 620 145 195 25 16 $blue $true)
    $colors=@{A=$blue;C=$teal;D=$orange;L=$violet}
    AddResidueChain 'SEQUENCE_ACDL' 'ACDL' 44 203 32 48 $colors 17
    AddResidueChain 'SEQUENCE_LDCA' 'LDCA' 44 277 32 48 $colors 17
    [void](Line 'FIRST_SEQUENCE_MERGE' 234 219 282 219 $gray 1.8)
    [void](Line 'SECOND_SEQUENCE_MERGE' 234 293 282 293 $gray 1.8)
    [void](Line 'MERGE_VERTICAL' 282 219 282 293 $gray 1.8)
    [void](Line 'SEQUENCE_TO_COMPOSITION' 282 253 317 253 $gray 1.8 $true)
    [void](Txt 'COUNT_LENGTH' "Count /`rlength" 240 173 83 40 14 $gray $false 2)
    $vector=$slide.Shapes.AddTable(2,4,330,213,224,70)
    $vector.Name='COMPOSITION_VECTOR_EDITABLE'
    $letters=@('A','C','D','L')
    for($r=1;$r -le 2;$r++){for($c=1;$c -le 4;$c++){
        $cell=$vector.Table.Cell($r,$c).Shape
        $cell.TextFrame.MarginLeft=0; $cell.TextFrame.MarginRight=0
        $cell.TextFrame.MarginTop=2; $cell.TextFrame.MarginBottom=2
        $cell.TextFrame.VerticalAnchor=3
        $tr=$cell.TextFrame.TextRange; $tr.Font.Name='Helvetica Neue'; $tr.Font.Size=18
        $tr.ParagraphFormat.Alignment=2; $tr.Font.Color.RGB=$navy
        if($r -eq 1){$tr.Text=$letters[$c-1];$tr.Font.Color.RGB=$colors[$letters[$c-1]];$tr.Font.Bold=-1;$cell.Fill.ForeColor.RGB=$pale}
        else{$tr.Text='0.25';$tr.Font.Bold=0;$cell.Fill.ForeColor.RGB=$white}
        for($b=1;$b -le 4;$b++){$border=$vector.Table.Cell($r,$c).Borders.Item($b);$border.ForeColor.RGB=$soft;$border.Weight=[single]0.5}
        $vector.Table.Cell($r,$c).Borders.Item(5).Visible=0
        $vector.Table.Cell($r,$c).Borders.Item(6).Visible=0
    }}
    [void](Txt 'VECTOR_DIMENSIONS' 'Same 20 frequencies' 330 297 244 26 18 $ink $true)
    [void](Txt 'VECTOR_ZEROS' '16 other residues: 0' 330 327 244 25 17 $gray)
    [void](Line 'VECTOR_TO_SCALER' 568 240 605 240 $gray 1.8 $true)
    $s=Shape 'STANDARD_SCALER' 1 620 215 171 51 $light $blue
    LabelShape $s 'StandardScaler' 18 $navy
    [void](Line 'SCALER_TO_LR' 705 269 705 279 $gray 1.8 $true)
    $s=Shape 'BALANCED_LR' 1 620 284 171 52 $navy $navy
    LabelShape $s "Balanced LR`rC = 1" 17 $white
    [void](Line 'LR_TO_SCORE' 802 310 839 310 $gray 1.8 $true)
    $s=Shape 'COMPOSITION_SCORE' 9 853 283 54 54 $pale $blue 1.3
    LabelShape $s 's' 25 $blue $true
    [void](Txt 'COMPOSITION_SCORE_LABEL' 'Score' 840 345 80 25 17 $navy $false 2)
    [void](Txt 'ORDER_LOSS' 'Order is lost' 31 340 240 29 20 $mut $true)
    GroupDiagram 'COMPOSITION_CLASSIFIER_EDITABLE'

    $deck.Save()
    foreach($n in @(4,9,11)){$deck.Slides.Item($n).Export((Join-Path $build ('after-{0:D2}.png' -f $n)),'PNG',1600,900)}
    $deck.PrintOptions.Ranges.ClearAll();$range=$deck.PrintOptions.Ranges.Add(1,27)
    $deck.ExportAsFixedFormat((Join-Path $build 'main.pdf'),2,2,0,1,1,0,$range,4)
    $script:fit=@()
    function InspectShapes($shapes,$n){
        foreach($sh in $shapes){
            if($sh.Type -eq 6){InspectShapes $sh.GroupItems $n}
            elseif($sh.HasTextFrame -eq -1 -and $sh.TextFrame.HasText -eq -1){$script:fit += [pscustomobject]@{slide=$n;name=$sh.Name;width=$sh.Width;height=$sh.Height;bound_width=$sh.TextFrame.TextRange.BoundWidth;bound_height=$sh.TextFrame.TextRange.BoundHeight}}
        }
    }
    foreach($n in @(4,9,11)){InspectShapes $deck.Slides.Item($n).Shapes $n}
    $fit | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 (Join-Path $build 'fit.json')
    Write-Output 'Redrew slides 4, 9 and 11 with editable native diagrams.'
}finally{if($null -ne $deck){$deck.Close()};[void][Runtime.InteropServices.Marshal]::ReleaseComObject($ppt)}
