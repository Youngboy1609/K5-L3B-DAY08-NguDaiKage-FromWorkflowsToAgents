# Báo cáo cá nhân — Hồ Trọng Nghĩa

## 1. Thông tin thành viên

- Họ tên: Hồ Trọng Nghĩa
- MSSV: 2A202603729
- Email: 26ai.nghiaht@vinuni.edu.vn
- GitHub: Youngboy1609

## 2. Phần việc phụ trách

Phân công dự kiến; chưa phải kết quả đã hoàn thành.

- Vai trò: nhóm trưởng; workflow; tích hợp; ADR và kiểm chứng báo cáo cuối.
- Phụ trách `src/lab8/shapes/workflow.py`, `src/tests/test_team_workflow.py`, `TEAM.md`, `report/team/decision_adr.md`. Đọc và kiểm chứng `report/team/group_report.md` do Nhài viết.
- Bắt đầu ngay từ contract, host và dữ liệu public có sẵn: triển khai workflow cố định, tính quote bằng code, gọi host với quote đầy đủ, ghi trace an toàn và truyền crash_at.
- Bàn giao: 62 test student của workflow xanh; test mới kiểm nghiệp vụ, trần theo đơn, retry/crash.
- Sau bàn giao các phần: tích hợp, rà bằng chứng với Nhài, chốt ADR theo benchmark thực tế, kiểm chứng báo cáo nhóm Nhài bàn giao bằng code, test và JSON thực tế và kiểm tra bài nộp.

## 3. Đóng góp cụ thể

- Triển khai workflow cố định dùng read tools, compute_compensation và host issue_refund; thêm regression tests cho claim không tồn tại, ticket không thể override order, ba điểm crash và conflict khi retry khác amount.
- Commit kỹ thuật: `6317f88`.

## 4. Bằng chứng

- Môi trường: Python 3.12.13 trên Windows; launcher `py` cũ trỏ tới interpreter không tồn tại, nên dùng Python 3.12 đã có qua uv.
- Trước sửa: `python -m lab8.smoke` pass; host gate `54 passed`.
- TDD: 6 regression tests đỏ trên stub vì `not_implemented`, không phát crash và chưa có hàm quote trong module.
- Sau sửa: `python -m pytest -q tests/test_team_workflow.py` — 6 passed.
- `python -m pytest -q -m student -o addopts= -k workflow` — 62 passed.
- `python -m pytest -q` — 60 passed, 248 deselected.
- `python -m lab8.smoke` pass; crash suite — 20/20.
- Kết quả này chỉ xác nhận workflow và host hiện tại; chưa xác nhận các shape khác hoặc hidden.

## 5. Công cụ AI đã dùng

Codex hỗ trợ viết code/test và soạn plan. Các thay đổi được kiểm bằng test regression, ma trận student, host gate, smoke và crash suite ghi ở trên.

## 6. Tự đánh giá
