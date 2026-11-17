# Báo cáo cá nhân — Hồ Trọng Nghĩa

## 1. Thông tin thành viên

- Họ tên: Hồ Trọng Nghĩa
- MSSV: 2A202603729
- Email: 26ai.nghiaht@vinuni.edu.vn
- GitHub: Youngboy1609

## 2. Phần việc phụ trách

- Vai trò: nhóm trưởng; workflow; tích hợp; ADR và kiểm chứng báo cáo cuối.
- Phụ trách `src/lab8/shapes/workflow.py`, `src/tests/test_team_workflow.py`, `TEAM.md` và `report/team/decision_adr.md`; kiểm chứng `report/team/group_report.md` do Nhài tổng hợp.
- Triển khai workflow cố định từ contract và host có sẵn: đọc claim/order bằng tool, tính quote bằng code, chuyển quote đầy đủ cho host, ghi trace an toàn và truyền `crash_at`.
- Tích hợp benchmark, crash, ma trận student và self-check hidden không nhãn; chọn workflow từ số đo public và ghi rõ giới hạn hidden trong ADR.

## 3. Đóng góp cụ thể

- Triển khai workflow cố định dùng read tools, compute_compensation và host issue_refund; thêm regression tests cho claim không tồn tại, ticket không thể override order, ba điểm crash và conflict khi retry khác amount.
- Commit kỹ thuật: `6317f88`.

## 4. Bằng chứng

- Môi trường: Python 3.12.13 trên Windows; do launcher `py` trỏ tới interpreter không tồn tại, các lệnh được chạy bằng môi trường Python 3.12 có sẵn.
- Regression tests của workflow: `python -m pytest -q tests/test_team_workflow.py` — 6 passed; student tests của workflow — 62 passed.
- Trên bản tích hợp đủ 4 shape và R4: `python -m pytest -q` — 425 passed; ma trận student — 248 passed; `python -m lab8.smoke` pass; crash suite — 20/20.
- Benchmark public: 4 shape × 14 claim × 5 seed; workflow đạt 70/70, pass rate 1.000, cost/success 27,86 VND mô phỏng.
- Self-check ẩn không nhãn: workflow chạy 200 trial trên 40 claim × 5 seed; 0 status `error`, 0 lỗi trace contract và 0 `leak_suspect`. Vì không có nhãn, đây không phải pass rate và không thay grader chính thức.
- `python -m lab8.check_submission` — 0 FAIL sau khi điền ADR; chạy lại trên commit sạch trước khi nộp.

## 5. Công cụ AI đã dùng

Codex hỗ trợ viết code/test và soạn plan. Các thay đổi được kiểm bằng test regression, ma trận student, host gate, smoke và crash suite ghi ở trên.

## 6. Tự đánh giá

- Tôi hoàn thành workflow và các regression tests được giao, đồng thời đối chiếu số liệu public, crash, an toàn và hidden self-check không nhãn trước khi ghi quyết định kiến trúc.
- Tôi chọn workflow vì các shape nhóm viết cùng đạt 70/70 trên public, trong khi workflow có cost/success thấp nhất. Quyết định còn phụ thuộc kết quả hidden chính thức; self-check không nhãn không thể xác nhận ngưỡng pass rate.
