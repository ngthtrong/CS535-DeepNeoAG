# DeepNeoAG: Learning Through Controlled Experiments

**Audience:** a computational biology course class. **Duration:** 18 minutes, 18 main slides. **Language:** English. **Format:** 16:9. The central narrative is question → controlled change → observation → lesson. Updated from the complete 258-fit run on 25 October 2026; see [full report](FULL_RESULTS_REPORT.md) and [slide map](FULL_RESULTS_SLIDE_MAP.md). Numerical evidence reconciles, with an execution-source provenance caveat documented in the report.

## Image preparation and insertion plan (25 October 2026)

**Status: prompts prepared; new images not generated or inserted.** Use the [11 copy-ready prompts A-K](IMAGE_GENERATION_PROMPTS.md) for conceptual illustrations. Planned files under `docs/assets/generated/` do not exist yet. Keep English text, 16:9 format and the existing 18-slide / 18-minute timing.

| Slide | Main visual | Later placement |
|---|---|---|
| 1 | B / V02, five short labels | Editable labels under the title; full map on slide 4 |
| 2 | A / V01 biological context | Lower two-thirds, with context caption |
| 3 | G / V14 prediction endpoint | Central horizontal diagram |
| 4 | B / V02 independent approaches | Five readable rows in main content area |
| 5 | E / V03 top split strip | Upper half; editable counts table below |
| 6 | Existing V04 dataset plot | Preserve counts and length axes |
| 7 | E / V03 complete evaluation flow | Main content area; separate test lane |
| 8 | H / V15 composition baseline | Lower half; short evidence callout above |
| 9 | I / V16 one-hot MCNN | 64 filters per branch; concat 320 |
| 10 | C / V05 embeddings | Three panels; preserve tensor labels |
| 11 | D / V06 selected architectures | Three rows; ESM MCNN: 256 filters/branch, concat 1280 |
| 12 | J / V17 experiment matrix | Central table with staged-search caption |
| 13 | Existing V08 learning history | One readable example plus editable cost table |
| 14 | Existing V11 CV comparison | Main plot; fold/seed inset only if readable |
| 15 | Existing V09 ablations | Two or three contrasts; complete V09/V10 in appendix |
| 16 | Existing V12 complete PR panel | Locked metrics as editable text; confusion grid in appendix |
| 17 | V13 real error table | Left two-thirds; limitations at right |
| 18 | K / V18 questions and lessons | Five short rows and one next experiment |
| Appendix | F / V07, full result figures and credits | Workflow optional; full evidence and provenance retained |

Use one focal visual per slide. Numerical figures come from `assets/full_results/`; V13 comes from `../outputs/full_analysis/representative_errors.csv`. Prompts, planned filenames, draft captions, priorities and later review checks are in the prompt pack. Preserve the source and uncertainty captions of empirical figures.

## Slide 1 — DeepNeoAG: Learning Through Controlled Experiments (0:30)

**Message:** this project investigates how representation and architecture affect peptide classification.

- Sequence-based classification of neoantigen-like versus other peptides.
- Five core approaches, followed by controlled ablations.
- Emphasis on reasoning, fair evaluation and evidence.

**Visual:** Prompt B / V02 adapted into five short editable labels below the title; use the full map on slide 4. **Evidence:** experiment registry. **Speaker notes:** Introduce the task and explain that each model exists to answer a different question. Success means an explainable, reproducible investigation; a larger model does not need to win. Preview data, methods, experiments and lessons.

## Slide 2 — Why Predict Neoantigen-like Peptides? (1:00)

**Message:** peptide recognition motivates the task, while sequence prediction covers only one part of the biology.

- Tumor-specific mutations can alter peptide sequences.
- Peptide presentation and T-cell recognition depend on biological context.
- Sequence-based models can help prioritize candidates for further investigation.

**Visual:** Prompt A / V01 biological context in the lower two-thirds. **Evidence:** biological references in the bibliography. **Speaker notes:** Walk from altered protein to peptide, MHC presentation and T-cell recognition. Point out where the computational classifier sits. Do not imply that a high probability proves presentation, immune response or vaccine effectiveness.

## Slide 3 — Defining the Prediction Problem (0:50)

**Message:** the endpoint must be defined before choosing a model.

- Input: an amino-acid sequence, with no explicit HLA allele input.
- Output: a score and a binary decision at a specified threshold.
- Label 1: neoantigen; label 0: the dataset's other-peptide group.

**Visual:** Prompt G / V14 sequence, score and locked-threshold decision diagram. **Evidence:** dataset README and label counts. **Speaker notes:** Use one generic FASTA example. Explain that the zero class reflects the data source's definition and is not a universal proof of biological non-immunogenicity. Distinguish a probability-like score, a ranking and a binary decision.

## Slide 4 — Five Questions Behind the Model Sequence (1:00)

**Message:** increasing model complexity should answer an explicit question.

- Composition: are residue frequencies sufficient?
- One-hot MCNN: what can ordered pattern learning achieve?
- ESM pooled/CNN/MCNN: what do pretraining, local extraction and multiple scales contribute?

**Visual:** Prompt B / V02 with one independent model and research question per row. **Evidence:** protocol model table. **Speaker notes:** Explain that these are independently trained models rather than a chain of predictions. Mention that Composition + LR→One-hot + MCNN changes both representation and classifier; later matched comparisons isolate components more closely.

## Slide 5 — Dataset Provenance and Published Splits (1:00)

**Message:** preserve the supplied independent test rather than redistributing all records.

- Total: 7,012 peptides, with 302 positives and 6,710 others.
- Training: 5,608 records; independent test: 1,404 records.
- Record-level provenance and exact source identifiers are retained.

**Visual:** Top split strip from Prompt E / V03 plus a compact editable counts table. **Evidence:** `tables/dataset_counts.csv`, `data_audit/audit.json`. **Speaker notes:** Describe the source and what the labels mean. Introduce the held-out test boundary. Similarity filtering is reported by the source; explain that the project checks exact duplicates but does not independently reconstruct that filtering procedure.

## Slide 6 — Understanding the Data Before Training (1:10)

**Message:** the data determine what a meaningful evaluation must measure.

- Positives are rare: approximately one positive per 22 others.
- Length distributions affect padding and convolution windows.
- Check labels, duplicates and boundary cases before training.

**Visual:** V04 class bars and length histogram. **Evidence:** `tables/length_counts.csv`, audit JSON. **Speaker notes:** Explain why an all-other classifier has high accuracy. Show the 35-residue boundary case and the choice to preserve the sample. Do not assign MHC classes from length. Use this slide to show an actual data-driven implementation decision.

## Slide 7 — Designing a Fair Evaluation (1:20)

**Message:** different decisions require different partitions.

- Shared stratified five-fold training CV for comparable experiments.
- Inner early-stopping subsets; outer-fold predictions for selection.
- Lock configurations and OOF thresholds before independent testing.

**Visual:** Prompt E / V03 complete evaluation diagram; keep the test lane separate and visible. **Evidence:** `fold_assignments.csv`, locked selection JSON. **Speaker notes:** Trace one fold from fitting to early stopping to outer validation. Explain that choosing settings from CV makes those selection scores optimistic. The independent test answers the final generalization question. Seed repetitions examine initialization variability, not new independent datasets.

## Slide 8 — Baseline 1: Amino-acid Composition (0:45)

**Message:** a simple model establishes what composition alone can explain.

- Convert the sequence into 20 normalized residue frequencies.
- Standardize features within training partitions.
- Fit balanced Logistic Regression with controlled regularization.

**Visual:** Prompt H / V15 composition baseline: ACDL and LDCA share one frequency vector before LR. **Evidence:** Composition + LR CV rows. **Speaker notes:** Compare ACDL and LDCA: composition is identical. The model cannot see order. C=1 is selected: mean CV AP is 0.1287; test AP is 0.0714 and MCC 0.0515 at OOF threshold 0.6508. Composition contains some signal but is insufficient here; test prevalence is 0.0434.

## Slide 9 — Baseline 2: One-hot MCNN (0:55)

**Message:** one-hot preserves position so the classifier can learn local patterns from labels.

- Each residue has a 20-dimensional identity vector.
- Parallel windows scan ordered segments.
- Padding is excluded before maximum pooling.

**Visual:** Prompt I / V16 dedicated one-hot MCNN: 64 filters per branch and 320 concatenated features. **Evidence:** One-hot + MCNN configuration and fixed-default comparison. **Speaker notes:** Explain one filter's scan and how max pooling retains its strongest valid response. This model has no pretrained protein encoder. Improvement over composition is suggestive, but the comparison changes architecture too.

**Full-run evidence for slide 9:** One-hot + MCNN CV AP 0.4943; test AP 0.5408, MCC 0.5495, precision 0.5362 and recall 0.6066 at threshold 0.5125. With 28,801 trainable parameters and no encoder, it remains a strong efficiency reference.

## Slide 10 — From Peptides to Contextual Embeddings (1:10)

**Message:** a frozen encoder gives each residue a context-dependent representation.

- B: peptides per batch; L: padded residue positions; D: features per position.
- ESM-2 8M produces D=320; 35M produces D=480.
- Remove special tokens and retain real-residue lengths.

**Visual:** Prompt C / V05 tensor diagram, including real residues, padding and transpose. **Evidence:** feature manifests and observed tensor shapes. **Speaker notes:** Illustrate that identical residue letters may receive different contextual vectors. Separate encoder parameters from downstream trainable parameters. Explain the transpose from `[B,L,D]` to `[B,D,L]` without implying that it changes information.

## Slide 11 — Pooling, Single-window CNN and MCNN (1:10)

**Message:** the same residue embeddings can be used in three different ways.

- Mean pooling summarizes contextual residues into a sequence vector.
- A single-window CNN learns one local scale.
- MCNN combines several local scales before classification.

**Visual:** Prompt D / V06 selected pooled, single-window and multi-window architectures. Selected ESM MCNN uses 256 filters per branch and 1,280 concatenated features. **Evidence:** ESM 8M + pooled LR–ESM 8M + MCNN definitions. **Speaker notes:** Pooling contextual vectors does not erase all order information because the encoder already used context. Explain that MCNN adds capacity as well as window diversity. Do not call a filter a biological motif without supporting analysis.

**Full-run evidence for slide 11:** Selected 8M pooled/single/multi CV AP is 0.3976/0.4868/0.5142; test AP is 0.4764/0.5122/0.5437. Single selects window 3 and 64 filters. Selected multi uses 256 filters per branch and concatenates 1,280 features; use these selected values in Prompt D. Retain any default 64-filter / 320-feature diagram only in the appendix, explicitly labelled default.

## Slide 12 — Our Controlled Experiment Matrix (1:10)

**Message:** change one component at a time to understand its effect.

- Window size: 2,3,4,5,8; filters: 32,64,128,256.
- Class-weighted versus unweighted loss at a matched architecture.
- Frozen encoder 8M versus 35M with transferred CNN configurations.

**Visual:** Prompt J / V17 compact experiment matrix; emphasize the controlled variable and staged search. **Evidence:** experiment registry and protocol. **Speaker notes:** State the shared optimizer, epoch budget and folds. Explain why this is not a full factorial grid. State that 35M also changes embedding dimension and downstream parameter count, which must accompany performance comparisons.

**Full-run evidence for slide 12:** The full run contains 22 configurations: 45 LR CV fits, 195 neural CV fits and 18 final refits, totaling 258. This is a staged search, not a full factorial grid.

## Slide 13 — Tracking Learning and Computational Cost (0:55)

**Message:** a final score alone does not describe how a model learned.

- Track training loss and early-stopping AP by epoch.
- Record best epoch, training time and parameter count.
- Separate encoder extraction cost from downstream fitting cost.

**Visual:** V08 example history and a compact resource table. **Evidence:** epoch histories and encoder costs. **Speaker notes:** Explain the observed training behavior only after seeing full histories. Raw weighted and unweighted losses have different scales; compare AP for cross-loss quality. Show how these records support decisions rather than discuss storage or execution infrastructure.

**Full-run evidence for slide 13:** Representative losses decrease while early-stop AP plateaus or fluctuates. Refit epochs One-hot + MCNN/ESM 8M + CNN/ESM 8M + MCNN/ESM 35M + CNN/ESM 35M + MCNN are 23/13/16/10/14. Extraction is 9.53 s (8M) versus 13.21 s (35M); mean downstream CV fit times are 10.26 s (One-hot + MCNN), 11.50 s (ESM 8M + MCNN), 13.52 s (ESM 35M + MCNN) on the recorded Tesla T4. Timings depend on session state and stopping epoch; they are not deployment latency estimates.

## Slide 14 — What We Observed Across Folds and Seeds (1:10)

**Message:** stability matters alongside mean performance.

- Compare the same validation folds across methods.
- Examine initialization variability and difficult folds.
- Report descriptive spread with the mean, without calling it a confidence interval.

**Visual:** V11 CV mean/SD and fold-seed points. **Evidence:** selected CV runs. **Speaker notes:** One-hot + MCNN CV AP is 0.4943 with descriptive SD 0.1032; ESM 8M + MCNN is 0.5142 with SD 0.0547; ESM 35M + MCNN is 0.5216 with SD 0.0655. Fold 4 is difficult across neural methods: One-hot + MCNN/ESM 8M + MCNN/ESM 35M + MCNN fold means are 0.3252/0.4153/0.3978. The cause is unresolved. Keep observations distinct from explanations. If a sophisticated model is unstable, treat that as a useful finding, not an inconvenient result to omit.

## Slide 15 — What Changed When We Changed One Component? (1:20)

**Message:** ablations explain which choices mattered under this protocol.

- Window and filter changes: quality versus capacity.
- Weighted loss: precision/recall trade-off.
- Encoder size: quality versus extraction and fitting cost.

**Visual:** Two or three source-backed contrasts from V09. Put the complete V09 and V10 encoder comparison in the appendix. **Evidence:** ablations CSV, CV summaries and cost tables. **Speaker notes:** Choose two or three observed contrasts rather than list every number. State the fixed conditions for each. Avoid declaring a universal best window from one dataset. Include negative findings such as no measurable benefit from added capacity.

**Full-run evidence for slide 15:** Window 3 selects AP 0.4868, with only 0.0138 between best and worst window means. Filter AP for 32/64/128/256 is 0.4922/0.5013/0.4985/0.5142, a non-monotonic trend. Weighted/unweighted 64-filter AP is 0.5013/0.4713, while MCC at 0.5 is 0.4225/0.4398. The larger encoder improves multi-window CV/test AP, but pooled and single-window test AP decrease.

## Slide 16 — Independent Test: A Final Check (1:00)

**Message:** the independent test checks the already chosen methods.

- Show AP, MCC, precision and recall for locked selections.
- Compare PR curves against prevalence and retain confusion counts.
- Report uncertainty given only 61 positive test cases.

**Visual:** V12 complete PR panel with short editable locked-metric callouts. Put confusion matrices and the full table in the appendix. **Evidence:** ensemble test metrics and bootstrap intervals. **Speaker notes:** Present the final check briefly. State whether thresholds are 0.5 or OOF-selected. Avoid switching the highlighted model based on a favorable test metric or treating a narrow ranking difference as decisive.

**Full-run evidence for slide 16:** ESM 35M + MCNN is also the highest CV selection scorer. Test AP One-hot + MCNN/ESM 8M + MCNN/ESM 35M + MCNN is 0.5408/0.5437/0.5758; locked-threshold MCC is 0.5495/0.5512/0.5513. ESM 35M + MCNN finds 44/61 positives with 52 FP; One-hot + MCNN finds 37 with 32 FP; ESM 8M + MCNN finds 33 with 22 FP. ESM 35M + MCNN AP 95% CI is [0.4631, 0.7061]. Exploratory paired ESM 35M + MCNN minus One-hot + MCNN AP CI is [-0.0444, 0.1151], so superiority is unresolved. Use a complete PR panel here; move the dense all-model confusion grid to the appendix.

## Slide 17 — Errors, Limitations and Lessons Learned (1:10)

**Message:** individual failures reveal limits hidden by aggregate metrics.

- Inspect representative false positives and false negatives.
- Discuss label quality, similarity control and source-domain generalization.
- Separate sequence-based prediction from a biological mechanism.

**Visual:** V13 editable error table from `../outputs/full_analysis/representative_errors.csv` on the left; concise limitations on the right. **Evidence:** error examples with IDs/probabilities/thresholds. **Speaker notes:** Error examples are selected reproducibly by confidence within FP/FN categories, not by a convenient biological story. Do not invent causal explanations from sequence appearance. Highlight padding and validation as methodological lessons.

**Full-run evidence for slide 17:** At ESM 35M + MCNN threshold 0.632288, retained length-35 negative sgh_sequence7831 scores 0.999930 (FP); length-11 neo_sequence56 scores 0.000162 (FN). Do not infer motifs or a padding defect from these examples. State the 61-positive test limit and unverified similarity filtering. The appendix must note that historical and current code hashes differ, so exact execution provenance needs the executed notebook.

## Slide 18 — Conclusions and Next Experiments (0:25)

**Message:** summarize what the investigation taught us about modeling choices.

- Answer the five questions with observed evidence.
- State the strongest methodological lesson and one unresolved question.
- Next: stronger similarity controls, external data and targeted interpretation.

**Visual:** Prompt K / V18 five questions, short observed lessons and one next experiment. **Evidence:** final executed summary and corresponding CV/test tables. **Speaker notes:** Do not promise a clinical application. End with the most informative next experiment, which should address an actual limitation observed during the project.

**Full-run evidence for slide 18:** Composition is insufficient; one-hot is a strong efficiency reference; CNN extraction helps pooled 8M features; multi-window gains also add capacity. ESM 35M + MCNN has the highest observed AP with uncertain differences. End with similarity-aware validation and an external cohort using locked choices, rather than a clinical claim. Assess representation, architecture, threshold, uncertainty and compute together.

## Appendix (not included in the 18-minute timing)

- Complete configurations and fixed-versus-tuned comparison tables.
- AP, ROC-AUC, MCC, precision/recall/specificity definitions and threshold policy.
- Full eight-model independent-test table, seed variation and bootstrap intervals.
- Additional FP/FN records and learning histories.
- Optional Prompt F / V07 research workflow.
- Bibliography and image credits; disclose AI illustrations after generation.

## Bibliography and credits

- Chuang et al. (2024). https://doi.org/10.1016/j.ijbiomac.2024.136252 . Dataset: https://github.com/B1607/DeepNeoAG .
- ESM models and implementation: https://github.com/facebookresearch/esm .
- Biological image credits are recorded in `VISUAL_ASSET_GUIDE.md`; include them on the relevant slide or final credits slide.

## Result insertion rules

Follow [the prompt pack](IMAGE_GENERATION_PROMPTS.md) for future image insertion. Update asset status only after generation, review and placement. No new images were generated or inserted in this outline update.

All inserted numbers use complete full-run evidence. Trace settings and metrics through `FULL_RESULTS_SLIDE_MAP.md`. Link every numeric statement to a run/configuration and source table. Preserve negative results and uncertainty. The talk explains research decisions and observations; deployment and execution tooling are documented separately.
