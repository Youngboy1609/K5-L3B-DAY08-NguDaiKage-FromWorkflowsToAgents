# Báo cáo nhóm — Lab 8 LogiX-VN

> **Trạng thái: bản chờ duyệt.** Số liệu mục 4 lấy từ các file trong `src/reports/`, sinh trên bản đã gộp đủ 4 shape (nhánh `nhai`, commit gộp `cc05d4c`). Các chỗ đánh dấu **[CHỜ]** chưa có bằng chứng. Giới hạn: tối đa 5 trang ngoài phụ lục.

## 1. Thông tin nhóm

- Tên nhóm: NguDaiKage.
- Lớp: L3B.
- Người viết và tổng hợp báo cáo: Trần Thị Nhài — 2A202603911.
- Người kiểm chứng và duyệt cuối: Hồ Trọng Nghĩa — 2A202603729.
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md).
- Repo: [K5-L3B-DAY08-NguDaiKage-FromWorkflowsToAgents](https://github.com/Youngboy1609/K5-L3B-DAY08-NguDaiKage-FromWorkflowsToAgents); [danh sách PR](https://github.com/Youngboy1609/K5-L3B-DAY08-NguDaiKage-FromWorkflowsToAgents/pulls).
- Commit chốt (trùng `report/team/decision_adr.md`): **[CHỜ]** Nghĩa chốt sau tích hợp.

## 2. Mục tiêu và cách tiếp cận

Bài toán là xử lý claim hoàn phí vận chuyển của LogiX-VN bằng bốn kiến trúc có cùng chữ ký `run_claim`, rồi chọn kiến trúc ít tự chủ nhất mà vẫn đúng nghiệp vụ và an toàn. Nhóm so sánh trên cùng 14 claim public, cùng 5 seed, cùng bảng giá mô phỏng và cùng evaluator; tiêu chí là độ đúng, độ ổn định qua seed, chi phí cho mỗi lần thành công và ba điều kiện must-pass.

Năm người làm song song từ host, runtime, swarm tham chiếu và fixture public có sẵn, mỗi người một nhánh, không sửa file của nhau:

| Thành viên | Phần việc |
| --- | --- |
| Hồ Trọng Nghĩa | Workflow; tích hợp; ADR; kiểm chứng và duyệt báo cáo nhóm |
| Nguyễn Đức Nhật | Single ReAct agent và test riêng |
| Ngô Ngọc Hải | Orchestrator, handoff và test riêng |
| Trần Thị Nhài | Test an toàn mức shape; research card R4 và ablation; benchmark/crash; viết báo cáo nhóm |
| Phạm Đăng Quang | Bonus B3: verifier, bộ claim đối kháng, test và báo cáo bonus |

Thứ tự vào `main`: orchestrator, bonus B3, single, rồi workflow. Nhài tổng hợp số liệu và phân tích thực nghiệm thành báo cáo, Nghĩa đối chiếu bằng chứng và duyệt cuối; mỗi chủ shape đọc lại phần mô tả giải pháp của mình.

## 3. Giải pháp

Cả ba shape nhóm viết chung một ranh giới: **code** đọc dữ liệu có cấu trúc, tính tiền bằng `compute_compensation` và gọi `durability.issue_refund` với quote đầy đủ; **host** kiểm approval, trần theo đơn và idempotency rồi mới ghi ledger. Model không chọn số tiền, không tạo approval và không ghi refund. Chữ trong ticket không được dùng làm mã đơn, số ngày trễ hay lệnh.

| Shape | Đọc gì, quyết định gì | Gọi host | Event trace |
| --- | --- | --- | --- |
| A · Workflow (Nghĩa) | Ba bước Python cố định: `get_claim_view` → `lookup_order` → `compute_compensation`. Không gọi model | Shape gọi `issue_refund` khi quote > 0 | `claim`, `order_scope`, `quote`, `host`, `decision` |
| B · Single (Nhật) | Vòng `run_react` tối đa 8 bước, `worker=True` nên chỉ gọi được tool đọc: `lookup_order` → `lookup_policy` → `lookup_refund_history` → `compute_compensation`. Mỗi bước có một lời gọi MockLLM để tính cost | Code của shape gọi `issue_refund` sau vòng lặp; chạm trần bước thì trả `failed` | `quote`, `decision`, `crash` |
| C · Orchestrator (Hải) | Dựng `handoff.v1` bằng `make_handoff` với `facts` rỗng và ba tool đọc; investigator chạy qua `run_readonly_investigators`. Không gọi model | Orchestrator lấy quote của investigator rồi gọi `issue_refund` | `handoff`, `investigator`, `quote`, `host_result`, `decision`, `crash` |
| D · Swarm (có sẵn) | Như C, thêm hai lời gọi peer/parse và một lời gọi draft. Ở seed chia hết cho 5, tin số ngày trễ ghi trong ticket | Swarm gọi `issue_refund` | `handoff`, `investigator`, `model_override`, `quote`, `crash` |

**Handoff.** Orchestrator chỉ chuyển các field trong allowlist của `lab8.handoff`; `parent_secret`, header và lịch sử không đi qua ranh giới, và trace ghi handoff đã sanitize.

**Trace.** Field cố ý không ghi: `parent_secret`, header, nội dung ticket, SĐT, địa chỉ, tên hàng, ghi chú nội bộ. Workflow chỉ ghi `visible` và `reason` của đơn, không ghi cả dòng order; single chỉ ghi số tiền và mã clause. Mọi nhánh return đều ghi trace qua `finish()`.

**Crash.** Ba shape truyền `crash_at` vào `issue_refund` và không nuốt `InjectedCrash`. Single và orchestrator ghi trace rồi ném lại; workflow để exception truyền thẳng ra.

## 4. Kết quả

### 4.1. Benchmark chính

Nguồn: `src/reports/benchmark.json`, sinh bằng lệnh chuẩn trong `src/reports/README.md` trên bản đã gộp đủ 4 shape. Chạy lại hai lần cho file giống hệt nhau.

14 claim public × 5 seed (`11,22,33,44,55`) = 70 trial mỗi shape, SQLite mới cho mỗi trial. Cost là VND mô phỏng; latency của MockLLM là `unavailable`.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND) | Mean / p95 steps | Mean model calls | Mean tool calls |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| workflow | 1.000 | 1.000 | 1.000–1.000 | 0 | 27.86 | 4.43 / 5 | 0.00 | 2.79 |
| single | 1.000 | 1.000 | 1.000–1.000 | 0 | 47.19 | 1.86 / 2 | 4.43 | 4.50 |
| orchestrator | 1.000 | 1.000 | 1.000–1.000 | 0 | 46.43 | 3.50 / 4 | 0.00 | 4.64 |
| swarm | 0.986 | 0.929 | 0.929–1.000 | 0.000816 | 49.57 | 2.80 / 3 | 3.00 | 4.66 |

Ba điều đọc được từ bảng:

- **Độ đúng không phân biệt được ba shape nhóm viết** trên bộ public: cả ba đạt 70/70. Swarm fail đúng một trial, `C-002` seed 55 (ticket ghi trễ 5 ngày, order ghi 2 ngày, swarm trả tiền thay vì từ chối).
- **Chi phí chủ yếu do số tool call quyết định.** Workflow rẻ nhất vì chỉ cần khoảng 2,8 tool call mỗi trial; single và orchestrator gọi thêm `lookup_policy` (single thêm cả `lookup_refund_history`). Single có hơn 4 lời gọi model mỗi trial nhưng cost chỉ nhỉnh hơn orchestrator 0,76 VND, vì theo bảng giá một tool call tốn 10 VND còn một lời gọi model chưa tới 1 VND.
- **Cột steps không so được giữa các shape.** Steps là số event trong trace, tức mức chi tiết mỗi người chọn ghi, không phải khối lượng công việc.

### 4.2. An toàn và bằng chứng

| Yêu cầu | Trạng thái | Bằng chứng |
| --- | --- | --- |
| Cổng host `python -m pytest -q` | Xanh: 425 passed, không fail, không skip | Chạy trên bản đã gộp đủ 4 shape |
| Ma trận student T01–T14 | 248/248 (4 shape × 62 test) | `python -m pytest -q -m student -o addopts=` trên bản đã gộp |
| Crash safety 20/20 | Đạt | `src/reports/crash.json`, sinh lại trên bản đã gộp, nội dung trùng bản đã commit |
| Crash ở mức shape | Cả 4 shape: cả 3 điểm crash, chạy lại đúng một refund và một audit | `src/tests/test_team_safety.py` |
| Không refund khi approval hỏng | Cả 4 shape: approval thiếu, bị thu hồi, hết hạn hoặc mượn của claim khác đều không ghi ledger, có audit `policy_denied` | `src/tests/test_team_safety.py` |
| Không rò secret/PII | Cả 4 shape: 14 claim × seed 11 và 55, quét trace, kết quả và stdout với secret của mọi claim và PII của mọi order | `src/tests/test_team_safety.py` |
| Tái lập | Cùng claim, cùng seed cho kết quả giống hệt; file ablation chạy lại hai lần giống nhau | `src/tests/test_team_safety.py`, `src/reports/research_ablation.json` |
| Hidden chính ≥ 0.75; gate bonus ≥ 0.80 | Chưa có kết quả chính thức | Grader của giảng viên |
| Tự kiểm hidden không nhãn | Chưa nhận `student_drop/` **[CHỜ]** | `src/reports/hidden_selfcheck.json` nếu có |

### 4.3. Quyết định kiến trúc, nghiên cứu và bonus

- **Shape được chọn:** Nghĩa chốt trong [decision_adr.md](decision_adr.md) **[CHỜ]**. Số liệu nghiêng về workflow: cùng pass rate và variance với single và orchestrator, cost/success thấp hơn khoảng 40%, và là shape ít tự chủ nhất.
- **Ablation R4** ([research_card.md](research_card.md), `src/reports/research_ablation.json`): tắt riêng bước draft trên swarm. Nhánh đối chứng trùng swarm gốc trên 70/70 cặp (claim, seed). Pass rate, pass^5 và variance không đổi; không cặp nào đổi quyết định; model calls giảm đúng 1 mỗi trial; cost/success giảm từ 49,57 xuống 48,62 VND (1,9%). Giả thuyết ghi trước khi đo được xác nhận. Hệ quả cho bảng 4.1: phần cost do các lời gọi model "trò chuyện" gây ra là nhỏ, nên chênh cost giữa các shape phản ánh số tool call chứ không phải mức độ đa tác tử.
- **Bonus B3** ([bonus_report.md](bonus_report.md), `src/reports/bonus_b3_*.json`): thêm verifier bằng code trước khi ghi tiền. Trên bộ public, `swarm_verified` đạt pass rate 1.000 (swarm 0.986); trên 8 claim đối kháng viết tay, 1.000 so với 0.800, với 8 lần verifier can thiệp. So sánh thêm với workflow **[CHỜ]** Quang bổ sung sau tích hợp.
- **Run id dẫn chứng:** `R-swarm-C-002-s55` (swarm trả sai vì tin ticket) so với `R-orchestrator-C-002-s55` và `R-single-C-002-s55` (từ chối đúng); `R-swarm_no_draft-C-001-s11` cho ablation.

## 5. Khó khăn và cách xử lý

| Sự cố thực tế | Bằng chứng | Cách xử lý | Kết quả |
| --- | --- | --- | --- |
| Số slide trong tài liệu lab không khớp bộ slide N8 bản v3 (ví dụ bài EMNLP ghi ở slide 44, 59 nhưng thực tế ở trang 58) | Đối chiếu `docs/bonus_topics.md`, `report/team/research_card.md` với file slide | Dò theo nội dung thay vì số trang; tải bài gốc từ ACL Anthology và đối chiếu abstract, số trang, giải thưởng | Research card ghi số trang thực tế và nguồn đã mở được |
| Hai nhánh cùng sửa `group_report.md` và `research_card.md` (nhánh `nhai` và nhánh workflow của Nghĩa) | `git diff origin/main...origin/feature/nghia-workflow-report-verification` | Khi gộp `main` vào `nhai`: giữ nội dung của người phụ trách file (Nhài), lấy thêm từ bản của Nghĩa dòng lớp L3B, link danh sách PR và dòng người phụ trách | Đã gộp, không còn xung đột |
| `src/reports/crash.json` được commit từ nhánh orchestrator, trong khi file thuộc phần benchmark | Commit `ca844d9` | Giữ file; Nhài sinh lại trên bản đã gộp | Nội dung trùng bản đã commit, vẫn 20/20 |
| Cổng host chậm dần khi thêm test tham số hóa (khoảng 9 giây lúc đầu, khoảng 45 giây khi đủ 4 shape) | Output `python -m pytest -q` | Chấp nhận, vì các test này phủ đúng ba điều kiện must-pass; nếu cần thì giảm số seed ở nhóm test rò rỉ | Vẫn xanh |

## 6. Tổng hợp đóng góp

Bằng chứng dưới đây lấy từ lịch sử git tại thời điểm viết; bảng chính thức nằm trong [TEAM.md](../../TEAM.md) do Nghĩa hoàn thiện, và mỗi người tự điền báo cáo cá nhân theo MSSV.

| Thành viên | Commit kỹ thuật | Test đã thêm |
| --- | --- | --- |
| Hồ Trọng Nghĩa | `6317f88` | `src/tests/test_team_workflow.py` |
| Nguyễn Đức Nhật | `7a193ce` | `src/tests/test_team_single.py` |
| Ngô Ngọc Hải | `f55ab7b`, `8db0d9a` | `src/tests/test_team_orchestrator.py` |
| Trần Thị Nhài | `4241ad2`, `f8e6c92`, `43d808b` | `src/tests/test_research_ablation.py`, `src/tests/test_team_safety.py` |
| Phạm Đăng Quang | `4b95632` | `src/tests/test_bonus_b3.py` |

## 7. Hạn chế và hướng cải thiện

- MockLLM là mô phỏng cố định theo seed, không đại diện cho model sản xuất. Cost không phải hóa đơn API; latency để `unavailable`.
- Bộ public chỉ có 14 claim và không phân biệt được ba shape nhóm viết về độ đúng. Kết quả public không thay thế đánh giá hidden.
- Vòng ReAct của single dùng một chính sách chọn tool viết bằng code, vì MockLLM không trả về lời gọi tool có cấu trúc. Với model thật, thứ tự và số bước có thể dao động, nên variance bằng 0 của single ở đây không dự báo được variance khi triển khai.
- Grader không chấm câu trả lời cho khách, nên các bước soạn chữ (như draft của swarm) không ảnh hưởng pass rate trong lab. Ngoài thực tế đó là thứ khách hàng đọc.
- Điều kiện khiến lựa chọn kiến trúc thay đổi: **[CHỜ]** đồng bộ với ADR. Gợi ý từ số liệu: nếu claim cần đọc nhiều nguồn độc lập hoặc đường đi không biết trước, phần cost thêm của single hoặc orchestrator mới đáng đổi.

## 8. Tài liệu tham khảo

- [Luật nghiệp vụ](../../docs/business_rules.md), [contract kết quả và trace](../../docs/contracts.md), [kiến trúc](../../docs/architecture.md), [định nghĩa metric](../../docs/metrics.md).
- Zhang và cộng sự (2026), *Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems*, EMNLP 2026, https://aclanthology.org/2026.emnlp-main.798/ — nguồn của research card R4.
- Google Research (2026), *Towards a Science of Scaling Agent Systems* — nguồn của bonus B3, chi tiết trong [bonus_report.md](bonus_report.md).
- Slide bài giảng AI20K N8 bản v3 (15/11/2026).
