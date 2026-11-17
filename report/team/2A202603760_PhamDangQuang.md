# Báo cáo cá nhân — Phạm Đăng Quang

## 1. Thông tin thành viên

- Họ tên: Phạm Đăng Quang
- MSSV: 2A202603760
- Email: 26ai.quangpd@vinuni.edu.vn
- GitHub: DanggQuangg

## 2. Phần việc phụ trách

- Vai trò: Bonus B3 — Swarm verifier, dữ liệu đối kháng và báo cáo bonus.
- File phụ trách trực tiếp:
  - `src/bonus/__init__.py`
  - `src/bonus/swarm_verified.py`
  - `src/bonus/cases.jsonl`
  - `src/bonus/world.json`
  - `src/bonus/evaluate_b3.py`
  - `src/tests/test_bonus_b3.py`
  - `src/reports/bonus_b3_*.json`
  - `report/team/bonus_report.md`
  - `report/team/2A202603760_PhamDangQuang.md`

## 3. Đóng góp cụ thể

1. **Khởi tạo và cấu trúc Package Bonus:**
   - Tạo `src/bonus/__init__.py` rỗng, độc lập với các shape khác để không gây xung đột dependency.
2. **Cài đặt Swarm Verifier (`src/bonus/swarm_verified.py`):**
   - Giữ nguyên chữ ký `run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult`.
   - Cài đặt cơ chế kiểm định độc lập bằng code trước khi gọi `issue_refund`: đối chiếu các trường dữ kiện tính toán (`delay_days`, `status`, `damage_verified`) với dữ liệu đơn hàng có cấu trúc trong SQLite DB.
   - Khi phát hiện sai lệch (do model bị đánh lừa bởi ticket hoặc điểm yếu tham chiếu ở seed % 5 == 0), verifier tự động ghi đè dữ kiện chuẩn, quote lại bồi thường (tối đa 1 vòng sửa) và ghi event `verifier_override` vào trace.
   - Tuân thủ nghiêm ngặt Trace Contract v1, đảm bảo không rò rỉ canary secret hay PII.
3. **Thiết kế tập dữ liệu đối kháng (`src/bonus/cases.jsonl` & `src/bonus/world.json`):**
   - Xây dựng 8 kịch bản đối kháng (`ADV-001` đến `ADV-008`) bao gồm: ticket nói quá ngày trễ, nói thiếu ngày trễ, nói dối hỏng hàng, chứa nhiều con số gây nhiễu, cố ý bóp méo dữ liệu đơn hàng.
   - Toàn bộ nhãn kỳ vọng (`expected`) được viết tay chuẩn xác theo [docs/business_rules.md](file:///C:/Study/VinAI/K5-L3B-DAY08-NguDaiKage-FromWorkflowsToAgents/docs/business_rules.md), tuyệt đối không dùng code tự sinh nhãn.
4. **Xây dựng bộ kiểm thử tự động (`src/tests/test_bonus_b3.py`):**
   - `test_b3_verifier_overrides_discrepancy_and_emits_event`: Kiểm tra việc phát hiện sai lệch, sửa quote và ghi event `verifier_override`.
   - `test_b3_verifier_safety_and_no_secret_leak`: Kiểm tra tuân thủ cổng host, duyệt approval và không rò rỉ secret vào trace.
   - `test_b3_comparison_swarm_vs_swarm_verified_on_adversarial_case`: Đối chứng trực tiếp Swarm tham chiếu bị fail ở seed 55 còn Swarm Verifier pass 100%.
   - `test_b3_crash_and_idempotency_compliance`: Kiểm tra khả năng xử lý `crash_at` và đảm bảo tính idempotency khi thử lại.
5. **Xây dựng công cụ đánh giá & sinh báo cáo thực nghiệm (`src/bonus/evaluate_b3.py`):**
   - Tự động hóa đánh giá trên 5 seed (`11, 22, 33, 44, 55`) cho cả tập public và tập đối kháng, xuất kết quả ra `src/reports/bonus_b3_public.json`, `src/reports/bonus_b3_adversarial.json`, `src/reports/bonus_b3_summary.json`.
6. **Hoàn thiện Báo cáo Bonus B3 (`report/team/bonus_report.md`):**
   - Viết báo cáo khoa học theo chuẩn Google Research 2026, đối chiếu giả thuyết, phân tích số liệu thực nghiệm, tính toán chi phí và nêu rõ giới hạn của MockLLM.

## 4. Bằng chứng

- **Test Suite:** Chạy `python -m pytest -q tests/test_bonus_b3.py` đạt **4 passed in 0.66s**.
- **Cổng Host:** Chạy `python -m pytest -q` đạt **54 passed**.
- **Mã commit kỹ thuật:** `4b95632` (triển khai B3 code, test, reports), `4a706b8` (cập nhật bảng đóng góp).
- **Kết quả đo lường trên tập đối kháng:**
  - `swarm`: Pass rate = 0.800, Pass^5 = **0.000**, Variance = 0.160000, Cost/success = 67.98 VND.
  - `swarm_verified`: Pass rate = **1.000**, Pass^5 = **1.000**, Variance = **0.000000**, Cost/success = **56.38 VND**, 8 lần can thiệp override thành công.
- **Trace bằng chứng:** Run ID `R-swarm_verified-ADV-001-s55` ghi nhận event `verifier_override` chính xác.

## 5. Công cụ AI đã dùng

- **Antigravity CLI & Codex CLI:**
  - Hỗ trợ rà soát contract, cấu trúc code verifier, tạo sinh các kịch bản đối kháng và kiểm tra định dạng báo cáo.
  - Mọi dữ liệu nhãn đối kháng và quyết định logic đều được người làm tự kiểm tra và thẩm định dựa trên tài liệu quy tắc nghiệp vụ.

## 6. Tự đánh giá

- **Mức độ hoàn thành:** 100% kế hoạch phân công cho Bonus B3.
- **Chất lượng:** Code chạy ổn định, sạch sẽ, tuân thủ toàn bộ must-pass gates, không sửa file cấm, test tự động xanh hoàn toàn và có báo cáo đối chứng khoa học rõ ràng.
