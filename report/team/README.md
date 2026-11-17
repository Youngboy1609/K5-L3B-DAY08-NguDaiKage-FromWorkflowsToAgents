# Hồ sơ báo cáo nhóm

Các file dưới đây là khung chuẩn bị. Chỉ điền kết quả, commit và test bằng bằng chứng thực tế. Phân công đầy đủ nằm ở [TEAM.md](../../TEAM.md).

| File | Người viết chính | Nội dung và giới hạn |
| --- | --- | --- |
| [group_report.md](group_report.md) | Trần Thị Nhài | Viết báo cáo nhóm tối đa 5 trang ngoài phụ lục; Nghĩa kiểm chứng và duyệt cuối |
| [decision_adr.md](decision_adr.md) | Hồ Trọng Nghĩa | Chốt shape sau benchmark; giữ nguyên các dòng nhãn để checker đọc |
| [research_card.md](research_card.md) | Trần Thị Nhài | R4; nguồn đã kiểm chứng, ablation bật/tắt draft, kết quả và giới hạn |
| [bonus_report.md](bonus_report.md) | Phạm Đăng Quang | B3; tối đa 2 trang; verifier, bộ đối kháng và phép so sánh |
| [2A202603729_HoTrongNghia.md](2A202603729_HoTrongNghia.md) | Hồ Trọng Nghĩa | Báo cáo cá nhân |
| [2A202603812_NguyenDucNhat.md](2A202603812_NguyenDucNhat.md) | Nguyễn Đức Nhật | Báo cáo cá nhân |
| [2A202603939_NgoNgocHai.md](2A202603939_NgoNgocHai.md) | Ngô Ngọc Hải | Báo cáo cá nhân |
| [2A202603911_TranThiNhai.md](2A202603911_TranThiNhai.md) | Trần Thị Nhài | Báo cáo cá nhân |
| [2A202603760_PhamDangQuang.md](2A202603760_PhamDangQuang.md) | Phạm Đăng Quang | Báo cáo cá nhân |
| [MSSV_HoTen.md](MSSV_HoTen.md) | File mẫu | Giữ lại để tham khảo |

## Bằng chứng cần nhận trước khi chốt

- Nhài: benchmark đủ 4 shape, crash report, kết quả test an toàn, research card, JSON ablation và bản group report để Nghĩa kiểm chứng.
- Quang: JSON B3 trên public/bộ đối kháng, số lần override, safety counts, test và mô tả trace minh họa.
- Mỗi thành viên: commit kỹ thuật, test đã thêm/sửa, phần việc thực tế và cách tự kiểm tra kết quả AI.
- Nghĩa: đối chiếu số liệu, chốt ADR, kiểm chứng group report do Nhài viết và hoàn thiện bảng đóng góp; giữ commit chốt nhất quán giữa báo cáo và ADR.

Kết quả JSON do công cụ sinh trong `src/reports/`; không tạo giả hoặc sửa tay. Chưa có module/thực nghiệm thì không đánh dấu lệnh dự kiến là đã chạy. Các trường bằng chứng còn trống nghĩa là hồ sơ chưa sẵn sàng nộp.
