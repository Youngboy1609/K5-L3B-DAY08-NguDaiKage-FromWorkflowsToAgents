# Báo cáo cá nhân — Nguyễn Đức Nhật

## 1. Thông tin thành viên

- Họ tên: Nguyễn Đức Nhật
- MSSV: 2A202603812
- Email: 26ai.nhatnd@vinuni.edu.vn
- GitHub: NguyenDucNhat3006

## 2. Phần việc phụ trách

- Phụ trách shape `single` trong `src/lab8/shapes/single.py` và test riêng trong `src/tests/test_team_single.py`.
- Xử lý claim bằng `lab8.runtime.run_react` với tối đa 8 bước. Hàm `decide()` chọn các tool đọc theo trạng thái đã quan sát; `worker=True` chặn tool ghi. MockLLM hiện không trả lựa chọn tool có cấu trúc.
- Tiền được tính bằng `compute_compensation`; sau vòng lặp, code chuyển quote đầy đủ cho `durability.issue_refund` để host kiểm approval, trần theo đơn và idempotency.

## 3. Đóng góp cụ thể

- Triển khai `run_claim` cho shape `single`: đọc claim và order theo principal, xử lý các nhánh `failed`, `needs_info`, `escalated`, `denied`, `resolved`, trả `RunResult` qua `finish()` và ghi trace ở các nhánh trả về.
- Giới hạn vòng ReAct ở 8 bước, đếm lượt MockLLM và tool trong `Budget`. Chỉ đưa dữ liệu đã chọn lọc vào trace; không ghi ticket, secret hay dòng order thô.
- Gọi `issue_refund` với quote đầy đủ và truyền `crash_at`; khi có `InjectedCrash`, ghi sự kiện crash rồi cho exception truyền ra để kiểm tra khả năng chạy lại.
- Thêm ba test riêng: kiểm giới hạn bước, tool đọc và quote đầy đủ; kiểm runtime từ chối tool ghi; kiểm ticket giả mạo và secret không làm sai quyết định hoặc lọt vào trace.
- Commit kỹ thuật: **chưa tạo**. Bổ sung hash sau khi tự rà soát và commit hai file code/test.

## 4. Bằng chứng

- Lệnh chạy từ `src/`: `python -m pytest -q -m student -o addopts= -k "single and not workflow and not orchestrator and not swarm"` → **62 passed**.
- `python -m pytest -q tests/test_team_single.py -o addopts=` → **3 passed**.
- Các test mới: `test_single_uses_bounded_read_tools_and_full_quote`, `test_react_rejects_model_write_request`, `test_single_trace_omits_ticket_and_secret`.
- C-014 cho `proposal_amount=150000` VND và ledger ghi `120000` VND vì đơn đã được hoàn trước `30000` VND. Test riêng xác nhận quote đầy đủ được chuyển cho host.
- Link commit và run id: 

## 5. Công cụ AI đã dùng

- Dùng Codex/ChatGPT để đọc cấu trúc repo, làm rõ phân công, giải thích kiến trúc single ReAct, gợi ý và viết mã tham khảo cho `single.py` cùng `test_team_single.py`, sau đó giải thích từng phần và review code.
- Tôi đọc lại code, đối chiếu với contract và yêu cầu được giao, hỏi lại các điểm chưa rõ, sửa lỗi được phát hiện khi review và trực tiếp quan sát bộ 62 test student chạy thành công. Kết quả test riêng được kiểm tra trong cùng môi trường làm việc.
- Tôi chịu trách nhiệm rà soát nội dung báo cáo và chỉ ghi bằng chứng thực tế; chưa ghi hash commit, benchmark hoặc run id khi chưa có.

## 6. Tự đánh giá

- Tôi đã hiểu luồng xử lý: tool đọc thu thập dữ liệu; `compute_compensation` tính quote; host kiểm quyền, approval và số tiền trước khi ghi refund. Tôi hiểu lý do phải truyền quote đầy đủ và để host xử lý phần đã hoàn trước đó.
- Phần của tôi đạt 62/62 test student của `single` và 3/3 test riêng trên bộ public. Điều này xác nhận các trường hợp public đã kiểm, chưa xác nhận pass rate của bộ hidden.
- Giới hạn hiện tại: MockLLM được gọi và tính chi phí nhưng đầu ra không quyết định tool; `decide()` chọn tool đọc bằng quy tắc trong code. Tôi cần trình bày rõ lựa chọn này khi nhóm chốt kiến trúc và báo cáo.
