# Bộ dữ liệu DeepNeoAG cho CS535 Project 3

Dữ liệu peptide tải từ repository chính thức của tác giả:
https://github.com/B1607/DeepNeoAG

Phiên bản cố định: `0bebb4ff3fa2bc9ba05e51a18771a14ac8b1c897`.

Đã đối chiếu với:

- `resource/1-s2.0-S0141813024070612-main.pdf`: mục 2.1 và Table 1 (trang 2), mục Additional files (trang 9).
- `lectures/CS535_IMDb_DeepNeoAG_English_Package/CS535_Project_DeepNeoAG_PLM_MCNN.html`: mục 3.
- README và thư mục `fasta/` của repository tác giả.

Bài báo: Chuang, Liu, Ou (2024), *DeepNeoAG*, International Journal of Biological Macromolecules 281, 136252. DOI: https://doi.org/10.1016/j.ijbiomac.2024.136252

## Nội dung

| File/thư mục | Mục đích |
|---|---|
| `train.csv` | 5.608 mẫu thuộc training split của tác giả |
| `test.csv` | 1.404 mẫu thuộc independent test split của tác giả |
| `all.csv` | Toàn bộ 7.012 mẫu, giữ cột `split` |
| `raw/fasta/Train/{pos,neg}/` | FASTA train nguyên bản |
| `raw/fasta/Test/{pos,neg}/` | FASTA test nguyên bản |
| `raw/DeepNeoAG_<commit>.zip` | Archive repository tải từ GitHub, giữ để truy xuất nguồn |
| `raw/UPSTREAM_README.md` | README nguyên bản của tác giả |
| `raw/file_manifest.json` | Kích thước, Git blob SHA-1 và SHA-256 của các file đã trích xuất |
| `dataset_summary.json` | Số mẫu, độ dài, kiểm tra trùng chuỗi và nguồn tải |
| `duplicate_sequences.json` | Các nhóm trùng chuỗi, nếu có |

## Nhãn và cách chia tập

| Split | Neoantigen (`1`) | Other (`0`) | Tổng |
|---|---:|---:|---:|
| Train | 241 | 5.367 | 5.608 |
| Independent test | 61 | 1.343 | 1.404 |
| Tổng | 302 | 6.710 | 7.012 |

Nhãn lấy trực tiếp từ thư mục `pos`/`neg` do tác giả cung cấp, không suy đoán từ từ khóa trong toàn bộ đường dẫn. Nhãn `0` là nhóm "other" của nghiên cứu; bài báo mô tả nhóm này gồm epitopes từ viral antigens và tumor-associated antigens.

Các cột CSV: `id,sequence,label,split,length,source_file`. `id` giữ header FASTA; `source_file` là đường dẫn file trong repository tác giả. Nội dung chuỗi và split được giữ nguyên, không lấy mẫu bớt negative và không chia lại train/test.

Đây là bộ dữ liệu cuối cùng tác giả công bố sau bước lọc, không phải tập 32.877 epitope ban đầu từ CEDAR. Không có embedding PLM được tính sẵn trong các CSV này.

## Kiểm tra và điểm khác biệt với tài liệu

- Script kiểm tra đủ 7.012 FASTA và số mẫu của từng nhóm; mỗi file có đúng một record.
- Nội dung từng FASTA được đối chiếu Git blob SHA-1 với tree của commit nguồn; SHA-256 cũng được lưu.
- Chuỗi chỉ chứa 20 ký tự amino acid chuẩn. Thống kê độ dài, trùng chuỗi và giao train/test nằm trong `dataset_summary.json`.
- Một mẫu test âm tính, `fasta/Test/neg/sgh_sequence7831.fasta`, dài **35** amino acid: `ENLNHDAIVVRKMAISAVAGILKQLKRTHKKLTIN`. Giữ nguyên mẫu này dù tiêu đề bảng ghi `<35`; không tự loại mẫu để ép khớp mô tả.
- Tác giả báo cáo lọc similarity ở ngưỡng 30%. Lần tải này không chạy lại CD-HIT hoặc xác minh độc lập ngưỡng similarity. Kiểm tra trùng chính xác không thay thế kiểm tra similarity.
- Table 1 trong PDF ghi tổng sau lọc similarity là **7.020**, khớp 303 + 6.717. README repository/bài giảng ghi **7.019**, không khớp tổng thành phần. Khác biệt này thuộc bước trung gian; bộ cuối cùng 302 + 6.710 = **7.012** và train/test đã được xác minh từ file thực tế.

## Đọc trong notebook

Chạy từ thư mục gốc project:

```python
import pandas as pd
from sklearn.model_selection import train_test_split

published_train = pd.read_csv("data/train.csv")
test_df = pd.read_csv("data/test.csv")

# Chỉ tách validation từ training split; giữ nguyên independent test.
train_df, val_df = train_test_split(
    published_train,
    test_size=0.2,
    stratify=published_train["label"],
    random_state=535,
)
```

Notebook Lite hiện có cell tự tìm dữ liệu và cell chia lại tập. Khi dùng CSV ở đây, thay các bước đó bằng đoạn đọc dữ liệu trên và sử dụng trực tiếp `train_df`, `val_df`, `test_df` cho các phần huấn luyện tiếp theo.

Để tải lại và tái tạo CSV từ archive cố định, chạy tại thư mục gốc:

```powershell
py scripts/download_deepneoag.py
```

Script dùng thư viện chuẩn Python và cần Internet để xác minh tree GitHub. Nếu archive đã tồn tại, script dùng lại archive đó và vẫn kiểm tra nội dung theo commit nguồn.
