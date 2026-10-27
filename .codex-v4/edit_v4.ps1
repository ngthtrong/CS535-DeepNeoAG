$ErrorActionPreference = 'Stop'
$root = (Get-Location).Path
$source = Join-Path $root 'presentation\DeepNeoAG_Operating_Review_2026-10-26_v3.pptx'
$target = Join-Path $root 'presentation\DeepNeoAG_Operating_Review_2026-10-26_v4.pptx'
if (Test-Path $target) { throw "Output already exists: $target" }
$p = New-Object -ComObject PowerPoint.Application
$d = $null
try {
  $d = $p.Presentations.Open($source, $false, $false, $false)
  $d.SaveAs($target)

  # The printed slide numbers are stable references in the supplied deck.
  $toHide = @{}
  foreach ($s in $d.Slides) {
    foreach ($sh in $s.Shapes) {
      if ($sh.Name -like 'Slide Number Placeholder*' -and $sh.HasTextFrame -eq -1 -and $sh.TextFrame.HasText -eq -1) {
        $n = $sh.TextFrame.TextRange.Text.Trim()
        if ($n -in @('20','21','26','30','31')) { $toHide[$n] = $s.SlideID }
      }
    }
  }
  if ($toHide.Count -ne 5) { throw 'Could not identify all five requested slides' }

  $cover = $d.Slides.Item(1)
  foreach ($sh in $cover.Shapes) {
    if ($sh.HasTextFrame -eq -1 -and $sh.TextFrame.HasText -eq -1) {
      $t = $sh.TextFrame.TextRange.Text
      if ($t -like 'Computational Biology*') { $sh.TextFrame.TextRange.Text = "CS535`rNguyễn Thanh Trọng" }
      if ($t -like 'Complete experimental run*') { $sh.TextFrame.TextRange.Text = "Võ Trần Vũ Khoa`rMai Nhật Minh" }
    }
  }

  # Rewrite the introduction while preserving the inherited slide template.
  $intro = $d.Slides.Item(3)
  foreach ($sh in @($intro.Shapes | ForEach-Object { $_ })) {
    if ($sh.Name -like 'RESULT_IMAGE*' -or $sh.Name -eq 'TextBox 8') { $sh.Delete() }
    elseif ($sh.Name -like 'Google Shape*') { $sh.TextFrame.TextRange.Text = 'Protein, peptide and neoantigen' }
    elseif ($sh.Name -eq 'TextBox 7') { $sh.TextFrame.TextRange.Text = 'A tumor mutation can create a peptide the immune system recognizes' }
  }
  function AddText($slide, [string]$text, [single]$x, [single]$y, [single]$w, [single]$h, [single]$size, [int]$color, [bool]$bold=$false) {
    $shape = $slide.Shapes.AddTextbox(1,$x,$y,$w,$h)
    $shape.TextFrame.MarginLeft=0; $shape.TextFrame.MarginRight=0
    $shape.TextFrame.MarginTop=0; $shape.TextFrame.MarginBottom=0
    $shape.TextFrame.WordWrap=-1
    $tr=$shape.TextFrame.TextRange; $tr.Text=$text
    $tr.Font.Name='Helvetica Neue'; $tr.Font.Size=$size; $tr.Font.Color.RGB=$color
    if ($bold) { $tr.Font.Bold=-1 } else { $tr.Font.Bold=0 }
    return $shape
  }
  $blue = 0xE8640D # PowerPoint RGB is BGR; matches the template blue.
  $black = 0x161616
  $gray = 0x555555
  [void](AddText $intro 'PROTEIN' 31 159 260 30 17 $blue $true)
  [void](AddText $intro 'PEPTIDE' 330 159 260 30 17 $blue $true)
  [void](AddText $intro 'IMMUNE RECOGNITION' 630 159 299 30 17 $blue $true)
  [void](AddText $intro 'Normal protein' 31 212 260 31 19 $black $true)
  [void](AddText $intro 'Normal peptide' 330 212 260 31 19 $black $true)
  [void](AddText $intro 'Typically recognized as self' 630 212 299 52 18 $black)
  [void](AddText $intro 'Protein in healthy cells' 31 250 260 55 17 $gray)
  [void](AddText $intro 'A fragment of the normal protein' 330 250 260 55 17 $gray)
  [void](AddText $intro 'Mutated tumor protein' 31 323 260 31 19 $black $true)
  [void](AddText $intro 'Mutation-bearing peptide' 330 323 260 49 19 $black $true)
  [void](AddText $intro 'Candidate neoantigen' 630 323 299 31 19 $black $true)
  [void](AddText $intro 'A tumor mutation changes the protein' 31 365 260 68 17 $gray)
  [void](AddText $intro 'A fragment contains the altered sequence' 330 365 260 68 17 $gray)
  [void](AddText $intro 'A neoantigen can be recognized by T cells when presented by HLA' 630 365 299 80 17 $gray)

  # Five answers correspond in order to the five questions on slide 5.
  $conclusion=$d.Slides.Item(29)
  foreach($sh in @($conclusion.Shapes | ForEach-Object { $_ })) {
    if($sh.Name -like 'Google Shape*') { $sh.TextFrame.TextRange.Text='Answers to the five research questions' }
    elseif($sh.Name -eq 'TextBox 4') { $sh.TextFrame.TextRange.Text='Independent-test results under this dataset and protocol' }
    elseif($sh.Name -eq 'TextBox 6') { $sh.Delete() }
    elseif($sh.HasTable -eq -1) { $table=$sh.Table }
  }
  $rows = @(
    @('Question','Observed answer'),
    @('Are residue frequencies sufficient?','No. Composition + LR reaches test AP 0.0714.'),
    @('What can ordered learning achieve?','One-hot MCNN reaches AP 0.5408 with 28,801 trainable parameters.'),
    @('Do frozen representations add signal?','Pooled 8M reaches AP 0.4764. The baseline differs in representation and model.'),
    @('Does local extraction help?','8M CNN reaches AP 0.5122 vs 0.4764 for pooled 8M LR.'),
    @('Do multiple local scales help?','8M MCNN reaches AP 0.5437 vs 0.5122 for CNN, with more head capacity.')
  )
  for($r=1;$r -le 6;$r++) { for($c=1;$c -le 2;$c++) {
    $cell=$table.Cell($r,$c).Shape
    $cell.TextFrame.TextRange.Text=$rows[$r-1][$c-1]
    if($r -gt 1){$cell.TextFrame.TextRange.Font.Size=15}
  }}
  $table.Columns.Item(1).Width=300
  $table.Columns.Item(2).Width=598

  # Footnotes are separate text objects at the bottom of the source slides.
  foreach($s in $d.Slides) {
    $delete=@()
    foreach($sh in $s.Shapes) {
      if($sh.Name -notlike 'Slide Number Placeholder*' -and $sh.Top -ge 470 -and $sh.Height -le 40 -and $sh.HasTextFrame -eq -1 -and $sh.TextFrame.HasText -eq -1) { $delete += $sh }
    }
    foreach($sh in $delete){$sh.Delete()}
  }
  # Move the five original slides to the end, then hide them from slide show.
  foreach($n in @('20','21','26','30','31')) {
    $s=$d.Slides.FindBySlideID($toHide[$n]); $s.MoveTo($d.Slides.Count); $s.SlideShowTransition.Hidden=-1
  }
  # Keep visible page markers consistent with the revised order.
  for($i=1;$i -le $d.Slides.Count;$i++) {
    foreach($sh in $d.Slides.Item($i).Shapes) {
      if($sh.Name -like 'Slide Number Placeholder*' -and $sh.HasTextFrame -eq -1) { $sh.TextFrame.TextRange.Text=[string]$i }
    }
  }
  $d.Save()
  for($i=1;$i -le $d.Slides.Count;$i++) {
    $d.Slides.Item($i).Export((Join-Path $root ('.codex-v4\v4-{0:D2}.png' -f $i)), 'PNG', 1280, 720)
  }
  "Saved $target; total $($d.Slides.Count); hidden slides $($toHide.Count)"
} finally {
  if($null -ne $d){$d.Close()}
  $p.Quit()
}
