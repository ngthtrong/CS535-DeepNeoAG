# Visual Asset Guide and Image Preparation Plan

All presentation assets use English text, a white background, 16:9 composition, charcoal/navy text, teal method accents and restrained orange highlights. Use readable labels rather than tiny embedded paragraphs. Conceptual images must not invent data. Export high-resolution PNG; retain SVG for charts and editable diagrams when available.

## Current preparation status (26 October 2026)

**I / V16, C / V05 and D / V06 are complete and inserted in slides 12–14 of the v3 deck.** They were recomposed from the actual slide context and checked experiment settings, rather than generated from the old prompts. Each is an editable PowerPoint group, with standalone PNG and SVG copies in `docs/assets/generated/`. See [diagram notes](assets/generated/README.md).

The [prompt set](IMAGE_GENERATION_PROMPTS.md) retains historical plans for A–K. Other assets and slide numbers in the register below refer to the original outline unless explicitly updated. Existing numerical figures remain available.

Prompt D depicts selected ESM MCNN with 256 filters per branch and 1,280 concatenated features. Prompt I separately depicts one-hot MCNN with 64 filters per branch and 320 concatenated features.

## Asset register

| ID | Asset | Slides | Source or generation | Caption focus |
|---|---|---|---|---|
| V01 | Biological context | 2 | Prompt A (planned), or licensed reference below | Classification covers part of the biology |
| V02 | Five independent approaches | 1,4 | Prompt B (planned) | One question per approach |
| V03 | Published split and evaluation | 5,7 | Prompt E (planned) | Test separated from selection |
| V04 | Class counts and length histogram | 6 | Notebook `V04_dataset.png/svg` | Rare positives and length distribution |
| V05 | Frozen embeddings and B/L/D | 13 (v3) | Complete: `C_V05_embeddings.png/svg`, native PowerPoint group | Residue embeddings, padding and transpose |
| V06 | Selected pooled, CNN and MCNN | 14 (v3) | Complete: `D_V06_selected_architectures.png/svg`, native PowerPoint group | Three independent heads and selected settings |
| V07 | Research workflow | Appendix | Prompt F (planned, optional) | Research decisions |
| V08 | Learning histories | 13–14 | Notebook `V08_learning_curves.*` | Epoch behavior; losses have different scales |
| V09 | Controlled ablations | 12,15 | Notebook `V09_ablations.*` | One changed component per panel |
| V10 | 8M/35M quality and cost | 13,15 | Notebook `V10_encoder_comparison.*` and cost CSV | Larger encoder also changes D and capacity |
| V11 | CV comparison and fold/seed scatter | 14 | Notebook `V11_cv_comparison.*`, `V11_fold_seed.*` | Spread is descriptive, not a CI |
| V12 | Test curves and confusion matrices | 16 | Notebook `V12_test_curves.*`, `V12_confusion.*` | Locked choices and class imbalance |
| V13 | FP/FN table | 17 | `../outputs/full_analysis/representative_errors.csv` | Real IDs, scores and thresholds |
| V14 | Prediction endpoint | 3 | Prompt G (planned) | Score and locked threshold |
| V15 | Composition baseline | 8 | Prompt H (planned) | Order is lost |
| V16 | One-hot MCNN | 12 (v3) | Complete: `I_V16_onehot_mcnn.png/svg`, native PowerPoint group | Five parallel branches, 64 filters/branch, concat 320 |
| V17 | Experiment matrix | 12 | Prompt J (planned) | Staged search |
| V18 | Questions and lessons | 18 | Prompt K (planned) | Observed lessons and next experiment |

Use one focal figure per slide; move dense full-model panels into the appendix. Cropping a chart must not remove its denominator, threshold policy or uncertainty label. Do not use reduced-mode outputs for research slides.

## Reusable biological references

### Full-run asset update (25 October 2026)

Use the redrawn numerical figures from `assets/full_results/`, with captions from `assets/full_results/figure_index.csv`. All axes, titles and legends use descriptive model names. The full [slide map](FULL_RESULTS_SLIDE_MAP.md) connects each slide to actual settings and evidence. All eight redrawn PNG figures were inspected via `../outputs/full_analysis/named_figure_contact_sheet.png`. Historical figures and evidence remain in `../results_full/`.

For V06, any retained 64-filter design must be explicitly labelled **default architecture** and placed in the appendix. The selected ESM 8M + MCNN/ESM 35M + MCNN models have **256 filters per branch**, five branches and **1,280 concatenated features**. ESM 8M + CNN/ESM 35M + CNN use window 3 with 64 filters. For a selected-model diagram, change these labels consistently; do not reuse the default 320-feature concat label. This is a guide update, not a claim that new Gemini images were generated.

For V13, use the deterministically selected records in `../outputs/full_analysis/representative_errors.csv`. Show ESM 35M + MCNN threshold 0.632288 and real FP/FN labels. On the main test slide, use a readable complete PR panel and place the dense eight-model confusion grid in the appendix. Caption close rankings as uncertain; the paired differences are in `../outputs/full_analysis/paired_test_differences.csv`.

## Reusable biological references (existing source register)

### R1 — Neoantigen vaccine manufacturing illustration

- Landing page: https://www.cancer.gov/news-events/cancer-currents-blog/2025/neoantigen-vaccine-pancreatic-kidney-cancer
- Select the diagram in the middle of the page, whose caption begins “Neoantigens found on patients' tumor cells…”.
- Direct asset: https://www.cancer.gov/sites/www/files/styles/cgov_article/public/cgov_image/media_image/2025-03/neoantigen%20vaccine%20manufacture.jpg?itok=p3HFIlKP
- Page credit: **Adapted from Nature May 2023, https://doi.org/10.1038/s41586-023-06063-y , CC BY 4.0**.
- Attribution line: “Adapted from Nature (2023), doi:10.1038/s41586-023-06063-y, via National Cancer Institute, CC BY 4.0. [Describe any further changes.]”
- License: https://creativecommons.org/licenses/by/4.0/
- Downloaded copy: `assets/references/R1_neoantigen_vaccine.jpg`; provenance and checksum are in `assets/references/sources.json`.
- Do not select the page's opening iStock/Design Cells image; it has a different credit.
- Use as background context, not evidence for this classifier's performance.

### R2 — Antigen presentation

- Landing page: https://commons.wikimedia.org/wiki/File:Antigen_presentation.svg
- Download the original SVG from the file page.
- Downloaded copy: `assets/references/R2_antigen_presentation.svg`; checksum and source are in `assets/references/sources.json`.
- Creator: Sjef; subsequent file revisions are listed in the page history.
- Reuse option: **CC BY-SA 3.0**. https://creativecommons.org/licenses/by-sa/3.0/
- Attribution line: “Antigen presentation, Sjef and file-history contributors, Wikimedia Commons, CC BY-SA 3.0. [Describe changes.]”
- If adapting the figure, preserve applicable share-alike terms for that adapted asset. Record the downloaded revision/date in the slide asset notes.

The diagrams above are references for biological context. Custom model architecture and evaluation illustrations require project-specific prompts below rather than copying unrelated published network diagrams.

## Prompt library A-K

Use [the complete prompt pack](IMAGE_GENERATION_PROMPTS.md) for all future conceptual illustrations. It replaces the earlier A-F prompts and adds the endpoint, composition baseline, dedicated one-hot MCNN, experiment matrix and conclusion assets. Combine its shared style prompt with the individual prompt.

Planned outputs go under `docs/assets/generated/` (repository-relative). Exact filenames and pending status are listed in the prompt pack. This guide retains source credits and numerical asset references. Experimental plots use real data rather than text-to-image generation.

## Verification before inserting any illustration

- Check arrows, biological actors, exact counts and tensor dimensions.
- Keep every architecture parallel/sequential relationship correct.
- Distinguish model defaults from tuned configurations.
- Remove fabricated performance values or implied clinical claims.
- Keep proper source/license attribution for reused images.
- Label AI-generated conceptual illustrations and edit errors before use.
- Use code-generated curves, counts, matrices and tables for all experimental evidence.
