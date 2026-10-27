$ErrorActionPreference='Stop'
$path=(Resolve-Path 'presentation\DeepNeoAG_Operating_Review_2026-10-26_v4.pptx').Path
$p=New-Object -ComObject PowerPoint.Application
$d=$null
try {
  $d=$p.Presentations.Open($path,$false,$false,$false)
  $notes=@{
    3="A protein can be broken into peptides. A tumor mutation may alter a peptide. A mutation-derived peptide is a candidate neoantigen and requires presentation and T-cell recognition to establish immunogenicity. A sequence score alone does not prove either.`r`rBiological context: Chuang et al. (2024), https://doi.org/10.1016/j.ijbiomac.2024.136252"
    27="The five answers summarize observations under the supplied dataset and protocol. The pooled representation comparison changes both features and classifier; the selected multi-window head also has more capacity than the single-window head. Differences between close test AP values remain uncertain.`r`rSource: docs/FULL_RESULTS_REPORT.md and results_full/tables/test_metrics.csv"
  }
  foreach($number in @(3,27)) {
    foreach($sh in $d.Slides.Item($number).NotesPage.Shapes) {
      if($sh.HasTextFrame -eq -1 -and $sh.TextFrame.HasText -eq -1) { $sh.TextFrame.TextRange.Text=$notes[$number]; break }
    }
  }
  # The old NCI illustration was removed from slide 3, so its image credit is no longer applicable.
  foreach($sh in $d.Slides.Item(33).Shapes) {
    if($sh.Name -eq 'TextBox 8') {
      $sh.TextFrame.TextRange.Text="Chuang et al. (2024), International Journal of Biological Macromolecules`rhttps://doi.org/10.1016/j.ijbiomac.2024.136252`rDataset and original project: https://github.com/B1607/DeepNeoAG`r`rESM models and implementation`rhttps://github.com/facebookresearch/esm`r`rEmpirical figures: complete supplied training run, results_full/`rNamed figure exports: docs/assets/full_results/`rOperating Review template: retained source deck, cloned and adapted"
    }
  }
  $d.Save()
  $d.Slides.Item(33).Export((Join-Path (Get-Location).Path '.codex-v4\v4-33.png'),'PNG',1280,720)
  'Notes and credits updated.'
} finally { if($null -ne $d){$d.Close()}; $p.Quit() }
