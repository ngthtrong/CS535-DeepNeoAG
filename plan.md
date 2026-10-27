
# DeepNeoAG Course Project — Revised Implementation and Presentation Plan

## 1. Mục tiêu và sản phẩm

Triển khai năm cách tiếp cận theo thứ tự:

**Composition + Logistic Regression → One-hot MCNN → ESM pooled → ESM single-window CNN → ESM MCNN**, rồi khảo sát window, filter, weighted loss và encoder 8M/35M.

Notebook và tài liệu bàn giao sử dụng tiếng Anh. Thuyết trình dài 15–20 phút, tập trung vào **câu hỏi nghiên cứu, quá trình triển khai, thiết kế thí nghiệm và bài học rút ra**.

**Điều chỉnh nội dung thuyết trình:**

- Bỏ slide giới thiệu hoặc so sánh với *Original Paper*.
- Không trình bày smoke run, Save Version, checkpoint hoặc resume.
- Bài báo vẫn được ghi trong tài liệu tham khảo.
- Smoke và checkpoint vẫn được triển khai trong notebook để kiểm tra và vận hành.

| Sản phẩm           | Nội dung                                                             |
| -------------------- | --------------------------------------------------------------------- |
| Dataset ZIP          | CSV, FASTA, nguồn và checksum để upload Kaggle                    |
| Một notebook Kaggle | Toàn bộ pipeline, chế độ smoke/full, log và xuất kết quả     |
| Presentation outline | 18 slide, speaker notes, thời lượng và figure mapping             |
| Visual asset guide   | Hình cần dùng, nguồn, attribution và prompt Gemini               |
| Kaggle run guide     | Hướng dẫn chạy và khôi phục phiên; tách khỏi thuyết trình |

## 2. Dataset, mô hình và phương pháp đánh giá

### Dataset ZIP

Đóng gói dữ liệu với `train.csv`, `test.csv`, `all.csv`, README, summary, checksum và FASTA nguyên bản.

- Giữ nguyên 5.608 train và 1.404 independent test.
- Giữ nhãn, thứ tự chuỗi và mẫu dài đúng 35 amino acid.
- Không lấy mẫu bớt negative trong full.
- Không đưa PDF, bài giảng, archive repository hoặc encoder checkpoint vào ZIP.
- Kiểm tra số mẫu, nhãn, alphabet, độ dài, duplicates và checksum trước khi đóng gói.
- Ghi rõ similarity filtering là quy trình tác giả báo cáo, chưa được chạy lại trong project.

### Các mô hình

| ID | Mô hình                              | Câu hỏi                                                      |
| -- | -------------------------------------- | -------------------------------------------------------------- |
| Composition + LR | Composition + Logistic Regression      | Thành phần amino acid đã đủ phân loại chưa?           |
| One-hot + MCNN | One-hot + MCNN                         | Học trực tiếp từ chuỗi hiệu quả đến đâu?            |
| ESM 8M + pooled LR | ESM-2 8M pooled + Logistic Regression  | Embedding học trước chứa thông tin hữu ích đến đâu? |
| ESM 8M + CNN | ESM-2 8M + single-window CNN           | CNN có khai thác thêm thông tin từ embedding không?      |
| ESM 8M + MCNN | ESM-2 8M + MCNN                        | Kết hợp nhiều độ dài cửa sổ có giúp ích không?     |
| ESM 35M + pooled LR | ESM-2 35M pooled + Logistic Regression | Encoder lớn hơn ảnh hưởng biểu diễn pooled thế nào?   |
| ESM 35M + CNN | ESM-2 35M + single-window CNN          | Encoder lớn hơn ảnh hưởng single-window CNN thế nào?    |
| ESM 35M + MCNN | ESM-2 35M + MCNN                       | Lợi ích có tương xứng với chi phí tính toán không?  |

Đóng băng encoder; lấy layer cuối: 8M có `D=320`, 35M có `D=480`. Mask padding khi mean pooling và loại các cửa sổ chạm padding trước global max pooling.

### Thử tham số

- Logistic Regression: `C={0.1,1,10}`, balanced class weights; scaler chỉ fit trên training.
- Single-window 8M: `window={2,3,4,5,8}`, 64 filters.
- MCNN mặc định: windows `[2,3,4,5,8]`, 64 filters mỗi nhánh.
- MCNN 8M: filters `{32,64,128,256}`, giữ weighted loss.
- Loss ablation: weighted/unweighted BCE tại MCNN 64 filters.
- One-hot MCNN giữ cấu hình mặc định.
- 35M pooled chọn `C` riêng; 35M CNN dùng window và cấu hình MCNN được chọn trên 8M.
- Tách bảng so sánh cấu hình cố định khỏi bảng so sánh mô hình sau tuning.

### Đánh giá

1. Dùng shared stratified 5-fold trên published train, split seed `535`.
2. Trong training portion của mỗi fold, tách 15% cho early stopping; outer validation chỉ dùng đánh giá.
3. Neural chạy seed `535,536,537`; LR một lần mỗi fold.
4. Chọn cấu hình bằng mean outer-fold AP; hòa trong `1e-6` thì ưu tiên MCC tại 0.5, số tham số ít hơn, rồi configuration ID.
5. Lưu OOF predictions; neural lấy trung bình xác suất ba seed.
6. Chọn thêm ngưỡng tối đa hóa MCC trên OOF; hòa thì chọn gần 0.5 nhất, sau đó ngưỡng lớn hơn.
7. Khóa cấu hình và threshold trước test.
8. Refit trên toàn bộ train; số epoch bằng trung vị làm tròn lên của best epochs trong CV.
9. Đánh giá tám mô hình đã chốt trên toàn bộ independent test; báo cáo từng seed và ensemble cho neural.

Metric gồm AP, ROC-AUC, MCC, precision, recall, specificity, F1, accuracy, balanced accuracy và confusion-matrix counts. Lưu kết quả tại 0.5 và OOF-selected threshold. Bootstrap stratified 2.000 lần trên test để ước lượng khoảng tin cậy 95% cho AP, ROC-AUC và MCC.

Không diễn giải CV đã dùng để tuning như đánh giá hoàn toàn độc lập. Không đổi cấu hình dựa trên test rồi tiếp tục gọi kết quả đó là independent evaluation.

## 3. Notebook và hệ thống lưu kết quả

### Cấu trúc

**Goal → Setup → Data Audit → EDA → Evaluation Protocol → Baselines → ESM Features → CNN Models → Controlled Experiments → Model Selection → Final Training → Test → Error Analysis → Figures and Export.**

Mỗi thí nghiệm có bốn phần: **question, controlled change, evidence, interpretation**. Kết luận được tạo từ output đã chạy.

Cấu hình đầu notebook:

```python
RUN_MODE = "smoke"  # or "full"
DATASET_DIR = None
RESUME_DIR = None
OUTPUT_DIR = "/kaggle/working/deepneoag_results"
```

Full dùng AdamW, learning rate `1e-3`, weight decay `1e-2`, CNN batch size `64`, extraction batch size `16`, dropout `0.3`, tối đa 30 epoch, patience 5 và tối thiểu 3 epoch. Class weight chỉ tính từ training partition.

### Smoke và vận hành

- Smoke dùng 256 train, 64 test lấy stratified, hai fold, một seed và một epoch.
- Kiểm tra cả encoder 8M/35M; window `{2,8}`, filter `{8,16}`, cả hai loss.
- Chạy đủ selection, refit, prediction, figure và export.
- Tách output/cache khỏi full; mọi kết quả mang nhãn kiểm tra pipeline.
- Full yêu cầu GPU, tự chạy toàn bộ trong một Save & Run All.
- Cache embedding kèm sequence order, checkpoint, layer và hash.
- Lưu checkpoint latest/best mỗi epoch, gồm optimizer và RNG state.
- Ngân sách mặc định 10 giờ; nếu chưa xong thì dừng tại ranh giới epoch và ghi trạng thái partial.
- Resume từ output phiên trước sau khi xác minh cấu hình và checksum.
- Trial lỗi có traceback; không báo complete khi thiếu trial.

### Output

| Nhóm                | Nội dung                                                  |
| -------------------- | ---------------------------------------------------------- |
| Configuration        | Resolved config, registry, seed, package versions và GPU  |
| Data audit           | Counts, lengths, duplicates, checksum và fold assignments |
| Features             | Embedding cache và manifest                               |
| Logs                 | Console, JSONL events, thời gian và lỗi                 |
| Per-run evidence     | Epoch history, checkpoints và predictions                 |
| Tables               | CV, OOF, selection, test metrics và test predictions      |
| Figures              | PNG 300 dpi và SVG                                        |
| Presentation exports | Slide-ready tables, captions và figure index              |
| Run status           | Complete/partial/failed, số trial dự kiến/đã xong     |

Mỗi kết quả truy ngược được tới run ID, encoder, cấu hình, fold và seed. Cuối phiên tạo archive kết quả, không sao chép lại dataset hoặc encoder weights.

## 4. Dàn ý thuyết trình và hình minh họa

### Dàn ý 18 slide, khoảng 18 phút

| Slide | English title                                                | Nội dung chính                                             |
| ----- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 1     | **DeepNeoAG: Learning Through Controlled Experiments** | Mục tiêu và phạm vi project                              |
| 2     | **Why Predict Neoantigen-like Peptides?**              | Bối cảnh sinh học                                         |
| 3     | **Defining the Prediction Problem**                    | Đầu vào, nhãn và ý nghĩa giới hạn của dự đoán   |
| 4     | **Five Questions Behind the Model Sequence**           | Lý do triển khai năm cách tiếp cận                     |
| 5     | **Dataset Provenance and Published Splits**            | Nguồn, số mẫu, nhãn và split                            |
| 6     | **Understanding the Data Before Training**             | Imbalance, độ dài, duplicates và chất lượng dữ liệu |
| 7     | **Designing a Fair Evaluation**                        | CV, early stopping, OOF và test                             |
| 8     | **Baseline 1: Amino-acid Composition**                 | Kiểm tra vai trò của thành phần chuỗi                  |
| 9     | **Baseline 2: One-hot MCNN**                           | Học mẫu chuỗi trực tiếp                                 |
| 10    | **From Peptides to Contextual Embeddings**             | Encoder, embedding và B/L/D                                 |
| 11    | **Pooling, Single-window CNN and MCNN**                | Ba cách khai thác embedding                                |
| 12    | **Our Controlled Experiment Matrix**                   | Window, filter, loss và encoder                             |
| 13    | **Tracking Learning and Computational Cost**           | Theo dõi loss, AP, thời gian và số tham số              |
| 14    | **What We Observed Across Folds and Seeds**            | Độ ổn định và learning curves                          |
| 15    | **What Changed When We Changed One Component?**        | Kết quả ablation và trade-off                             |
| 16    | **Independent Test: A Final Check**                    | Tóm tắt kết quả cuối                                    |
| 17    | **Errors, Limitations and Lessons Learned**            | FP/FN và bài học phương pháp                           |
| 18    | **Conclusions and Next Experiments**                   | Trả lời các câu hỏi nghiên cứu                        |

Mỗi slide có thông điệp chính, 3–4 ý, speaker notes, thời lượng, nguồn và figure ID. Tài liệu tham khảo và bảng tham số đầy đủ nằm ở phần phụ. Không đưa chi tiết vận hành Kaggle vào bài nói.

### Danh mục hình

| Hình                                           | Cách chuẩn bị                                  |
| ----------------------------------------------- | ------------------------------------------------- |
| Neoantigen, peptide–MHC và T-cell recognition | Gemini hoặc hình có giấy phép tái sử dụng |
| Năm mô hình và câu hỏi nghiên cứu       | Gemini theo cấu trúc chính xác                |
| Dataset và sơ đồ CV/test                    | Sơ đồ dựa trên split thực tế               |
| Class counts, length distributions              | Sinh từ CSV                                      |
| One-hot, contextual embedding và B/L/D         | Gemini, kiểm tra shape                           |
| Pooled, single-window và MCNN                  | Gemini, kiểm tra kiến trúc                     |
| Learning curves                                 | Sinh từ epoch logs                               |
| Window/filter/loss ablations                    | Sinh từ CV metrics                               |
| 8M vs 35M: chất lượng và chi phí           | Sinh từ metrics, runtime và parameter counts    |
| Fold/seed variability                           | Sinh từ CV results                               |
| Test PR/ROC và confusion matrices              | Sinh từ test predictions                         |
| FP/FN examples                                  | Sinh từ prediction records                       |

Nguồn sinh học có thể tái sử dụng:

- [NCI — neoantigen vaccine manufacturing diagram](https://www.cancer.gov/news-events/cancer-currents-blog/2025/neoantigen-vaccine-pancreatic-kidney-cancer): chọn hình quy trình ở giữa bài có credit CC BY 4.0.
- [Wikimedia — Antigen presentation.svg](https://commons.wikimedia.org/wiki/File:Antigen_presentation.svg): ghi attribution và CC BY-SA 3.0.

### Đặc tả prompt Gemini

Visual guide sẽ cung cấp prompt tiếng Anh hoàn chỉnh theo sáu chủ đề:

1. **Biological context:** mutation → altered peptide → MHC presentation → TCR recognition; thêm nhánh sequence classifier, không đồng nhất dự đoán với đáp ứng miễn dịch.
2. **Research approach map:** năm mô hình độc lập từ cùng đầu vào; mỗi mô hình đi kèm câu hỏi, không nối prediction của mô hình trước vào mô hình sau.
3. **Embedding and tensor shapes:** `[B,35,320] → [B,320,35]`, chú thích `D=480` cho 35M và đánh dấu padding.
4. **MCNN architecture:** năm nhánh window 2/3/4/5/8, 64 filters, masked max pooling, concat 320, dropout 0.3, linear và sigmoid khi inference.
5. **Evaluation protocol:** train 5.608 và test 1.404; fold training/early-stopping/outer-validation; khóa lựa chọn trước test, không có mũi tên test quay về tuning.
6. **Research workflow:** data understanding → baseline → pretrained representations → controlled experiments → model selection → independent evaluation → error analysis → lessons learned.

Tất cả dùng 16:9, nền trắng, nhãn tiếng Anh và bảng màu nhất quán. Không đưa smoke, Save Version, checkpoint hay resume vào hình dành cho thuyết trình. Gemini không tạo số liệu hoặc biểu đồ kết quả.

## 5. Thực hiện và nghiệm thu

**Thứ tự triển khai:**

1. Xác minh dữ liệu và tạo ZIP.
2. Xây dựng notebook, split registry và logging.
3. Hoàn thiện baseline, encoder và CNN có masking.
4. Hoàn thiện CV, tuning, OOF selection, refit và test.
5. Hoàn thiện output, hình và khả năng resume.
6. Chạy smoke từ kernel sạch, kiểm tra và sửa lỗi.
7. Bàn giao notebook, ZIP, hướng dẫn, dàn ý và visual guide.
8. Sau khi người dùng chạy full, điền kết quả thật vào dàn ý và speaker notes.

**Tiêu chí nghiệm thu:**

- ZIP đúng số mẫu, split và checksum.
- Không rò rỉ dữ liệu qua scaler, class weight, early stopping hoặc threshold selection.
- Padding được xử lý đúng; embedding và prediction khớp ID.
- Metric tính lại từ predictions khớp bảng lưu.
- Cache smoke/full tách biệt; resume không nhân đôi trial.
- Trial lỗi hoặc thiếu không tạo trạng thái complete.
- Notebook smoke chạy top-to-bottom và lưu đủ log, checkpoint, bảng, hình.
- Hình không cắt nhãn; kết luận truy ngược được tới kết quả thực tế.
- Dàn ý không có phần Original Paper hoặc smoke run; trọng tâm là quá trình nghiên cứu.
- Kết quả full và kết luận thực nghiệm được để trống cho đến khi chạy xong.

## 6. Cập nhật sau full run — 25/10/2026

- Đã nhận và đối soát `results_full/`: 258/258 lượt chạy, 8 họ mô hình; 1.580 file khớp manifest.
- Đã tính lại 258 dòng metric từng run, 52 dòng test, 8 ngưỡng OOF, 22 cấu hình CV và 48 dòng khoảng tin cậy bootstrap.
- Báo cáo toàn bộ quy trình, kết quả, phân tích lỗi, giới hạn và kết luận: [`docs/FULL_RESULTS_REPORT.md`](docs/FULL_RESULTS_REPORT.md).
- Đã thực hiện bước 8: điền kết quả thực vào dàn ý 18 slide và speaker notes; thêm [`docs/FULL_RESULTS_SLIDE_MAP.md`](docs/FULL_RESULTS_SLIDE_MAP.md), cập nhật visual guide và README. Thời lượng giữ nguyên 18 phút.
- ESM 35M + MCNN có AP test quan sát cao nhất (0,5758), nhưng khoảng tin cậy chênh lệch với One-hot + MCNN/ESM 8M + MCNN chứa 0; không kết luận vượt trội chắc chắn.
- Điểm còn thiếu để khép kín provenance: hash mã nguồn của full run khác mã nguồn/notebook hiện tại. Cần lưu bản notebook/source đã thực sự chạy từ phiên Kaggle tương ứng; không coi notebook hiện tại là bản đã tạo ra kết quả.
- Chi tiết nghiệm thu và các thí nghiệm khoa học đề xuất tiếp theo: [`docs/FULL_RUN_STATUS.md`](docs/FULL_RUN_STATUS.md). Các thí nghiệm mới cần dữ liệu/compute riêng; chưa được trình bày như kết quả đã hoàn thành.
