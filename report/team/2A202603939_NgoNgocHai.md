# Báo cáo cá nhân — Ngô Ngọc Hải

## 1. Thông tin thành viên

- Họ tên: Ngô Ngọc Hải
- MSSV: 2A202603939
- Email: 26ai.hainn2@vinuni.edu.vn
- GitHub: NgoHai0804

## 2. Phần việc phụ trách

Phân công dự kiến; chưa phải kết quả đã hoàn thành.

- Vai trò: orchestrator, handoff và test riêng.
- Phụ trách `src/lab8/shapes/orchestrator.py`, `src/tests/test_team_orchestrator.py`.
- Bắt đầu ngay bằng make_handoff, runtime investigator và fixture public có sẵn; không phụ thuộc hai shape còn lại hay bonus.
- Investigator chỉ đọc dữ liệu qua tool được cho phép; orchestrator lấy quote và gọi host với quote đầy đủ. Trace chỉ ghi handoff/dữ kiện an toàn; truyền crash_at.
- Bàn giao: 62 test student của orchestrator xanh; test mới kiểm handoff allowlist, worker read-only và không rò secret. Cung cấp mô tả shape C cho báo cáo nhóm.

## 3. Đóng góp cụ thể

- Commit trên nhánh `hai`: `f55ab7b` (shape C orchestrator), `8db0d9a` (test riêng).
- Test đã thêm: `src/tests/test_team_orchestrator.py` — 19 test (happy path, quote=0, needs_info, escalated, host-denied, T14, T11, T12, handoff allowlist, worker read-only, trace contract, unknown claim).
- Quyết định kỹ thuật:
  - Handoff allowlist: `make_handoff` chỉ giữ field trong `ALLOWED_FIELDS`, `facts` lọc theo `FACT_KEYS`; trace chỉ ghi `safe_dump(handoff)`, không ghi claim/order row thô hay `parent_secret`.
  - Investigator read-only: `allowed_tools` chỉ 3 tool đọc (`lookup_order`, `lookup_policy`, `compute_compensation`), `compute_compensation` sau `lookup_order`; `dispatch(worker=True)` chặn mọi tool ghi.
  - Truyền **quote đầy đủ** từ `compute_compensation` vào `durability.issue_refund`; host tự cap theo đơn (T14: proposal 150000, ledger 120000).
  - Crash: truyền `crash_at`, chỉ ghi trace rồi re-raise `InjectedCrash` (không nuốt), retry dựa vào ledger nên vẫn một refund.

## 4. Bằng chứng

- Commit: `f55ab7b`, `8db0d9a` trên nhánh `hai`.
- Test riêng: `python -m pytest -q tests/test_team_orchestrator.py` → 19 passed.
- `python -m pytest -q -m student -o addopts= -k orchestrator` → 62 passed.
- `python -m pytest -q` → 73 passed (không failed).
- `python -m lab8.crash_test --count 20 --out reports/crash.json` → `crash_safety 20/20`.
- Run id mẫu: `R-orchestrator-C-001-s11` (resolved, proposal 35000), `R-orchestrator-C-014-s11` (resolved, proposal 150000).
- Quét an toàn: 75 lượt chạy (15 claim × 5 seed) với 74 token cấm (canary, PII, header) → 0 rò rỉ; trace hợp lệ 75/75.

## 5. Công cụ AI đã dùng

- Công cụ: Kilo Code (model `tokenharbor/deepseek-v4.1-flash:free`), dùng để soạn shape C theo hướng dẫn mục 4, viết test riêng, và rà checklist.
- Tự kiểm: chạy lại `-k orchestrator` (62 passed), `pytest -q` (73 passed), CLI C-001/C-014 và crash+resume C-012, `crash_test` 20/20; đọc lại từng dòng code và giải thích được vì sao truyền quote đầy đủ, vì sao không bắt `InjectedCrash`, vì sao handoff là allowlist trong code.

## 6. Tự đánh giá

- Đạt mục tiêu: shape C đúng contract, 62/62 test student xanh, test riêng 19 test xanh, không rò secret.
- Hạn chế: bỏ Bước 9 tuỳ chọn (không thêm lời gọi MockLLM draft) nên `model_calls` = 0.
- Điều rút ra: trace là một phần ranh giới bảo mật; redaction phải là allowlist trong code, không thể nhờ model tóm tắt cho sạch.
