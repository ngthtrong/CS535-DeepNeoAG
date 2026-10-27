# DeepNeoAG – cấu trúc bộ slide v3

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

## Ba sơ đồ đã hoàn thành

| Slide | Sơ đồ | Đối tượng chỉnh sửa trong PowerPoint |
|---|---|---|
| 12 | I / V16 – One-hot MCNN | `DIAGRAM_I_EDITABLE` |
| 13 | C / V05 – Frozen embeddings, padding và B/L/D | `DIAGRAM_C_EDITABLE` |
| 14 | D / V06 – Ba bộ phân loại độc lập dùng ESM | `DIAGRAM_D_EDITABLE` |

Thiết kế lại theo ngữ cảnh trang và cấu hình thực nghiệm, không dùng lại trực tiếp prompt cũ. Bản v3 thay ba khung chờ bằng sơ đồ vector, giữ nguyên chữ, bảng và hình ảnh bên ngoài khung. Ungroup để sửa từng khối, nhãn hoặc mũi tên.

PNG và SVG riêng nằm trong `docs/assets/generated/`; thông tin nguồn và kích thước khung được ghi trong `diagram_assets_v3.json`. Không còn khung ảnh chờ bổ sung trong bộ slide này.

Bản v2 đưa thêm minh chứng vào phần chính nên thời lượng 18 phút của bản đầu không còn là tổng thời lượng được xác nhận. Speaker notes của các slide cũ được giữ nguyên.
