# Bonus report: B3

> Khung báo cáo cho topic đã chọn; chưa có kết quả thực nghiệm. Khi hoàn thiện, giới hạn tối đa 2 trang.

- Người phụ trách: Phạm Đăng Quang — 2A202603760.
- Topic + nguồn (tên, năm, slide): B3 — Verifier/aggregator chống khuếch đại lỗi; tài liệu lab chỉ tới slide 17, 22, 42. Nguồn gốc và URL cần kiểm chứng trước khi trích dẫn.
- CLAIM của nguồn (1 câu):
- BOUNDARY (model / dataset / setup):
- HYPOTHESIS trên LogiX: verifier bằng code có thể giảm lỗi do swarm tin dữ kiện trong ticket; chi phí có thể tăng khi cần kiểm tra hoặc quote lại. Đây là giả thuyết, chưa phải kết quả.
- Biến cố định / biến thay đổi: khi so swarm và swarm_verified, giữ nguyên luồng nền, MockLLM, tool, seed, corpus, pricing và evaluator; chỉ thêm verifier với tối đa một vòng sửa. Workflow là baseline bổ sung.
- Lệnh tái lập (copy-paste được):
- File report + run id:

## Thiết kế thực nghiệm

Code dự kiến: `src/bonus/swarm_verified.py`; dữ liệu tự viết: `src/bonus/cases.jsonl`, `src/bonus/world.json`; script đo: `src/bonus/evaluate_b3.py`; test: `src/tests/test_bonus_b3.py`.

Verifier đối chiếu delay_days, status và damage_verified với order có cấu trúc trước bước ghi tiền. Nếu có sai lệch, tính quote lại bằng code, tối đa một vòng sửa và ghi event verifier_override. Giữ nguyên ranh giới approval, ownership, trần theo đơn và idempotency của host.

- Corpus: 14 claim public và ít nhất 8 claim đối kháng do nhóm tự viết. Nhãn đối kháng viết tay theo luật nghiệp vụ, không sinh bằng compensation.quote.
- Seed: `11,22,33,44,55`; SQLite mới cho mỗi trial.
- Biến thể đăng ký bằng `--extra-shape`; không sửa swarm tham chiếu hoặc registry chính.
- Điều kiện chạy bonus: shape chính qua 3 must-pass, hidden >= 0.80 và cổng host xanh; chưa xác nhận khi chưa có bằng chứng.

Lệnh public dự kiến, chạy trong `src/` sau khi module đã tồn tại; chưa phải lệnh đã chạy:

```text
python -m lab8.benchmark --shapes workflow,swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/bonus_b3_public.json
```

## Kết quả

Điền từ JSON do công cụ sinh; báo safety counts từ test/kiểm tra thực tế, không tự suy ra 0 từ pass rate.

| Corpus | Shape | Pass rate | Pass^5 | Variance | Cost/success | Số lần override |
| --- | --- | --- | --- | --- | --- | --- |
| Public | workflow | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Không áp dụng |
| Public | swarm | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Không áp dụng |
| Public | swarm_verified | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo |
| Đối kháng | workflow | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Không áp dụng |
| Đối kháng | swarm | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Không áp dụng |
| Đối kháng | swarm_verified | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo |

- Test mới và output thực tế (ít nhất 2 test):
- Approval bypass / secret leak / PII leak / lỗi trùng refund, theo corpus và shape:
- Trace minh họa: run id, dữ kiện lệch, verifier_override và effect thực tế; trace giữ local, không commit dữ liệu nhạy cảm:

## Kết luận

Chưa kết luận khi chưa có số liệu. Sau thực nghiệm, xác định hypothesis được ủng hộ, bị bác bỏ hoặc chưa đủ bằng chứng; đánh giá verifier có đưa swarm gần workflow không và chi phí đi kèm. Giải thích swarm còn đóng góp gì nếu verifier đã quyết định toàn bộ dữ kiện nghiệp vụ, cùng điều kiện khiến kết luận thay đổi.

## Giới hạn

MockLLM không phải model sản xuất; latency unavailable; chi phí mô phỏng; bộ đối kháng do nhóm thiết kế có thể thiên lệch. Kết quả public/tự viết không chứng minh gate hidden đã đạt.
