# Research card

- Người phụ trách: Trần Thị Nhài — 2A202603911.
- Trạng thái: đã hoàn thành. Nguồn đã kiểm chứng trên ACL Anthology; giả thuyết được commit (`d910497`) trước khi đo; kết quả lấy từ `src/reports/research_ablation.json`.

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R4 · Evaluation confounders (slide N8 bản v3: trang 58 và 68) |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | Zhang, Zhang, Lu và cộng sự, *Rethinking the Evaluation of Efficiency Methods for Multi-Agent Systems*, EMNLP 2026 (Outstanding Paper Award, ghi trên trang ACL Anthology của bài), trang 18527–18562, https://aclanthology.org/2026.emnlp-main.798/, DOI 10.18653/2026.emnlp-main.798; bản arXiv: https://arxiv.org/abs/2609.05933. Loại bằng chứng: benchmark chẩn đoán có kiểm soát trên 5 phương pháp cắt gọn MAS. Nhóm đã đọc bản PDF của kỷ yếu. |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Nhiều mức cải thiện hiệu quả được báo cáo cho MAS phụ thuộc vào setup đánh giá: khi giữ chung backbone, agent registry và runtime, một phần cải thiện đến từ những hệ khởi đầu mà cắt ngẫu nhiên đã giữ được accuracy, chứ không phải cải thiện bền vững về hiệu quả. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Bài chỉ xét nhóm phương pháp nhận một MAS có sẵn rồi tái cấu trúc (cắt agent hoặc cạnh giao tiếp); 4 nhóm task cộng phần mở rộng HotpotQA, toàn tiếng Anh; backbone mã nguồn mở cỡ nhỏ 4B–8B cố định theo nhóm task; cost là proxy đếm token. Tác giả ghi rõ đây là bằng chứng chẩn đoán cho các phương pháp và setting đã thử, không phải cho mọi triển khai MAS. Khác với lab: bài cắt topology trên LLM thật, còn nhóm cắt một lời gọi model trên MockLLM; nhóm mượn phương pháp so sánh, không tái lập kết quả của bài. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Tắt riêng bước draft trên swarm tham chiếu: pass rate, pass^5 và seed variance không đổi; mean model calls giảm đúng 1 mỗi trial; cost/success giảm khoảng 2% (ước tính trước khi đo: một lần draft khoảng 0,9 VND so với khoảng 50 VND tiền tool mỗi trial theo config/pricing.yaml). Giả thuyết bị bác bỏ nếu có bất kỳ cặp (claim, seed) nào đổi status hoặc proposal khi tắt draft, hoặc nếu cost/success giảm quá 10%. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ cố định: MockLLM, bộ tool, 14 claim public, seed 11,22,33,44,55, config/pricing.yaml, evaluator lab8.metrics, DB mới cho mỗi trial và toàn bộ logic swarm kể cả REFERENCE_WEAKNESS. Biến duy nhất được thay đổi: có gọi complete(purpose="draft") hay không. Ba nhánh chạy cùng lúc: swarm gốc, bản chép bật draft (control) và bản chép tắt draft. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Lỗi dự kiến: bản chép của swarm lệch khỏi bản gốc, khiến khác biệt không còn do draft. Cách đo: nhánh control phải trùng swarm gốc ở status, proposal, model calls, tool calls và cost trên mọi cặp (claim, seed). Metric so sánh giữa control và bản tắt draft: pass rate, pass^5, seed variance, cost/success, mean model calls; số trial lộ secret và số refund thiếu approval phải bằng 0 ở cả hai nhánh. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m bonus.research_ablation --out reports/research_ablation.json` (chạy trong `src/`; chạy lại hai lần cho file giống hệt nhau).
- Run id / file report: `src/reports/research_ablation.json`; 3 nhánh × 14 claim × 5 seed = 210 trial. Run id dẫn chứng cho cùng một trial ở ba nhánh: `R-swarm-C-001-s11`, `R-swarm_draft_control-C-001-s11`, `R-swarm_no_draft-C-001-s11`.
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: **đúng** trên bộ public, không điều kiện bác bỏ nào xảy ra.
  - Phép so sánh hợp lệ: nhánh control trùng swarm gốc trên 70/70 cặp (claim, seed) ở status, pass/fail, lý do, steps, model calls, tool calls và cost.
  - Pass rate 0.986, pass^5 0.929, seed variance 0.000816, seed min–max 0.929–1.000: giống nhau ở cả ba nhánh. Không cặp nào đổi quyết định khi tắt draft (0/70); trial fail duy nhất vẫn là `C-002` seed 55 (điểm yếu tham chiếu).
  - Mean model calls giảm từ 3.0 xuống 2.0, đúng 1 lời gọi ở 70/70 trial. Mean tool calls (4.66) và mean steps (2.80) không đổi.
  - Cost/success giảm từ 49.57 xuống 48.62 VND, tức 1,9% (dự đoán khoảng 2%, ngưỡng bác bỏ 10%). Mỗi trial bớt 0,92–0,94 VND.
  - Số trial lộ secret/PII và số trial refund thiếu approval: 0 ở cả ba nhánh.
  - Ý nghĩa cho R4: trong lab này bước draft không đi vào quyết định, nên chênh lệch cost do nó gây ra không nói lên gì về topology. Khi so cost/success giữa bốn shape phải báo kèm số model call và tool call của từng shape; với bảng giá hiện tại cost chủ yếu do số tool call quyết định.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`. Kết quả chỉ đúng cho 14 claim public và bảng giá mô phỏng trong `config/pricing.yaml`. Với model thật, câu draft là thứ khách hàng đọc, nên "draft không ảnh hưởng pass" chỉ đúng vì grader của lab không chấm câu chữ trả lời.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).

## Bằng chứng

- Module/script: `src/bonus/swarm_no_draft.py`, `src/bonus/research_ablation.py`.
- Test: `src/tests/test_research_ablation.py`.
- Kết quả: `src/reports/research_ablation.json`, do script sinh.
- Thí nghiệm này độc lập với B3 của Quang; số liệu và kết luận đã đưa vào mục 4.3 của báo cáo nhóm để Nghĩa kiểm chứng.
