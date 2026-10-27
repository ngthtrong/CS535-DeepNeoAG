# DeepNeoAG – hướng dẫn sử dụng bộ slide

Bộ PowerPoint dùng template Operating Review, gồm 18 slide chính bằng tiếng Anh (18 phút) và 16 slide phụ lục. Speaker notes của 18 slide chính có thời lượng, lời dẫn và đường dẫn minh chứng.

## Hình kết quả thực nghiệm

Các slide 6, 13–16 ưu tiên ảnh kết quả từ `docs/assets/full_results/`: phân bố dữ liệu, training loss và early-stop AP, CV, ablation và precision–recall. Phụ lục giữ toàn bộ learning histories, fold/seed scatter, ablation, encoder comparison, PR/ROC và confusion matrices. Các ảnh kết quả được nhúng vào PowerPoint, không cần mang theo thư mục ảnh để trình chiếu.

Slide 16 dùng nguyên panel PR, giữ trục và legend. Bản PR/ROC đầy đủ ở slide 30. Số liệu trên slide và bảng dùng các lựa chọn đã khóa, `aggregation=ensemble`, `policy=oof_selected`.

## Ba ảnh cần bổ sung

| Slide | Tên khung trong Selection Pane | Nội dung | Prompt có sẵn |
|---|---|---|---|
| 9 | `PLACEHOLDER_V16` | One-hot MCNN: 64 filters/branch, concat 320 | Prompt I |
| 10 | `PLACEHOLDER_V05` | One-hot, contextual embeddings và tensor B/L/D | Prompt C |
| 11 | `PLACEHOLDER_V06` | Pooled LR, single CNN, selected ESM MCNN: 256 filters/branch, concat 1,280 | Prompt D |

Các prompt nằm trong `docs/IMAGE_GENERATION_PROMPTS.md`. Dùng ảnh 16:9, nền trắng, chữ tiếng Anh rõ ràng. Kích thước và tọa độ khung (đơn vị point) có trong `image_placeholders.json`.

Trong PowerPoint, mở **Home → Select → Selection Pane** để tìm khung. Chèn ảnh, khóa tỷ lệ, thu ảnh vừa bên trong khung, căn giữa rồi xóa khung placeholder. Không kéo méo ảnh hoặc cắt mất nhãn, nhánh kiến trúc và tensor. Slide 10 có khoảng trắng để giữ nguyên tỷ lệ ảnh khi vừa khung.

Nếu ảnh có AI hỗ trợ, thêm “AI-generated conceptual illustration” vào caption hoặc credits sau khi kiểm tra. Giữ các bảng và thông số ở ngoài ảnh để tiếp tục chỉnh sửa được.

## Phụ lục

| Slide | Nội dung |
|---|---|
| 19 | Selected configurations, số tham số, ngưỡng, refit epochs |
| 20–21 | Đầy đủ 22 cấu hình CV |
| 22 | Fixed defaults so với tuned selections |
| 23 | Định nghĩa metric và threshold policy |
| 24–27 | Learning histories, fold/seed, ablation, encoder/cost |
| 28–29 | Test metrics, bootstrap intervals và single-seed spread |
| 30–31 | PR/ROC đầy đủ và confusion matrices |
| 32 | Ví dụ FP/FN thật |
| 33 | Execution provenance và giới hạn |
| 34 | Tài liệu tham khảo và image credits |

Phụ lục nằm ngoài thời lượng 18 phút. Chỉ trình bày khi cần giải thích hoặc trả lời câu hỏi.

Giữ lưu ý về 61 mẫu dương test, độ bất định và khác biệt code hash trong phụ lục. Chênh lệch AP nhỏ chưa xác lập mô hình vượt trội. Bảng số liệu và sơ đồ đơn giản vẫn là đối tượng PowerPoint chỉnh sửa được.
