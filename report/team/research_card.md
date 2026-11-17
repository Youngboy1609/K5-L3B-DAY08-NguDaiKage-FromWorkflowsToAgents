# Research card

- Người phụ trách: Trần Thị Nhài — 2A202603911.
- Trạng thái: thiết kế ablation R4, chưa chạy. SOURCE/CLAIM/BOUNDARY để trống đến khi kiểm chứng nguồn gốc; kết quả điền sau từ JSON.

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
| CÂU | R1 / R2 / R3 / R4 | R4 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Dự đoán bỏ riêng bước draft làm giảm một model call ở mỗi trial có draft, pass rate chênh 0 điểm phần trăm và effect/approval/trace contract không đổi; mức giảm cost đo bằng usage thực tế. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Swarm tham chiếu so với swarm_no_draft; chỉ bật/tắt draft, giữ điểm yếu tham chiếu và logic còn lại. Cùng 14 claim public, seed 11/22/33/44/55, MockLLM, tool, pricing, evaluator; SQLite mới mỗi trial. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Kiểm cost/model calls bị thay đổi nhưng quyết định không đổi; đo pass rate, pass^5, variance, cost/success, model calls và safety counts. Không sửa lỗi seed 55 trong ablation này. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn):
- Run id / file report:
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu:
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).

## Bằng chứng dự kiến

- Module/script: `src/bonus/swarm_no_draft.py`, `src/bonus/research_ablation.py`.
- Test: `src/tests/test_research_ablation.py`.
- Kết quả: `src/reports/research_ablation.json`; chưa sinh.
- Thí nghiệm này độc lập với B3 của Quang; bàn giao số liệu và kết luận cho Nghĩa tổng hợp báo cáo nhóm.
