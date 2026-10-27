# DeepNeoAG – cấu trúc bộ slide v2

Bản v2 giữ nguyên 34 slide nội dung, số liệu và hình ảnh của bản trước. Thêm bốn trang chuyển phần và sắp xếp lại thành 38 slide.

| Phần | Slide |
|---|---|
| Cover | 1 |
| Introduction | 2–5 |
| Methodology | 6–16 |
| Results | 17–28 |
| Conclusion | 29–32 |
| Appendix chi tiết | 33–38 |

Trong PowerPoint, các phần cũng là **Sections** để dễ điều hướng trong Slide Sorter.

## Các minh chứng đã đưa lên phần chính

- Methodology: định nghĩa metric và threshold policy (10), cấu hình được chọn (16).
- Results: fold/seed variation (20), fixed defaults so với tuned selections (22), encoder và chi phí (23), bảng test đầy đủ (25), độ bất định và seed spread (26), PR/ROC đầy đủ (27), confusion matrices (28).
- Conclusion: execution provenance và giới hạn (31).

Phụ lục giữ hai bảng CV đủ 22 cấu hình, learning histories và ablation dạng đầy đủ, ví dụ lỗi bổ sung và credits.

## Highlight trong bảng

**Xanh nhạt, chữ đậm:** giá trị metric cao nhất trong cột đang so sánh hoặc mốc hiệu năng cần theo dõi. Giá trị cao nhất là quan sát mô tả, không tự xác lập khác biệt có ý nghĩa thống kê.

**Cam nhạt, chữ đậm:** điểm cần chú ý như 61 mẫu dương test, ranh giới split, số tham số, cấu hình đã chọn, khoảng bất định và lỗi dự đoán tự tin. Cam không có nghĩa là tốt hơn.

Không thay số liệu, đổi ngưỡng hoặc vẽ lại biểu đồ.

## Ảnh còn chờ bổ sung

| Slide mới | Tên khung | Prompt |
|---|---|---|
| 12 | `PLACEHOLDER_V16` – One-hot MCNN | I |
| 13 | `PLACEHOLDER_V05` – Embeddings, B/L/D | C |
| 14 | `PLACEHOLDER_V06` – Selected architectures | D |

Prompt nằm trong `docs/IMAGE_GENERATION_PROMPTS.md`. Cách thay ảnh và thông số kỹ thuật vẫn như hướng dẫn bản đầu. Dùng ảnh vừa khung, khóa tỷ lệ, không cắt mất nhãn hoặc nhánh.

Bản v2 đưa thêm minh chứng vào phần chính nên thời lượng 18 phút của bản đầu không còn là tổng thời lượng được xác nhận. Speaker notes của các slide cũ được giữ nguyên.
