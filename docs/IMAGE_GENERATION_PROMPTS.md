# DeepNeoAG — Bộ prompt và kế hoạch chuẩn bị hình ảnh

> Cập nhật 26/10/2026: I / V16, C / V05 và D / V06 đã hoàn thành và được chèn vào slide 12–14 của bản v3. Ba sơ đồ được thiết kế lại theo ngữ cảnh trang và cấu hình thực tế, không tạo từ prompt cũ. Xem [ghi chú và file PNG/SVG](assets/generated/README.md). Các kế hoạch bên dưới là bản lưu lịch sử.

Cập nhật: 25/10/2026. Phạm vi hiện tại: chuẩn bị prompt, tên file và vị trí chèn cho outline 18 slide / 18 phút. **Chưa tạo hoặc chèn ảnh.** Nội dung trên hình và slide giữ bằng tiếng Anh để khớp bài thuyết trình hiện có.

## Cách sử dụng ở bước tạo ảnh sau

Ghép **prompt chung** với một prompt A–K bên dưới. Lưu ảnh đã kiểm tra vào `docs/assets/generated/` theo đúng tên dự kiến; đường dẫn trong tài liệu là kế hoạch, chưa phải file có sẵn. Có thể dùng Gemini hoặc công cụ tạo ảnh khác. Ưu tiên A, B, C, D, E, I cho phần cốt lõi; G, H, J, K hoàn thiện câu chuyện; F dành cho phụ lục.

Các sơ đồ có nhiều nhãn nên được dựng hoặc sửa thành phần tử có thể chỉnh sửa trong phần mềm trình chiếu ở bước sau. Nếu công cụ làm sai chữ, để vùng trống rồi thêm nhãn trong slide. Không dùng ảnh minh họa để thay thế biểu đồ hay bảng số liệu thực nghiệm.

## Danh sách ảnh cần chuẩn bị

| Prompt / asset | Nội dung | Slide | File dự kiến | Khung ảnh và vị trí | Trạng thái |
|---|---|---|---|---|---|
| A / V01 | Sinh học neoantigen, MHC và TCR | 2 | `A_V01_biological_context.png` | 16:9, khoảng 2/3 dưới slide | Chờ tạo |
| B / V02 | Năm hướng mô hình độc lập | 4; bản rút gọn ở 1 | `B_V02_five_approaches.png` | 16:9, gần toàn bộ vùng nội dung | Chờ tạo |
| C / V05 | One-hot, embedding và kích thước tensor | 10 | `C_V05_embeddings.png` | 16:9, ba vùng ngang | Chờ tạo |
| D / V06 | Pooled LR, CNN và MCNN đã chọn | 11 | `D_V06_selected_architectures.png` | 16:9, ba hàng độc lập | Chờ tạo |
| E / V03 | Published split và quy trình đánh giá | 7; phần split ở 5 | `E_V03_evaluation.png` | 16:9, vùng nội dung chính | Chờ tạo |
| F / V07 | Quy trình nghiên cứu | Phụ lục | `F_V07_research_workflow.png` | 16:9, gần toàn slide | Chờ tạo, tùy chọn |
| G / V14 | Chuỗi đầu vào, điểm số và ngưỡng | 3 | `G_V14_prediction_endpoint.png` | 2:1, giữa slide | Chờ tạo |
| H / V15 | Composition bỏ qua thứ tự | 8 | `H_V15_composition.png` | 2:1, nửa dưới slide | Chờ tạo |
| I / V16 | One-hot MCNN, không có encoder | 9 | `I_V16_onehot_mcnn.png` | 16:9, phần dưới tiêu đề | Chờ tạo |
| J / V17 | Ma trận thí nghiệm có kiểm soát | 12 | `J_V17_experiment_matrix.png` | 16:9, bảng trung tâm | Chờ tạo |
| K / V18 | Năm câu hỏi và bài học | 18 | `K_V18_lessons.png` | 16:9, năm hàng ngắn | Chờ tạo |

V14–V18 bổ sung vào hệ mã V01–V13 hiện có. Slide 1 dùng các nhãn rút gọn dựng trực tiếp từ B, không thu nhỏ sơ đồ năm hàng. Slide 5 chỉ lấy phần split từ E. Giữ bản đầy đủ B/E cho slide 4/7.

## Prompt chung

```text
Create an original scientific teaching diagram for an English-language computational biology course presentation about DeepNeoAG. Use a white background, flat vector-like shapes, navy text (#183047), teal method blocks (#138A8A), light grey padding and held-out data, and restrained orange (#E89540) highlights for the changed component. Use one readable sans-serif font, generous whitespace and consistent line weights. No photorealism, decorative 3D, logos, watermarks or ornamental neural-network meshes.

Use the aspect ratio specified below, targeting at least 2400 pixels on the long edge. Keep a 5% safe margin and leave a clear caption area at the bottom. Use only the requested short English labels. Keep labels legible when placed in a 16:9 slide. If exact text cannot be rendered, leave clean label spaces for later editable text. Do not add numerical performance results, biological claims or model components that are absent from the brief. Conceptual matrices and marks must be visibly illustrative rather than experimental measurements. Do not imitate a published figure.
```

## A — Biological context / V01

**Caption dự kiến:** “Biological context. Sequence classification does not establish presentation or immune response.”

```text
Use a 16:9 landscape canvas. Show a left-to-right biological sequence: tumor-specific DNA mutation, altered protein, peptide generation, peptide displayed in an MHC molecule on a cell membrane, and recognition of that peptide–MHC complex by a T-cell receptor on a separate T cell. Highlight the altered residue in orange. The TCR must contact the peptide–MHC complex, never free DNA or a free peptide. Show the cell membranes clearly.

Below, draw a visually separate computational branch: “Peptide sequence” to “Sequence classifier” to “Neoantigen-like score”. Label this branch “Our project”. Do not imply that the classifier measures any of the biological stages above. Do not suggest every mutation is presented or recognized. Do not show guaranteed T-cell activation, treatment response or vaccine efficacy. Keep the biology schematic and labels short.
```

## B — Five independent approaches / V02

**Caption:** “Five research approaches. Each model receives the peptide independently.”

```text
Use a 16:9 canvas with five aligned horizontal rows. Each row starts with its own “Peptide sequence” input and ends with its own “Score”. Never connect one row's prediction to another row's input.

1. “Composition” then “Logistic Regression”. Question: “Are residue frequencies sufficient?”
2. “One-hot” then “MCNN”. Question: “What can ordered pattern learning achieve?”
3. “Frozen ESM-2” then “Masked mean” then “Logistic Regression”. Question: “What do pretrained features contain?”
4. “Frozen ESM-2” then “Single-window CNN” then “Max pooling” then “Classifier”. Question: “Does local extraction help?”
5. “Frozen ESM-2” then “Parallel CNN windows” then “Max pooling + concat” then “Classifier”. Question: “Do multiple scales help?”

Use orange outlines to identify the changed component without depicting a guaranteed improvement. A small footer may say “Five approaches; eight model families with 8M/35M comparisons”. Do not draw a performance ladder, leaderboard or winner icon. Do not show ESM fine-tuning.
```

## C — One-hot and contextual embeddings / V05

**Caption:** “Illustrative representations. Encoder dimension D is fixed by the checkpoint.”

```text
Create a 16:9 three-panel educational diagram. Use the generic 12-residue peptide “ACDEFGHIKLMN”.

Panel 1, “One-hot”: show a 12 by 20 matrix with exactly one active entry per residue row, followed by 23 grey padding rows, for 35 positions total. Label “Residue identity”, “12 real residues”, “23 padding rows”, and “[B,35,20]”.

Panel 2, “Contextual embedding”: the same peptide enters “Frozen ESM-2”. Show a conceptual heatmap labelled “12 real residues × D features” followed by 23 grey padding rows. Do not try to draw hundreds of individually labelled columns. Label “Special tokens removed” and “Illustrative values”. Embedding dimensions are unnamed learned features, not known biological properties.

Panel 3, “Tensor layout”: define “B: peptides per batch”, “L: padded positions”, “D: features per residue”. Show “8M: [B,35,320]” then “Transpose” then “[B,320,35]”. Separately show “35M: D=480”. Add “Real residues only in mean pooling” and “Mask convolution windows touching padding”. Do not change any tensor dimension during transpose or equate D with batch size.
```

## D — Selected pooling / CNN / MCNN architectures / V06

**Caption:** “Selected architectures. ESM is frozen; MCNN has five parallel branches.”

```text
Create a 16:9 diagram with three horizontal architecture rows. Title: “Selected architectures”. Use ESM 8M examples with D=320. Add one small note: “35M uses D=480 with the same transferred CNN settings”.

Row A, “Pooled LR”: “Frozen ESM embeddings [B,35,D]”, then “Mean over real residues [B,D]”, then “StandardScaler”, then “Balanced LR, C=0.1”, then “Score”.

Row B, “Single-window CNN”: “Frozen ESM embeddings”, then “Transpose [B,D,35]”, then “Conv1D k=3, 64 filters”, then “ReLU”, then “Mask invalid windows”, then “Global max [B,64]”, then “Dropout 0.3”, then “Linear: one logit”, then “Sigmoid at inference”.

Row C, “Multi-window CNN”: “[B,D,35]” fans out into five parallel branches labelled “k=2”, “k=3”, “k=4”, “k=5”, “k=8”. Each branch has “256 filters”, “ReLU”, “Mask invalid windows”, and “Global max [B,256]”. Merge via “Concat [B,1280]”, then “Dropout 0.3”, then “Linear: one logit”, then “Sigmoid at inference”. Use a shared legend for repeated branch operations if needed for readability.

Label “1280 = 5 × 256; separate from encoder D”. Show no gradients entering ESM. Never put the five kernels in sequence. Do not use the default 64-filter / 320-concat labels for selected ESM MCNN. Do not imply that MCNN's comparison isolates scale diversity from added capacity. No measured scores.
```

## E — Published split and fair evaluation / V03

**Caption:** “Selection uses training data. Independent testing follows locked choices.”

```text
Create a 16:9 evaluation diagram. Top strip: “Published data: 7,012 peptides” splits into “Training: 5,608; 241 positives; 5,367 others” and a clearly separated grey lane “Independent test: 1,404; 61 positives; 1,343 others”. Make this top strip self-contained so it can be reused on a dataset slide.

Below training, show “Shared stratified 5-fold CV”. Enlarge one outer fold: its outer-training portion splits into a fitting subset and an inner 15% early-stopping subset. A separate outer-validation portion supplies OOF predictions only after fitting. Label “Neural seeds: 535, 536, 537; shared partitions”. Include a separate note “LR: full outer-training portion; no early stopping”. Do not invent inner-subset counts.

Show “Configuration selection by mean CV AP” and “Threshold selection by OOF MCC”, followed by “Lock choices”, “Refit on all 5,608 training records”, and “Final evaluation”. Only connect the grey independent-test lane at final evaluation. No test-to-selection arrows. Mark “Selection CV is optimistic after tuning”. Keep the test lane separate from early stopping and all threshold decisions. Avoid operational infrastructure details.
```

## F — Research workflow / V07, phụ lục tùy chọn

**Caption:** “Research decisions and checks used in this investigation.”

```text
Create a 16:9 research workflow in two clearly connected rows. Stages: “Define endpoint”, “Audit data”, “Composition + one-hot baselines”, “Frozen ESM representations”, “Pooled / CNN / MCNN”, “Controlled ablations”, “CV selection”, “Lock choices”, “Independent test”, “Inspect errors”, “Lessons + next experiments”. Use orange only for research decision points.

Add two short callouts: “What did each change add?” and “How uncertain is the result?”. Do not imply that later stages guarantee better scores. Do not include cloud setup, deployment, checkpoints, resume logic, storage or execution tooling.
```

## G — Prediction endpoint / V14

**Caption:** “A ranking score becomes a binary decision at a locked threshold.”

```text
Create a 2:1 horizontal diagram. Show a generic FASTA-style input labelled “Peptide sequence”, then “Sequence classifier”, then “Score s”, then a decision node “s ≥ t?”. Branch to “Label 1: neoantigen” for yes and “Label 0: dataset other group” for no. Add “t selected from training OOF predictions” beneath the decision node.

Show no numeric example score, no patient details and no HLA allele input. Add a concise note: “Score is not proof of immunogenicity or a calibrated probability”. Keep score, ranking and thresholded decision visually distinct. Do not call label 0 a universally non-immunogenic peptide.
```

## H — Composition baseline / V15

**Caption:** “The same residue composition can occur in different sequence orders.”

```text
Create a 2:1 educational diagram. On the left show two example sequences “ACDL” and “LDCA”. Both feed the SAME 20-component normalized frequency vector. Highlight A, C, D and L at 0.25 each; all other components are zero. These are teaching examples, not dataset records.

Continue to “StandardScaler fitted on training data”, then “Balanced Logistic Regression”, then “Score”. Label “Order is lost” near the merge. Do not show a CNN or contextual encoder. Do not add experimental AP, accuracy or performance claims. Make the 20-component vector schematic and explicitly label its size if all letters would crowd the image.
```

## I — One-hot MCNN / V16

**Caption:** “One-hot MCNN learns ordered local patterns directly from task labels.”

```text
Create a 16:9 architecture diagram for the selected One-hot + MCNN baseline. Start with “Peptide” then “One-hot + padding [B,35,20]”, then “Transpose [B,20,35]”. Fan out into five parallel Conv1D branches k=2,3,4,5,8, each with 64 filters. Each branch applies ReLU, masks windows touching padding, and uses global max pooling to produce [B,64]. Merge into “Concat [B,320]”, then “Dropout 0.3”, then “Linear: one logit”, then “Sigmoid at inference”.

Show one small inset of a window sliding across valid residues; padding is grey. Mark an overlapping-padding window as excluded from max pooling. Add “No pretrained encoder” and “320 = 5 × 64”. Distinguish this head size from ESM embedding D=320 in other models. Do not insert ESM, depict sequential kernels, or use the 256-filter selected ESM architecture here. No measured results.
```

## J — Controlled experiment matrix / V17

**Caption:** “A staged, one-factor search. This is not a full factorial grid.”

```text
Create a 16:9 flat, readable experiment matrix with three columns: “Change”, “Values”, “Held fixed / caveat”. Use five rows:

“LR regularization” | “C: 0.1, 1, 10” | “Balanced LR; same folds”.
“Single CNN window, ESM 8M” | “k: 2, 3, 4, 5, 8” | “64 filters; weighted loss”.
“MCNN filters, ESM 8M” | “32, 64, 128, 256 per branch” | “k: 2,3,4,5,8; weighted loss”.
“MCNN loss, ESM 8M” | “Weighted / unweighted” | “64 filters; same windows”.
“Frozen encoder” | “8M / 35M” | “Transfer selected CNN settings; D and head size change”.

Highlight the changed component in orange. Footer: “22 configurations; 240 CV fits; 18 final refits”. Do not depict every possible row combination as tested. No leaderboard or fabricated effect sizes. Use short labels and roomy rows; leave text editable if it cannot be rendered clearly.
```

## K — Questions and lessons / V18

**Caption:** “Observed lessons under this protocol. Close model differences remain uncertain.”

```text
Create a 16:9 closing diagram with five simple aligned rows, pairing a question with a short evidence-based lesson:

“Composition sufficient?” | “Insufficient in this dataset”.
“Ordered supervised patterns?” | “One-hot MCNN is a strong efficiency reference”.
“Pretrained features?” | “Useful signal; pooling limits the classifier”.
“Local extraction?” | “CNN improves over pooled 8M features here”.
“Multiple scales?” | “Higher observed AP; capacity also increases”.

Below the rows, emphasize one next experiment: “Similarity-aware validation + external cohort with locked choices”. Add a small note: “35M MCNN has highest observed test AP; superiority unresolved”. No trophy, guaranteed improvement, clinical promise, new numerical results or invented biological mechanism. Keep the whole figure scannable for a short closing slide.
```

## Hình và bảng lấy từ dữ liệu, không dùng prompt tạo ảnh

| Slide | Asset có sẵn / nguồn | Cách đưa vào sau |
|---|---|---|
| 6 | `assets/full_results/V04_dataset.png` | Giữ số lượng lớp, trục chiều dài và mẫu dài 35 |
| 13 | `assets/full_results/V08_learning_curves.png`; `../results_full/tables/encoder_costs.csv` | Chọn learning-history panel dễ đọc; bảng chi phí là bảng chỉnh sửa được |
| 14 | `assets/full_results/V11_cv_comparison.png`; `V11_fold_seed.png` cùng thư mục | Biểu đồ trung bình làm hình chính, fold/seed làm inset hoặc phụ lục |
| 15 | `assets/full_results/V09_ablations.png`; `V10_encoder_comparison.png` cùng thư mục | Chọn 2–3 đối chiếu có điều kiện cố định rõ ràng; bản đầy đủ ở phụ lục |
| 16 | `assets/full_results/V12_test_curves.png`; `V12_confusion.png` cùng thư mục | PR panel đầy đủ trên slide chính; confusion grid ở phụ lục |
| 17 | `../outputs/full_analysis/representative_errors.csv` | Dựng bảng V13 bằng dữ liệu thật, giữ ID / nhãn / điểm / ngưỡng |

Đường dẫn trong bảng tính từ `docs/`. Caption gốc: `assets/full_results/figure_index.csv`. Chưa tạo thêm, cắt hoặc chèn các hình này trong lần cập nhật này. Bản đầy đủ và số liệu tham chiếu nằm trong [slide evidence map](FULL_RESULTS_SLIDE_MAP.md).

## Kiểm tra trước khi chèn ở bước sau

- Đúng nhánh song song, chiều mũi tên, số nhánh và các tensor B/L/D.
- One-hot MCNN: 64 bộ lọc/nhánh, concat 320. Selected ESM MCNN: 256/nhánh, concat 1280. Single CNN: k=3, 64 bộ lọc.
- Test tách khỏi chọn mô hình, early stopping và chọn ngưỡng; số liệu khớp `selected_models.csv` và slide map.
- Chữ đọc được ở kích thước trình chiếu. Thêm nhãn chỉnh sửa được nếu chữ do AI tạo sai.
- Ghi “AI-generated conceptual illustration” cho hình tạo bằng AI sau khi có ảnh thật. Hình nguồn ngoài giữ credit/license trong [visual guide](VISUAL_ASSET_GUIDE.md).
- Biểu đồ kết quả giữ trục, mẫu số, threshold policy và uncertainty caption. Không tạo số liệu bằng AI.
- Chỉ đổi trạng thái “Chờ tạo” khi file đã tồn tại và được kiểm tra; chỉ ghi “Đã chèn” sau khi kiểm tra slide.
