# Báo cáo nhóm — Lab 8 LogiX-VN

> Khung báo cáo đang chuẩn bị; các phần giải pháp dưới đây mô tả kế hoạch, chưa xác nhận triển khai hoặc kết quả kiểm thử. Giới hạn: tối đa 5 trang ngoài phụ lục khi hoàn thiện.

## 1. Thông tin nhóm

- Tên nhóm:
- Người viết và tổng hợp báo cáo: Trần Thị Nhài — 2A202603911.
- Người kiểm chứng và duyệt cuối: Hồ Trọng Nghĩa — 2A202603729.
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md).
- Repo: [K5-L3B-DAY08-NguDaiKage-FromWorkflowsToAgents](https://github.com/Youngboy1609/K5-L3B-DAY08-NguDaiKage-FromWorkflowsToAgents).
- Commit chốt (trùng decision_adr.md):

## 2. Mục tiêu và cách tiếp cận

Nhóm dự kiến triển khai ba kiến trúc workflow, single ReAct và orchestrator để so sánh với swarm tham chiếu trên cùng bài toán hoàn phí của LogiX-VN. Mục tiêu là lựa chọn kiến trúc ít tự chủ nhất nhưng đáp ứng yêu cầu nghiệp vụ và an toàn, dựa trên độ đúng, độ ổn định qua seed và chi phí mô phỏng.

| Thành viên | Phần việc được giao |
| --- | --- |
| Hồ Trọng Nghĩa | Workflow; tích hợp; ADR; kiểm chứng và duyệt báo cáo nhóm |
| Nguyễn Đức Nhật | Single ReAct agent và test riêng |
| Ngô Ngọc Hải | Orchestrator, handoff và test riêng |
| Trần Thị Nhài | QA; benchmark/crash; research card R4 và ablation; viết báo cáo nhóm |
| Phạm Đăng Quang | Bonus B3: verifier, dữ liệu đối kháng, test và báo cáo bonus |

Các phần được phát triển từ host, runtime, swarm tham chiếu và fixture public có sẵn. Nhài tổng hợp số liệu và phân tích thực nghiệm thành báo cáo, Nghĩa đối chiếu bằng chứng và duyệt cuối; mỗi chủ shape cung cấp mô tả giải pháp và bằng chứng riêng.

## 3. Giải pháp

Bảng sau là thiết kế dự kiến; cập nhật theo code thực tế trước khi nộp.

| Shape | Luồng xử lý dự kiến | Người phụ trách |
| --- | --- | --- |
| Workflow | Các bước đọc claim/order, tính quote và gọi host được cố định bằng Python | Nghĩa |
| Single | Vòng ReAct tối đa 8 bước, chỉ gọi tool đọc; code tính quote và gọi host sau vòng lặp | Nhật |
| Orchestrator | Chuyển handoff qua allowlist cho investigator chỉ đọc; orchestrator gọi host | Hải |
| Swarm | Baseline có sẵn; giữ điểm yếu tham chiếu để đối chứng qua seed | Repo cung cấp |

Ranh giới cần kiểm chứng: số tiền do compute_compensation tính từ order và policy hiện hành; host kiểm approval, trần theo đơn và idempotency. Shape truyền quote đầy đủ, kể cả khi đơn đã nhận refund trước đó. Model không tạo approval hoặc ghi refund.

Handoff và trace chỉ chứa dữ kiện được phép. Không chuyển hoặc ghi parent_secret, header, số điện thoại, địa chỉ, ghi chú nội bộ hay tên hàng. Truyền crash_at xuống host và để InjectedCrash truyền ra để test được cửa sổ crash thực tế.

- Khác biệt giữa thiết kế và code sau tích hợp:
- Event trace thực tế và field cố ý loại bỏ:
- Bằng chứng retry/crash, approval và trần theo đơn:

## 4. Kết quả

### 4.1. Benchmark chính

Nguồn sẽ lấy từ `src/reports/benchmark.json`: đủ 4 shape, toàn bộ 14 claim public, seed `11,22,33,44,55`, SQLite mới cho mỗi trial. Chi phí là VND mô phỏng; latency của MockLLM là unavailable.

| Shape | Pass rate | Pass^5 | Seed min–max | Variance | Cost/success (VND mô phỏng) | Mean/p95 steps |
| --- | --- | --- | --- | --- | --- | --- |
| workflow | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo |
| single | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo |
| orchestrator | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo |
| swarm | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo | Chưa đo |

### 4.2. An toàn và bằng chứng

| Yêu cầu | Trạng thái | Bằng chứng cần bổ sung |
| --- | --- | --- |
| Cổng host và ma trận student của cả 4 shape | Chưa chạy cho bài nhóm | Lệnh, output thực tế và commit được kiểm |
| Crash safety 20/20 | Chưa đo | `src/reports/crash.json`; test T11/T12 riêng từng shape |
| Không bypass approval; không rò secret/PII | Chưa xác nhận | Test, kiểm tra trace/stdout; kết quả grader khi có |
| Hidden chính >= 0.75; gate bonus >= 0.80 | Chưa có kết quả chính thức | Grader của giảng viên; không commit hidden_grade.json |
| Tự kiểm hidden không nhãn | Chưa có dữ liệu được phát | `src/reports/hidden_selfcheck.json` nếu có; không suy ra pass rate |

### 4.3. Quyết định kiến trúc, nghiên cứu và bonus

- Shape được chọn và lý do: bổ sung sau benchmark; xem [decision_adr.md](decision_adr.md).
- Ablation R4 bật/tắt bước draft: Nhài bổ sung kết quả tại [research_card.md](research_card.md).
- Bonus B3 so sánh swarm, swarm_verified và workflow: Quang bổ sung tại [bonus_report.md](bonus_report.md).
- Run id và ví dụ trial giải thích khác biệt:

## 5. Khó khăn và cách xử lý

Chỉ ghi sự cố đã thực sự gặp trong quá trình làm bài.

| Sự cố thực tế | Lệnh/output/commit liên quan | Cách xử lý | Kết quả kiểm tra lại |
| --- | --- | --- | --- |
| Chưa ghi nhận trong khung báo cáo | | | |

## 6. Tổng hợp đóng góp

Bảng ở mục 2 thể hiện phân công. Đóng góp đã hoàn thành phải đối chiếu bảng đóng góp trong [TEAM.md](../../TEAM.md), commit kỹ thuật và test thực tế của từng thành viên. Mỗi người tự điền báo cáo cá nhân theo MSSV; không dùng phân công làm bằng chứng hoàn thành.

## 7. Hạn chế và hướng cải thiện

MockLLM là mô phỏng cố định theo seed, không đại diện cho model sản xuất. Cost không phải hóa đơn API và latency để unavailable. Kết quả public không thay thế đánh giá hidden. Chỉ kết luận trong phạm vi corpus, seed và evaluator đã chạy.

- Hạn chế khác ghi nhận sau thực nghiệm:
- Điều kiện khiến lựa chọn kiến trúc thay đổi:

## 8. Tài liệu tham khảo

- [Luật nghiệp vụ](../../docs/business_rules.md).
- [Contract kết quả và trace](../../docs/contracts.md).
- [Kiến trúc](../../docs/architecture.md) và [định nghĩa metric](../../docs/metrics.md).
- Nguồn nghiên cứu ngoài repo: bổ sung nguồn gốc đã đọc, URL và phạm vi sử dụng, đồng bộ research_card.md và bonus_report.md.
