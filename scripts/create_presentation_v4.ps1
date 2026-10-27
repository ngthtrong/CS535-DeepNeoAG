$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$build = Join-Path $root 'tmp\presentation_v4'
$source = Join-Path $root 'presentation\DeepNeoAG_Operating_Review_2026-10-26_v3.pptx'
$candidate = Join-Path $build 'candidate.pptx'
$data = Get-Content -Raw -Encoding UTF8 (Join-Path $build 'content.json') | ConvertFrom-Json
New-Item -ItemType Directory -Force (Join-Path $build 'rendered') | Out-Null

# The bundled artifact-tool package is absent in this Windows installation.
# PowerPoint's native file API preserves the source's charts, groups and masters.
$ppt = New-Object -ComObject PowerPoint.Application
$deck = $null
$map = @()
$removed = @()
$fit = @()
function AddText($slide, $name, [string]$text, $x, $y, $w, $h, $size, $color, $bold=$false) {
    $sh = $slide.Shapes.AddTextbox(1, $x, $y, $w, $h)
    $sh.Name = $name
    $sh.TextFrame.MarginLeft = 0; $sh.TextFrame.MarginRight = 0
    $sh.TextFrame.MarginTop = 0; $sh.TextFrame.MarginBottom = 0
    $sh.TextFrame.WordWrap = -1
    $tr = $sh.TextFrame.TextRange; $tr.Text = $text
    $tr.Font.Name = 'Helvetica Neue'; $tr.Font.Size = $size
    $tr.Font.Color.RGB = $color; $tr.Font.Bold = $(if ($bold) {-1} else {0})
    return $sh
}
function RemoveDiagramFootnotes($shapes, $original) {
    for($i=$shapes.Count; $i -ge 1; $i--) {
        $sh=$shapes.Item($i)
        if($sh.Type -eq 6) { RemoveDiagramFootnotes $sh.GroupItems $original }
        elseif($sh.HasTextFrame -eq -1 -and $sh.TextFrame.HasText -eq -1) {
            $t=$sh.TextFrame.TextRange.Text
            if($t -like 'Per branch:*' -or $t -like 'CNNs transpose to*') {
                $script:removed += [pscustomobject]@{original_slide=$original; name=$sh.Name; text=$t}
                $sh.Delete()
            }
        }
    }
}

try {
    $deck = $ppt.Presentations.Open($source, 0, 0, 0)
    $deck.SaveAs($candidate, 24)
    if ($deck.Slides.Count -ne 38) { throw 'Expected 38 source slides.' }
    $originalById = @{}
    $slideByOriginal = @{}
    foreach ($s in $deck.Slides) {
        $original = $s.SlideIndex
        foreach ($sh in $s.Shapes) {
            if ($sh.Name -like 'Slide Number Placeholder*' -and $sh.HasTextFrame -eq -1) {
                $original = [int]$sh.TextFrame.TextRange.Text.Trim()
            }
            elseif ($sh.Name -like 'Title*' -and $sh.HasTextFrame -eq -1 -and $sh.TextFrame.TextRange.Text.Trim() -eq 'Conclusion') {
                $original = 29
            }
        }
        $originalById[[string]$s.SlideID] = $original
        $slideByOriginal[[string]$original] = $s
    }
    if ($slideByOriginal.Count -ne 38) { throw 'Source slide-number mapping is ambiguous.' }

    $cover = $slideByOriginal['1']
    foreach ($sh in $cover.Shapes) {
        if ($sh.HasTextFrame -eq -1 -and $sh.TextFrame.HasText -eq -1) {
            $text = $sh.TextFrame.TextRange.Text
            if ($text -like 'Computational Biology*') {
                $sh.TextFrame.TextRange.Text = "CS535`rNguyễn Thanh Trọng"
                $sh.Width = 420
            } elseif ($text -like 'Complete experimental run*') {
                $sh.TextFrame.TextRange.Text = "Võ Trần Vũ Khoa`rMai Nhật Minh"
                $sh.Width = 429
            }
        }
    }

    # Remove separate footer/footnote objects, preserving page-number placeholders.
    foreach ($s in $deck.Slides) {
        $original = $originalById[[string]$s.SlideID]
        for ($i = $s.Shapes.Count; $i -ge 1; $i--) {
            $sh = $s.Shapes.Item($i)
            if ($sh.Name -like 'Slide Number Placeholder*') { continue }
            if ($sh.HasTextFrame -ne -1 -or $sh.TextFrame.HasText -ne -1) { continue }
            $isFootnote = ($sh.Top -ge 470 -and $sh.Height -le 40)
            $isFootnote = $isFootnote -or ($original -eq 26 -and $sh.Name -eq 'TextBox 6')
            $isFootnote = $isFootnote -or ($original -eq 1 -and $sh.Name -eq 'TextBox 5')
            if ($isFootnote) {
                $removed += [pscustomobject]@{original_slide=$original; name=$sh.Name; text=$sh.TextFrame.TextRange.Text}
                $sh.Delete()
            }
        }
        RemoveDiagramFootnotes $s.Shapes $original
    }

    $intro = $slideByOriginal['3']
    for ($i=$intro.Shapes.Count; $i -ge 1; $i--) {
        $sh=$intro.Shapes.Item($i)
        if ($sh.Name -like 'Slide Number Placeholder*') {continue}
        if ($sh.Name -like 'Google Shape*') {
            $sh.TextFrame.TextRange.Text='Protein, peptide and neoantigen'
        } elseif ($sh.Name -eq 'TextBox 7') {
            $sh.TextFrame.TextRange.Text='Normal and mutation-derived peptides differ in their source sequence'
        } else {$sh.Delete()}
    }
    $blue=0xFF5C00; $black=0x161616; $gray=0x555555
    [void](AddText $intro 'V4_PROTEIN_HEADING' 'PROTEIN' 31 145 270 27 17 $blue $true)
    [void](AddText $intro 'V4_PEPTIDE_HEADING' 'PEPTIDE' 340 145 270 27 17 $blue $true)
    [void](AddText $intro 'V4_NEOANTIGEN_HEADING' 'NEOANTIGEN' 649 145 280 27 17 $blue $true)
    [void](AddText $intro 'V4_PROTEIN_DEF' 'A chain of amino acids' 31 177 270 28 17 $gray)
    [void](AddText $intro 'V4_PEPTIDE_DEF' 'A short protein fragment' 340 177 270 28 17 $gray)
    [void](AddText $intro 'V4_NEOANTIGEN_DEF' 'A new tumor-specific antigen' 649 177 280 43 17 $gray)
    [void](AddText $intro 'V4_NORMAL_PROTEIN' 'Normal protein' 31 245 270 29 20 $black $true)
    [void](AddText $intro 'V4_NORMAL_PEPTIDE' 'Normal peptide' 340 245 270 29 20 $black $true)
    [void](AddText $intro 'V4_NORMAL_IMMUNE' 'Usually tolerated as self' 649 245 280 48 20 $black)
    [void](AddText $intro 'V4_NORMAL_ORIGIN' 'Present in healthy cells' 31 280 270 28 17 $gray)
    [void](AddText $intro 'V4_NORMAL_FRAGMENT' 'Unaltered source sequence' 340 280 270 28 17 $gray)
    [void](AddText $intro 'V4_TUMOR_PROTEIN' 'Mutated tumor protein' 31 340 270 30 20 $black $true)
    [void](AddText $intro 'V4_TUMOR_PEPTIDE' 'Mutation-derived peptide' 340 340 285 30 20 $black $true)
    [void](AddText $intro 'V4_CANDIDATE' 'Candidate neoantigen' 649 340 280 30 20 $blue $true)
    [void](AddText $intro 'V4_TUMOR_ORIGIN' 'Mutation changes the sequence' 31 377 270 45 17 $gray)
    [void](AddText $intro 'V4_TUMOR_FRAGMENT' 'Fragment contains the alteration' 340 377 280 45 17 $gray)
    [void](AddText $intro 'V4_IMMUNE_CONTEXT' 'HLA presents the peptide. T cells may recognize the altered sequence.' 31 440 898 31 19 $blue)

    $conclusion=$slideByOriginal['32']
    $tableShape=$null
    for ($i=$conclusion.Shapes.Count; $i -ge 1; $i--) {
        $sh=$conclusion.Shapes.Item($i)
        if ($sh.Name -like 'Google Shape*') {$sh.TextFrame.TextRange.Text='Answers to the five research questions'}
        elseif ($sh.Name -eq 'TextBox 4') {$sh.TextFrame.TextRange.Text='Five questions from the introduction, answered with independent-test evidence'}
        elseif ($sh.HasTable -eq -1) {$tableShape=$sh}
        elseif ($sh.Name -eq 'TextBox 6') {$sh.Delete()}
    }
    if ($null -eq $tableShape) {throw 'Conclusion table missing.'}
    $table=$tableShape.Table
    $tableShape.Left=31; $tableShape.Top=143
    $table.Columns.Item(1).Width=368; $table.Columns.Item(2).Width=530
    $table.Rows.Item(1).Height=36
    for($r=2;$r -le 6;$r++) {$table.Rows.Item($r).Height=59}
    for($r=1;$r -le 6;$r++) {for($c=1;$c -le 2;$c++) {
        $cell=$table.Cell($r,$c).Shape
        $cell.TextFrame.TextRange.Text=[string]$data.conclusion[$r-1][$c-1]
        $cell.TextFrame.TextRange.Font.Size=17
        $cell.TextFrame.MarginLeft=0; $cell.TextFrame.MarginRight=12
        $cell.TextFrame.MarginTop=5; $cell.TextFrame.MarginBottom=3
        $cell.TextFrame.VerticalAnchor=3
        if($r -gt 1){$cell.TextFrame.TextRange.Font.Bold=0}
    }}

    # Source numbers are resolved before moving; these are the user's five slides.
    foreach($n in @('20','21','26','30','31')) {
        $s=$slideByOriginal[$n]
        $s.MoveTo($deck.Slides.Count)
        $s.SlideShowTransition.Hidden=-1
    }
    $credits=$slideByOriginal['38']
    foreach($sh in $credits.Shapes) {
        if($sh.Name -eq 'TextBox 8') {
            $sh.TextFrame.TextRange.Text="Chuang et al. (2024), International Journal of Biological Macromolecules`rhttps://doi.org/10.1016/j.ijbiomac.2024.136252`rDataset and original project: https://github.com/B1607/DeepNeoAG`r`rESM models and implementation: https://github.com/facebookresearch/esm`r`rBiological definitions: National Cancer Institute and NIH`rhttps://www.cancer.gov/publications/dictionaries/cancer-terms/def/neoantigen`rhttps://clinicalinfo.hiv.gov/en/glossary/human-leukocyte-antigen-complex`r`rEmpirical figures: supplied full training run, results_full/`rOperating Review template: retained and adapted"
            $sh.TextFrame.TextRange.Font.Size=15
        }
    }

    # Replace the body notes, preserving the original notes separately for sources.
    foreach($s in $deck.Slides) {
        $original=$originalById[[string]$s.SlideID]
        $script=[string]$data.script.PSObject.Properties[[string]$original].Value
        $oldNotes=''
        foreach($sh in $s.NotesPage.Shapes) {
            if($sh.Type -eq 14 -and $sh.PlaceholderFormat.Type -eq 2) {
                if($sh.HasTextFrame -eq -1){$oldNotes=$sh.TextFrame.TextRange.Text}
                $notes="SCRIPT TRÌNH BÀY`r$script"
                $oldFootnotes=@($removed | Where-Object original_slide -eq $original)
                if($oldFootnotes.Count -gt 0) {
                    $notes += "`r`rGHI CHÚ DIỄN GIẢI`r" + (($oldFootnotes | ForEach-Object text) -join "`r")
                }
                if($original -eq 3){$notes += "`r`rSOURCES`r" + $data.bio_sources}
                elseif($oldNotes.Trim()) {$notes += "`r`rSOURCE NOTES FROM V3`r" + $oldNotes}
                $sh.TextFrame.TextRange.Text=$notes
            }
        }
        $title=''
        foreach($sh in $s.Shapes) {
            if($sh.Name -like 'Slide Number Placeholder*') {$sh.TextFrame.TextRange.Text=[string]$s.SlideIndex}
            elseif(($sh.Name -like 'Google Shape*' -or $sh.Name -like 'Title*') -and $sh.HasTextFrame -eq -1) {$title=$sh.TextFrame.TextRange.Text -replace '[\r\v]',' '}
        }
        $map += [pscustomobject]@{slide=$s.SlideIndex; source_number=$original; slide_id=$s.SlideID; title=$title; hidden=($s.SlideShowTransition.Hidden -eq -1); script=$script}
    }
    # Default slide show ends at the conclusion. Existing appendices remain accessible.
    $deck.SlideShowSettings.RangeType=2
    $deck.SlideShowSettings.StartingSlide=1
    $deck.SlideShowSettings.EndingSlide=27
    $deck.SlideShowSettings.ShowPresenterView=-1

    # Rebuild navigation sections after the move.
    $sections=$deck.SectionProperties
    while($sections.Count -gt 1){$sections.Delete($sections.Count,$false)}
    if($sections.Count -eq 1){$sections.Rename(1,'Cover')}
    else{[void]$sections.AddBeforeSlide(1,'Cover')}
    [void]$sections.AddBeforeSlide(2,'Introduction')
    [void]$sections.AddBeforeSlide(6,'Methodology')
    [void]$sections.AddBeforeSlide(17,'Results')
    [void]$sections.AddBeforeSlide(26,'Conclusion')
    [void]$sections.AddBeforeSlide(28,'Appendix')
    [void]$sections.AddBeforeSlide(34,'Removed from main presentation')

    $deck.Save()
    foreach($s in $deck.Slides) {
        $s.Export((Join-Path $build ('rendered\slide-{0:D2}.png' -f $s.SlideIndex)),'PNG',1600,900)
        foreach($sh in $s.Shapes) {
            if($sh.HasTextFrame -eq -1 -and $sh.TextFrame.HasText -eq -1) {
                $fit += [pscustomobject]@{slide=$s.SlideIndex; name=$sh.Name; height=$sh.Height; bound_height=$sh.TextFrame.TextRange.BoundHeight; width=$sh.Width; bound_width=$sh.TextFrame.TextRange.BoundWidth}
            }
            if($sh.HasTable -eq -1){for($r=1;$r -le $sh.Table.Rows.Count;$r++){for($c=1;$c -le $sh.Table.Columns.Count;$c++){
                $cell=$sh.Table.Cell($r,$c).Shape
                $fit += [pscustomobject]@{slide=$s.SlideIndex; name="table r$r c$c"; height=$cell.Height; bound_height=$cell.TextFrame.TextRange.BoundHeight; width=$cell.Width; bound_width=$cell.TextFrame.TextRange.BoundWidth}
            }}}
        }
    }
    # Export a reading copy of the main presentation only.
    $deck.PrintOptions.Ranges.ClearAll()
    $range=$deck.PrintOptions.Ranges.Add(1,27)
    $deck.ExportAsFixedFormat((Join-Path $build 'main.pdf'),2,2,0,1,1,0,$range,4)
    $map | ConvertTo-Json -Depth 5 | Set-Content -Encoding UTF8 (Join-Path $build 'slide_map.json')
    $removed | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 (Join-Path $build 'removed_footnotes.json')
    $fit | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 (Join-Path $build 'text_fit.json')
    Write-Output "Created candidate: 38 total slides, 27 main slides, 5 hidden slides."
} finally {
    if($null -ne $deck){$deck.Close()}
    # Keep the user's existing PowerPoint process and other presentations intact.
    [void][Runtime.InteropServices.Marshal]::ReleaseComObject($ppt)
}
