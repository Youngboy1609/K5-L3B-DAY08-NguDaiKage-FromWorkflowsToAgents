# Báo cáo cá nhân — Phạm Đăng Quang

## 1. Thông tin thành viên

- Họ tên: Phạm Đăng Quang
- MSSV: 2A202603760
- Email: 26ai.quangpd@vinuni.edu.vn
- GitHub: DanggQuangg

## 2. Phần việc phụ trách

Phân công dự kiến; chưa phải kết quả đã hoàn thành.

- Vai trò: bonus B3 — swarm verifier, dữ liệu đối kháng và báo cáo bonus.
- Phụ trách `src/bonus/__init__.py` (rỗng), `src/bonus/swarm_verified.py`, `src/bonus/cases.jsonl`, `src/bonus/world.json`, `src/bonus/evaluate_b3.py`, `src/tests/test_bonus_b3.py`, `src/reports/bonus_b3_*.json`, `report/team/bonus_report.md`.
- Bắt đầu ngay từ swarm tham chiếu có sẵn; không sửa file tham chiếu, không phụ thuộc ablation của Nhài hay code workflow mới.
- Thêm verifier bằng code trước ghi tiền, đối chiếu delay_days/status/damage_verified với order có cấu trúc; nếu lệch thì quote lại tối đa 1 vòng và ghi verifier_override.
- Tạo ít nhất 8 claim đối kháng; nhãn viết tay theo business_rules, không sinh nhãn bằng compensation.quote. Thêm ít nhất 2 test có ý nghĩa, bao gồm sửa dữ kiện và giữ ranh giới an toàn.
- Đo swarm/swarm_verified ngay trên public và bộ tự viết; khi tích hợp thêm workflow vào cùng phép so sánh. Báo pass rate, pass^5, variance, cost/success, safety counts, số lần override và trace minh họa.
- Bàn giao: code/test chạy được, JSON sinh bằng script, lệnh tái lập và báo cáo B3 tối đa 2 trang; nêu nguồn, CLAIM/BOUNDARY và giới hạn MockLLM.

## 3. Đóng góp cụ thể


## 4. Bằng chứng


## 5. Công cụ AI đã dùng


## 6. Tự đánh giá
