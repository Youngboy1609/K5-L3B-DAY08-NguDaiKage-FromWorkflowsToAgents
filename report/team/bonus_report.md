# Bonus report: B3

- Topic + nguồn (tên, năm, slide): B3 — Verifier/aggregator chống khuếch đại lỗi; Google Research 2026, *Towards a Science of Scaling Agent Systems* (Slide 17: Evaluator–optimizer, Slide 22: Reflection, Slide 42: Error amplification).
- CLAIM của nguồn (1 câu): Các agent độc lập khuếch đại lỗi lên tới 17.2×, trong khi cơ chế kiểm định/tổng hợp tập trung (evaluator/verifier) giảm hệ số khuếch đại lỗi xuống còn 4.4×.
- BOUNDARY (model / dataset / setup): Đánh giá trên bài toán claims flow LogiX-VN với 14 claim public và 8 claim đối kháng viết tay; môi trường MockLLM chạy offline không đo latency thực tế.
- HYPOTHESIS trên LogiX: Bổ sung bước verifier bằng code trước khi gọi `issue_refund` nhằm đối chiếu các dữ kiện nhạy cảm (`delay_days`, `status`, `damage_verified`) với dữ liệu đơn hàng có cấu trúc sẽ triệt tiêu hoàn toàn lỗi suy diễn/đối kháng từ ticket (đưa pass rate về 100%, pass^5 = 1.0, seed variance = 0) với overhead chi phí công cụ tăng không đáng kể.
- Biến cố định / biến thay đổi:
  - Biến cố định: Host durability, cơ chế approval, pricing giả lập, 5 seed (`11, 22, 33, 44, 55`), 14 public claims, 8 adversarial claims.
  - Biến thay đổi: Kiến trúc swarm nguyên bản (`swarm`) vs Swarm có bước Verifier đối chiếu DB bằng code (`swarm_verified`).
- Lệnh tái lập (copy-paste được):
  `python -m bonus.evaluate_b3`
  hoặc:
  `python -m lab8.benchmark --shapes swarm,swarm_verified --extra-shape swarm_verified=bonus.swarm_verified:run_claim --cases bonus/cases.jsonl --world bonus/world.json --seeds 11,22,33,44,55 --out reports/bonus_b3_benchmark.json`
- File report + run id:
  - File report: `src/reports/bonus_b3_summary.json`, `src/reports/bonus_b3_adversarial.json`, `src/reports/bonus_b3_public.json`.
  - Sample Run ID có can thiệp: `R-swarm_verified-ADV-001-s55`.

## Kết quả

Số liệu đo lường trực tiếp từ bộ benchmark tự động trên 5 seed (`11, 22, 33, 44, 55`):

### 1. Trên tập Adversarial Cases (8 claims × 5 seeds = 40 trials)

| Kiến trúc | Pass rate | Pass^5 | Seed Variance | Min | Max | Cost/Success (VND) | Mean Steps | Số lần Override |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `swarm` | 0.800 | 0.000 | 0.160000 | 0.000 | 1.000 | 67.98 | 3.20 | 0 |
| `swarm_verified` | **1.000** | **1.000** | **0.000000** | **1.000** | **1.000** | **56.38** | 3.40 | **8** |

*Lỗi thường gặp của `swarm`: `status resolved != denied` (5 lần) và `status denied != resolved` (3 lần) tại seed 55 do tin vào số ngày trễ ghi trong ticket người dùng thay vì dữ liệu DB.*

### 2. Trên tập Public Claims (14 claims × 5 seeds = 70 trials)

| Kiến trúc | Pass rate | Pass^5 | Seed Variance | Min | Max | Cost/Success (VND) | Mean Steps |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `swarm` | 0.986 | 0.929 | 0.000816 | 0.929 | 1.000 | 49.57 | 2.80 |
| `swarm_verified` | **1.000** | **1.000** | **0.000000** | **1.000** | **1.000** | **49.00** | 2.81 |

### 3. Minh họa can thiệp của Verifier (Trace Event)
Tại trial `R-swarm_verified-ADV-001-s55` (Đơn O-ADV-001 thực tế trễ 2 ngày, khách nói quá trễ 6 ngày):
```json
{
  "kind": "verifier_override",
  "payload": {
    "discrepancies": {
      "delay_days": {
        "used_by_model": 6,
        "structured_db": 2
      }
    },
    "corrected_quote": 0,
    "recomputed_from": "structured_order"
  }
}
```
Verifier đã phát hiện sự sai lệch giữa dữ kiện mô hình tin theo ticket (`6`) và dữ liệu thực trong cơ sở dữ liệu (`2`), tự động tính lại quote về `0 VND` và từ chối yêu cầu hoàn tiền, ngăn chặn thất thoát cho hệ thống.

## Kết luận

- **Ủng hộ giả thuyết (Support Hypothesis):** Kết quả thực nghiệm hoàn toàn ủng hộ claim của Google Research 2026. Một bước verifier bằng code có thể khôi phục 100% độ chính xác (`pass^5` tăng từ 0.0 lên 1.0 trên tập đối kháng, và từ 0.929 lên 1.0 trên tập public), triệt tiêu hoàn toàn phương sai giữa các seed (`seed_variance = 0`).
- **Hiệu quả kinh tế:** Chi phí trên mỗi ca thành công (`cost_per_success_vnd`) của `swarm_verified` thậm chí **thấp hơn** `swarm` (56.38 VND so với 67.98 VND trên tập đối kháng) do không bị lãng phí chi phí gọi host/refund vào các trial thất bại.
- **Giá trị còn lại của Swarm:** Nếu Verifier đã đối chiếu toàn bộ dữ kiện đơn hàng, Swarm chủ yếu chỉ còn giá trị trong việc trích xuất thực thể phi cấu trúc ban đầu hoặc sinh câu trả lời tự nhiên. Quyết định nghiệp vụ cốt lõi và ghi sổ bắt buộc phải do code/verifier bảo vệ.
- **Điều kiện kết luận đảo ngược:** Khi dữ liệu DB không đủ tin cậy (DB lỗi thời, dữ liệu trễ không đồng bộ kịp thời thực tế) hoặc khi chi phí gọi thêm tool để verify vượt quá giá trị đơn hàng bồi thường, việc ép buộc code verifier ghi đè có thể dẫn đến từ chối sai (false negative).

## Giới hạn

- **MockLLM:** Mô hình LLM được mô phỏng có tính tiền định qua seed và hàm băm, chưa phản ánh đầy đủ tính bất định, hallucinations đa dạng hay khả năng prompt injection phức tạp của LLM thương mại lớn.
- **Mô phỏng Latency:** Môi trường không đo độ trễ mạng/thực thi (latency: unavailable); trên thực tế một vòng sửa (correction loop) sẽ làm tăng p95 latency.
- **Quy mô tập đối kháng:** Thử nghiệm trên 8 ca đối kháng điển hình; cần mở rộng ra hàng nghìn trường hợp corner cases và tấn công đa ngôn ngữ trong môi trường sản xuất thực.
