# Team

## Thông tin nhóm

- Tên nhóm: NguDaiKage
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY08-NguDaiKage-FromWorkflowsToAgents`
- URL repo: [K5-L3B-DAY08-NguDaiKage-FromWorkflowsToAgents](https://github.com/Youngboy1609/K5-L3B-DAY08-NguDaiKage-FromWorkflowsToAgents); [danh sách PR](https://github.com/Youngboy1609/K5-L3B-DAY08-NguDaiKage-FromWorkflowsToAgents/pulls)
- Nhánh nộp: `main`; commit chốt: chưa chốt, cập nhật sau khi hoàn thiện báo cáo nhóm.

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Hồ Trọng Nghĩa | 2A202603729 | 26ai.nghiaht@vinuni.edu.vn | Youngboy1609 | Nhóm trưởng; workflow; tích hợp; ADR và kiểm chứng báo cáo |
|   2 | Nguyễn Đức Nhật | 2A202603812 | 26ai.nhatnd@vinuni.edu.vn | NguyenDucNhat3006 | Single ReAct agent và test riêng |
|   3 | Ngô Ngọc Hải | 2A202603939 | 26ai.hainn2@vinuni.edu.vn | NgoHai0804 | Orchestrator, handoff và test riêng |
|   4 | Trần Thị Nhài | 2A202603911 | 26ai.nhaitt@vinuni.edu.vn | chanhochust | QA; ablation độc lập; benchmark, research card và viết báo cáo nhóm |
|   5 | Phạm Đăng Quang | 2A202603760 | 26ai.quangpd@vinuni.edu.vn | DanggQuangg | Bonus B3: swarm verifier, dữ liệu đối kháng và báo cáo bonus |

## Phân công và cách làm song song

Đây là kế hoạch công việc, chưa phải bằng chứng đã hoàn thành. Cả 5 người có thể bắt đầu từ host, swarm tham chiếu và fixture public có sẵn; không cần chờ code của thành viên khác. Bước tích hợp, benchmark đủ 4 shape và chốt báo cáo thực hiện sau khi nhận các phần bàn giao.

### File mỗi người phụ trách

Đường dẫn tính từ gốc repo. Các file test và code mở rộng dưới đây là file dự kiến tạo mới.

| Người | File được phụ trách | Công việc bắt đầu ngay | Điều kiện bàn giao |
| --- | --- | --- | --- |
| Nghĩa | `src/lab8/shapes/workflow.py`; `src/tests/test_team_workflow.py`; `TEAM.md`; `report/team/decision_adr.md` | Viết workflow cố định từ contract và host có sẵn; thêm test nghiệp vụ, retry và crash | 62 test student của workflow xanh; test mới xanh; sau tích hợp chốt ADR và kiểm chứng báo cáo bằng số đo thật |
| Nhật | `src/lab8/shapes/single.py`; `src/tests/test_team_single.py` | Viết ReAct bằng runtime có sẵn, tối đa 8 bước; model chỉ chọn tool đọc; host ghi tiền | 62 test student của single xanh; test mới kiểm giới hạn bước, tool ghi và trace |
| Hải | `src/lab8/shapes/orchestrator.py`; `src/tests/test_team_orchestrator.py` | Dùng handoff và investigator runtime có sẵn; orchestrator tính quote/gọi host | 62 test student của orchestrator xanh; test mới kiểm handoff, read-only và không rò secret |
| Nhài | `src/tests/test_team_safety.py`; `src/tests/test_research_ablation.py`; `src/bonus/swarm_no_draft.py`; `src/bonus/research_ablation.py`; `src/reports/research_ablation.json`; `src/reports/benchmark.json`; `src/reports/crash.json`; `src/reports/hidden_selfcheck.json` nếu có; `report/team/research_card.md`; `report/team/group_report.md` | Viết test host/swarm an toàn; làm ablation R4 bật/tắt riêng bước draft trên swarm có sẵn, giữ các phần khác cố định; viết báo cáo nhóm từ số liệu thực tế | Test và ablation chạy độc lập với 3 shape mới/B3; nguồn nghiên cứu đã kiểm chứng; JSON do script sinh; sau tích hợp chạy lại test an toàn trên đủ 4 shape và sinh report chính |
| Quang | `src/bonus/__init__.py`; `src/bonus/swarm_verified.py`; `src/bonus/cases.jsonl`; `src/bonus/world.json`; `src/bonus/evaluate_b3.py`; `src/tests/test_bonus_b3.py`; `src/reports/bonus_b3_*.json`; `report/team/bonus_report.md` | Làm B3 từ swarm tham chiếu; verifier bằng code; ít nhất 8 claim đối kháng với nhãn viết tay; đo swarm và swarm_verified ngay | Ít nhất 2 test mới; tối đa 1 vòng sửa; event verifier_override; metric/safety counts và số lần override; thêm workflow vào so sánh cuối khi tích hợp |

Mỗi người tự cập nhật báo cáo cá nhân mang MSSV của mình. Nhài có thể làm toàn bộ ablation trên swarm hiện hữu, không phụ thuộc verifier của Quang. Quang không cần workflow mới để phát triển và kiểm thử B3; so sánh đủ workflow/swarm/swarm_verified là bước nghiệm thu cuối.

### Contract chung và ranh giới chỉnh sửa

- Ba shape và biến thể bonus giữ chữ ký `run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult`. Biến thể có tên shape/run_id riêng và đăng ký bằng `--extra-shape`, không sửa registry chính.
- Tiền do `compute_compensation` tính; truyền quote đầy đủ vào `durability.issue_refund`. Host xử lý approval, trần theo đơn và idempotency. Truyền `crash_at`, để `InjectedCrash` truyền ra.
- Dùng trace đúng contract ở mọi nhánh; không ghi secret/PII hoặc raw claim/order vào trace, log, stdout. Investigator chỉ có tool đọc.
- Không sửa `metrics.py`, `durability.py`, `policy.py`, `src/config/`, `src/data/`, swarm tham chiếu, registry hay CI. Test mới nằm trong file riêng được phân công. Nhãn đối kháng viết tay theo luật, không sinh bằng chính hàm quote.
- Quang tạo `src/bonus/__init__.py` rỗng; Nhài vẫn phát triển module ablation độc lập, không cần import module của Quang. Không sửa file nhau; lỗi ở shape nào gửi chủ file đó xử lý. Nghĩa tích hợp các phần đã bàn giao.
- Mỗi người chạy trong checkout riêng, dùng test database tạm và không commit trace/SQLite. Nhài sinh report chính trên bản đã tích hợp; Quang sinh `bonus_b3_*.json`; JSON kết quả không sửa tay.
- Mỗi người có commit kỹ thuật và ít nhất một test thêm/sửa. Chỉ điền bảng đóng góp bên dưới bằng commit/test thực tế sau khi làm.

### Nghiệm thu và nộp bài

- Mọi lệnh lab chạy từ `src/`. Từng chủ shape chạy `python -m pytest -q -m student -o addopts= -k <shape>` và test riêng trước khi bàn giao.
- Sau tích hợp: smoke; `python -m pytest -q`; toàn bộ ma trận student; benchmark 4 shape trên 14 claim public với seed `11,22,33,44,55`; crash suite `20/20`; test/benchmark B3; ablation; hidden self-check khi được phát dữ liệu.
- CI xanh không thay thế ma trận student đầy đủ: CI hiện chỉ benchmark và chạy student matrix cho swarm. Crash suite host không thay thế test retry/crash riêng của từng shape.
- Nghĩa chốt ADR và kiểm chứng báo cáo; Nhài viết báo cáo nhóm tối đa 5 trang ngoài phụ lục, bàn giao số liệu benchmark/crash và research card; Quang hoàn thiện báo cáo B3 tối đa 2 trang. Mỗi người điền báo cáo cá nhân. `check_submission` cần `0 FAIL`; cả 5 người tự nộp cùng link repo trên LMS.
- Bonus chốt B3, tối đa +10: shape chính phải qua 3 must-pass, hidden pass rate >= 0.80 và cổng host xanh; phần chính yêu cầu hidden >= 0.75. Tự kiểm hidden không nhãn không xác nhận được pass rate chính thức.

## Bảng đóng góp

Nhài là người viết group report; Nghĩa đối chiếu bằng chứng và duyệt cuối.

`python -m lab8.check_submission` đọc bảng này bằng máy: giữ nguyên tiêu đề `## Bảng đóng góp` và các cột. Mỗi người một dòng: commit có nội dung và ít nhất một test đã thêm hoặc sửa.

| Người | Vai | Commit | Test đã thêm hoặc sửa |
| --- | --- | --- | --- |
| Hồ Trọng Nghĩa (2A202603729) | Workflow + regression tests | `6317f88` | `tests/test_team_workflow.py` (6 cases) |

## Cá nhân

Mỗi thành viên đồng thời tạo một báo cáo riêng trong `report/` theo dạng:

```text
report/team/MSSV_HoTen.md
```

Ví dụ: `report/team/20241234_NguyenVanAn.md`.

Sao chép mục dưới đây cho từng thành viên.

## MSSV_HoTen

### Phần việc phụ trách

-

### Đóng góp cụ thể

-

### Bằng chứng

-
