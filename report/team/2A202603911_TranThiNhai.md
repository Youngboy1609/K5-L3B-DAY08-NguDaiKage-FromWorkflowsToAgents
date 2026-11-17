# Báo cáo cá nhân — Trần Thị Nhài

## 1. Thông tin thành viên

- Họ tên: Trần Thị Nhài
- MSSV: 2A202603911
- Email: 26ai.nhaitt@vinuni.edu.vn
- GitHub: chanhochust

## 2. Phần việc phụ trách

- Vai trò: QA; ablation độc lập cho research card R4; benchmark/crash chính thức; viết báo cáo nhóm.
- File phụ trách: `src/tests/test_team_safety.py`, `src/tests/test_research_ablation.py`, `src/bonus/swarm_no_draft.py`, `src/bonus/research_ablation.py`, `src/reports/research_ablation.json`, `src/reports/benchmark.json`, `src/reports/crash.json`, `report/team/research_card.md`, `report/team/group_report.md`.
- Phần ablation và test an toàn làm song song trên host và swarm tham chiếu, không phụ thuộc ba shape mới hay verifier B3 của Quang. Benchmark chính thức và báo cáo nhóm làm sau khi đủ 4 shape vào nhánh.
- Sau khi nhóm nhận `student_drop.zip`, nhóm trưởng chạy self-check không nhãn theo hướng dẫn repo; dữ liệu gốc không được đưa vào repo.

## 3. Đóng góp cụ thể

Commit trên nhánh `nhai`, theo thứ tự thời gian:

| Commit | Nội dung |
| --- | --- |
| `d910497` | Điền research card R4: nguồn, claim, boundary, giả thuyết và điều kiện bác bỏ, trước khi có số đo |
| `4241ad2` | `bonus/swarm_no_draft.py` (nhánh tắt draft và nhánh đối chứng) và `tests/test_research_ablation.py` |
| `f8e6c92` | `bonus/research_ablation.py`, `reports/research_ablation.json`, điền kết quả vào research card |
| `43d808b` | `tests/test_team_safety.py`: kiểm an toàn ở mức shape cho 4 shape |
| `574cdee` | Bản nháp báo cáo nhóm từ bằng chứng hiện có |
| `cc05d4c` | Gộp `main` (có workflow) vào `nhai`, xử lý xung đột ở `group_report.md` và `research_card.md` |
| `06e51d4` | `reports/benchmark.json` và `reports/crash.json` chính thức trên bản đủ 4 shape; cập nhật báo cáo nhóm |

Test đã thêm:

- `src/tests/test_research_ablation.py` — 143 ca: nhánh đối chứng trùng swarm gốc (70), tắt draft chỉ đổi usage của model (70), điểm yếu seed 55 còn nguyên (1), run id và trace riêng của từng nhánh (2).
- `src/tests/test_team_safety.py` — 196 ca trên 4 shape: rò rỉ secret/PII trong trace, kết quả và stdout (112), approval hỏng không được trả tiền (32), crash ở cả 3 điểm rồi chạy lại (12), tái lập (40).

Quyết định kỹ thuật:

- **Nhánh đối chứng cho ablation.** Không được sửa swarm gốc nên biến thể là một bản chép. Để chứng minh bản chép không lệch, bản chép có cờ `draft` và nhánh bật draft phải trùng swarm gốc trên mọi cặp (claim, seed). Nhờ đó khác biệt giữa hai nhánh của bản chép chỉ do một biến.
- **Không thêm event trace vào biến thể.** Metric `steps` đếm số event, nên thêm event sẽ thành biến thứ hai.
- **Giả thuyết commit trước số đo.** Research card ghi cả ngưỡng bác bỏ (có cặp nào đổi quyết định, hoặc cost/success giảm quá 10%) trong commit `d910497`, trước commit chứa JSON.
- **Danh sách cấm rộng hơn nhãn public.** Nhãn public chỉ liệt kê PII cho T05 và T10; test rò rỉ quét secret của mọi claim và SĐT, địa chỉ, tên hàng, ghi chú nội bộ của mọi order (57 chuỗi).
- **Test đi qua `run_claim`.** Test host có sẵn gọi thẳng `issue_refund`; test an toàn của nhóm đi qua đúng đường grader chấm, và bỏ qua shape còn là stub để cổng host luôn xanh trong lúc các shape chưa bàn giao.
- **Xử lý xung đột khi gộp.** Giữ nội dung của người phụ trách file; lấy thêm từ bản trên `main` dòng lớp L3B, link danh sách PR và dòng người phụ trách.

## 4. Bằng chứng

- Ablation R4: `python -m bonus.research_ablation --out reports/research_ablation.json` → nhánh đối chứng trùng swarm gốc 70/70 cặp; tắt draft không đổi quyết định ở cặp nào; pass rate 0.986, pass^5 0.929, variance 0.000816 ở cả ba nhánh; model calls 3.0 → 2.0; cost/success 49.57 → 48.62 VND (giảm 1,9%, dự đoán 2%). Chạy lại hai lần cho file giống hệt.
- Run id cùng một trial ở ba nhánh: `R-swarm-C-001-s11`, `R-swarm_draft_control-C-001-s11`, `R-swarm_no_draft-C-001-s11`.
- Benchmark chính thức: `src/reports/benchmark.json`, 4 shape × 14 claim × 5 seed; workflow, single, orchestrator 70/70; swarm 69/70 (fail `C-002` seed 55). Chạy lại hai lần cho file giống hệt.
- Crash suite: `src/reports/crash.json` → `crash_safety 20/20`.
- `python -m pytest -q` trên bản đủ 4 shape → 425 passed, không fail, không skip.
- `python -m pytest -q -m student -o addopts=` → 248 passed.
- `python -m lab8.check_submission` → `0 FAIL`; ADR đã được điền. Cổng được chạy lại sau khi commit để xác nhận working tree sạch.
- Nhóm trưởng chạy self-check không nhãn; `src/reports/hidden_selfcheck.json` ghi 40 claim × 5 seed trên workflow, single và orchestrator. Mỗi shape có 200 trial, không có status `error`, lỗi trace contract hay `leak_suspect`. Bộ này không có nhãn, nên không tính pass rate và không thay thế kết quả grader của giảng viên.
- Nguồn nghiên cứu: https://aclanthology.org/2026.emnlp-main.798/ (EMNLP 2026, trang 18527–18562, Outstanding Paper Award).

## 5. Công cụ AI đã dùng

- Công cụ: Claude Code (trợ lý lập trình của Anthropic) trong VS Code.
- Dùng vào việc gì:
  - Đọc đề bài, contract và code host, giải thích phần việc của tôi theo `TEAM.md`.
  - Soạn code `swarm_no_draft.py`, `research_ablation.py`, hai file test, và bản nháp nội dung research card và báo cáo nhóm. Phần lớn code và câu chữ trong các file này do AI soạn theo yêu cầu của tôi.
  - Phân tích hai file bị xung đột khi gộp `main` và đề xuất giữ phần nào.
- Tôi đã tự kiểm tra thế nào:
  - Nguồn nghiên cứu: Tôi tìm kiếm và mở trang arXiv và trang ACL Anthology của bài, đối chiếu tên bài, tác giả, số trang, DOI và dòng Outstanding Paper Award. Số slide trong tài liệu lab không khớp bộ slide bản v3, nên tôi tìm đúng trang theo nội dung.
  - Code và số liệu: mọi con số trong research card và báo cáo nhóm lấy từ file JSON do script sinh, không chép từ câu trả lời của AI. Tôi chạy lại `pytest`, script ablation và benchmark; các file JSON chạy lại cho cùng nội dung.
  - Thứ tự giả thuyết và số đo: tôi commit research card trước khi viết code ablation.
  - Tôi tự commit, push và gộp nhánh; đọc lại diff trước mỗi commit.

## 6. Tự đánh giá

- Đạt: research card R4 có nguồn đã kiểm chứng và một ablation một biến chạy lại được; bộ test an toàn phủ ba điều kiện must-pass trên cả 4 shape; benchmark và crash chính thức đã sinh; báo cáo nhóm có số thật.
- Hạn chế:
  - Tôi dựa vào AI để viết code và câu chữ; phần tôi tự làm chủ yếu là kiểm chứng nguồn, chạy lại, đọc kết quả và quyết định giữ gì.
  - Hai file test của tôi làm cổng host chậm từ khoảng 9 giây lên khoảng 45 giây.
  - Số đếm "refund thiếu approval" trong JSON ablation là suy ra từ lý do fail của evaluator, vì evaluator public không xuất bộ đếm bypass riêng.
  - Self-check hidden không nhãn chỉ kiểm tra khả năng chạy, trace và dấu hiệu lộ secret; chưa có kết quả hidden chính thức.
- Điều rút ra: muốn nói một chênh lệch là do kiến trúc thì phải có nhánh đối chứng và chỉ đổi một biến. Trong lab này bước draft không đi vào quyết định, và với bảng giá mô phỏng thì cost chủ yếu do số tool call, nên so cost giữa các shape phải báo kèm số model call và tool call.
