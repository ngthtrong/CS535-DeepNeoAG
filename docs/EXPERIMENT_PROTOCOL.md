# Experiment Protocol

## Questions and models

| Family | Representation | Downstream model | Question |
|---|---|---|---|
| Composition + LR | 20 normalized amino-acid frequencies | StandardScaler + balanced LR | Is composition sufficient? |
| One-hot + MCNN | Ordered one-hot residues, padded to 35 | Masked MCNN | What does supervised pattern learning achieve? |
| ESM 8M + pooled LR | ESM-2 8M, masked mean | StandardScaler + balanced LR | What information is present in pretrained features? |
| ESM 8M + CNN | ESM-2 8M per residue | Masked single-window CNN | Does local extraction help? |
| ESM 8M + MCNN | ESM-2 8M per residue | Masked MCNN | Are multiple scales useful? |
| ESM 35M + pooled LR | ESM-2 35M, masked mean | StandardScaler + balanced LR | Does encoder size help pooled classification? |
| ESM 35M + CNN | ESM-2 35M per residue | ESM 8M + CNN-selected CNN architecture | Does encoder size help local extraction? |
| ESM 35M + MCNN | ESM-2 35M per residue | ESM 8M + MCNN-selected MCNN architecture | Does encoder size help multi-scale extraction? |

All ESM parameters are frozen. The 8M model uses layer 6, D=320; 35M uses layer 12, D=480. Remove BOS/EOS; retain amino-acid positions only. Feature caches store float16, then cast to float32 for training on both initial and resumed sessions. No task labels enter encoder feature extraction. Embedding the test sequences without labels using a frozen, unchanged encoder does not tune the classifier.

## Controlled configurations

- Composition + LR/ESM 8M + pooled LR/ESM 35M + pooled LR LR: `C = 0.1, 1, 10`, `class_weight='balanced'`, `max_iter=2000`, solver `lbfgs`. Standardization is fit within the corresponding training partition.
- One-hot + MCNN: windows `[2,3,4,5,8]`, 64 filters per window, weighted loss.
- ESM 8M + CNN: one of `[2]`, `[3]`, `[4]`, `[5]`, `[8]`, 64 filters, weighted loss.
- ESM 8M + MCNN: windows `[2,3,4,5,8]`, weighted loss with 32/64/128/256 filters; plus unweighted loss at 64 filters. This is a one-factor experiment, not a full factorial search.
- ESM 35M + CNN transfers the selected ESM 8M + CNN window/filter/loss; ESM 35M + MCNN transfers selected ESM 8M + MCNN filter/loss. No additional 35M CNN tuning.
- All neural models: Conv1D → ReLU → mask invalid windows → global max → concatenate → dropout 0.3 → one-logit Linear. Sigmoid is applied for inference; train with BCEWithLogitsLoss.
- Optimizer AdamW, LR 0.001, weight decay 0.01, batch 64. No LR search. ESM batch 16, sequence capacity 35.

The shortest observed sequence is 11, so all listed windows have valid positions. Code still handles an entirely invalid branch by returning a zero pooled vector. Padding cannot activate the maximum. The same rules apply to one-hot and ESM.

### Fixed and tuned comparisons

`fixed_configuration_comparison.csv` contains Composition + LR/ESM 8M + pooled LR at C=1, One-hot + MCNN default, ESM 8M + CNN window 3, ESM 8M + MCNN default 64 filters weighted. Use this for the matched one-hot/ESM MCNN comparison. `selected_models.csv` and selected CV tables describe tuning outcomes. Do not label a tuned-vs-fixed difference as an isolated representation effect.

Composition + LR→One-hot + MCNN changes both classifier and representation. Pooled contextual ESM retains order information. MCNN changes capacity as well as window diversity. 35M changes D and hence downstream parameter count; report trainable parameter counts, frozen model size and runtime separately.

## Data and cross-validation

- Published train: 5,608 / 241 positives. Independent test: 1,404 / 61 positives. Test prevalence is approximately 4.34%; a majority-class classifier can exceed 95% accuracy.
- Shared `StratifiedKFold(5, shuffle=True, random_state=535)` on published train.
- For each outer fold, split 15% of its training partition for early stopping, seed `535+fold`. Neural training sees only the fit portion. LR sees the complete outer-training partition because it has no stopping decision.
- Neural initializations 535,536,537 use exactly the same data partitions. Deterministic algorithms are requested with warning mode; hardware/kernel differences can still matter.
- Weighted loss uses negative/positive count from the actual fit partition, never a global or test count. Unweighted uses weight 1.
- Maximum 30 epochs, minimum 3, patience 5. Save best early-stopping AP checkpoint; outer validation is evaluated after training completes.
- LR: nine configurations × five folds = 45 fits. Neural: thirteen configurations × five folds × three seeds = 195 CV fits. Final training adds 3 LR fits and 15 neural fits: **258 total full fits**. Early stopping reduces epochs, not the number of required fits.

## Selection and threshold

Select by mean AP across outer folds and initializations. AP ties within 1e-6 are resolved by higher mean MCC at 0.5, then fewer trainable parameters, then configuration ID. The reported CV mean is used for tuning and is not an unbiased post-selection performance estimate.

For each selected configuration, average OOF probabilities across neural seeds per peptide. Evaluate thresholds at all unique OOF probabilities, 0, 0.5 and just above the maximum. Maximize OOF MCC; ties prefer closest to 0.5, then the larger threshold. This selects an operating point, not probability calibration. Weighted BCE probabilities need not be calibrated.

Persist `locked_selection.json` before any final fitting/test evaluation. Refit neural models on all 5,608 training records for ceil(median of CV best epochs). No test early stopping. Final LR is refit once; final CNNs use all three seeds.

## Metrics and uncertainty

Export AP, ROC-AUC, MCC, precision, recall, specificity, F1, accuracy, balanced accuracy, TN/FP/FN/TP and threshold. AP is `average_precision_score`, not trapezoidal PR area. Undefined precision/F1 is zero with the confusion counts retained; AUROC/AP require both labels.

Test summaries include each seed and the arithmetic mean-probability ensemble at 0.5 and at the locked OOF threshold. Stratified bootstrap resamples test positives and negatives independently with replacement, 2,000 times, seed 535. Report percentile 95% intervals for AP, ROC-AUC and MCC conditional on this test and fitted model. They do not capture encoder, training or dataset-selection uncertainty. Fold/seed SD is descriptive, not a confidence interval; folds/seeds are not independent replicates.

## Analysis boundaries

No MHC/HLA assignments are available in the CSV; no class is inferred from length. Do not claim clinical utility, immune activation, natural processing or presentation from the sequence score. Negative-label quality, only 61 positive test samples, source-domain generalization and unverified similarity filtering remain limitations. No threshold or hyperparameter is altered after test inspection.
