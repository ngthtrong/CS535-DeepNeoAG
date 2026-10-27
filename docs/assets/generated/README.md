# DeepNeoAG diagrams I, C and D

Created 26 October 2026 for slides 12–14 of `DeepNeoAG_Operating_Review_2026-10-26_v3.pptx`.

The diagrams were recomposed around each actual slide's explanation. The historical text-to-image prompts were not used as generation inputs. Labels remain in English to match the deck. All three diagrams are native editable PowerPoint groups, with SVG companions and PNG exports at four pixels per slide point. Their aspect ratios match the actual slide frames.

| Diagram | Slide | Focus | Files |
|---|---|---|---|
| I / V16 | 12 | One-hot input, five parallel Conv1D branches, 64 filters each, masked max pooling and 320-feature concat | `I_V16_onehot_mcnn.png`, `.svg` |
| C / V05 | 13 | Frozen ESM, removal of BOS/EOS, real residues versus padding, `[B,35,D]` to `[B,D,35]` | `C_V05_embeddings.png`, `.svg` |
| D / V06 | 14 | Independent pooled LR, single-window CNN and MCNN heads on the same frozen embeddings | `D_V06_selected_architectures.png`, `.svg` |

Diagram C's colored matrix is schematic, not a measured embedding visualization. The symbol ℓ denotes an individual peptide's true length. The selected ESM MCNN has 256 filters per window and 1,280 concatenated features; the one-hot MCNN has 64 and 320 respectively. Masking excludes convolution windows touching padding before global maximum pooling. Inference uses sigmoid for the neural heads. A score is not a claim of calibrated biological probability.

Scientific sources: `docs/EXPERIMENT_PROTOCOL.md` and `results_full/tables/selected_models.csv`. No new experimental results were generated or inferred.

The PowerPoint groups are named `DIAGRAM_I_EDITABLE`, `DIAGRAM_C_EDITABLE` and `DIAGRAM_D_EDITABLE`. Ungroup in PowerPoint to edit individual labels, blocks and connectors. SVG files can be imported into other vector editors. Reproducible build specifications and validation are in `tmp/presentation_diagrams/`.
