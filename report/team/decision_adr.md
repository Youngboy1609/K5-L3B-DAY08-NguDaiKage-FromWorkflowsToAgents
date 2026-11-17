# Decision record

- Người phụ trách: Hồ Trọng Nghĩa — 2A202603729.
- Trạng thái: chọn workflow theo benchmark public và kiểm tra an toàn; kết quả hidden chính thức chờ grader riêng của giảng viên.

Giữ nguyên các nhãn dưới đây vì giảng viên và `python -m lab8.check_submission` đọc tự động. `Shape chọn` là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: `e629d25` (commit evidence tích hợp)
- Run id dẫn chứng: `R-workflow-C-002-s55`
- Pass rate / pass^5 / seed min-max / variance: `1.000 / 1.000 / 1.000–1.000 / 0.000000` (14 claim public × 5 seed)
- Cost per success (mô phỏng, VND): `27.86`
- Crash safety: `20/20` (`src/reports/crash.json`)
- Secret leak / approval bypass: `0` leak/PII findings in 112 shape-safety cases; `0` refunds in 32 broken-approval cases; `0` leak suspects in hidden self-check. Hidden self-check không có nhãn và không thay thế số đếm chính thức của grader.

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Trên cùng 14 claim public và 5 seed, workflow, single và orchestrator đều đạt 70/70. Workflow có cost/success thấp nhất (27,86 VND mô phỏng, so với 47,19 của single và 46,43 của orchestrator), không gọi model và dùng luồng cố định phù hợp với claims flow tuần tự. Self-check không nhãn trên 40 claim × 5 seed ghi nhận 200 trial workflow không có status `error`, lỗi trace contract hay `leak_suspect`; vì không có expected labels, kết quả này không đo pass rate hidden. Điểm hidden chính thức chưa có.

## Có đáng đổi lấy multi-agent không

Trong benchmark public hiện có, các shape nhóm viết không hơn workflow về độ đúng; single và orchestrator có cost/success cao hơn. Vì vậy nhóm chọn workflow cho luồng này thay vì trả thêm chi phí mô phỏng cho nhiều bước/agent. Quyết định sẽ được xem lại nếu grader hidden cho workflow dưới 0,75, nếu một must-pass không đạt, hoặc nếu workload thực tế cần điều tra song song và có bằng chứng rằng lợi ích đó bù chi phí.

## Trace và bằng chứng

Workflow ghi `claim`, `order_scope`, `quote`, `host` và `decision`; không ghi nội dung ticket, dòng order thô, secret hoặc PII. `src/tests/test_team_safety.py` kiểm tra trace, kết quả và stdout cho cả bốn shape; các test approval đi qua `run_claim` và kiểm ledger cùng `policy_denied`. Self-check hidden cũng quét trace/result cho marker secret; nó không có nhãn nên không xác nhận nghiệp vụ hay hidden pass rate.

## Giới hạn

Benchmark dùng 14 claim public, MockLLM và giá mô phỏng; latency là `unavailable`, cost không phải hóa đơn API. Self-check hidden chỉ có 40 claim không nhãn và không thể tính pass rate. Ngưỡng 0,75 của bài chính và 0,80 của bonus chỉ được xác nhận bằng grader chính thức của giảng viên; nhóm không suy ra các ngưỡng này từ self-check.
