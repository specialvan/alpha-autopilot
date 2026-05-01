# V7 Claude 璇勫楠屾敹鎻愪氦娓呭崟锛堢涓夊崄涓冭疆鐢熶骇鍖栵級
- 鏃ユ湡锛?026-05-01
- 鎻愪氦鐩爣锛氳瀵?V7 闃舵 `PR-AA-26~39` 绗笁鍗佷竷杞敓浜у寲澧炲己杩涜楠屾敹锛堟不鐞嗗崌绾т簨浠惰嚜鎰堣繍琛屽巻鍙插璁★級銆?
## 1. 闇€姹備笌璁″垝鏂囨。

1. `claude_review_package/v7/V7_MAOSHEN_NOVEL_REQUIREMENTS_REVIEW_AND_PRD.md`
2. `claude_review_package/v7/V7_DECISION_FEEDBACK_CONTROL_SYSTEM_PR.md`
3. `claude_review_package/v7/V7_DEVELOPMENT_PLAN_PR_2026_04_30.md`
4. `claude_review_package/v7/V7_PR_AA_26_39_EXECUTION_TASK_BOARD.md`

## 2. 浠ｇ爜鎻愪氦鑼冨洿

1. `backend/app/services/narrative_v7/schemas.py`
2. `backend/app/services/narrative_v7/benchmark_store.py`
3. `backend/app/services/narrative_v7/benchmark_library.py`
4. `backend/app/api/routes/narrative_v7.py`
5. `tests/test_narrative_v7_modules.py`
6. `tests/test_narrative_v7_api.py`

## 3. 绗笁鍗佷竷杞兘鍔涘寮?
1. 鏂板娌荤悊鍗囩骇浜嬩欢鑷剤杩愯鍘嗗彶钀界洏鑳藉姏锛坮emediation runs锛夈€?2. 鏂板鑷剤鍘嗗彶鏌ヨ API锛歚GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations`銆?3. 鍘嗗彶璁板綍杈撳嚭鍔ㄤ綔涓庢墽琛屽瓧娈碉細`action/executed/emitted/pruned`銆?4. 鍘嗗彶璁板綍杈撳嚭瀹¤瀛楁锛歚emitted_event_id/auto_prune_pruned_count/auto_prune_malformed_dropped_count`銆?5. 鏀寔 `limit/cursor` 鍒嗛〉娑堣垂骞惰緭鍑?`malformed_line_count`銆?
## 4. 娴嬭瘯娓呭崟

1. `tests/test_narrative_v7_modules.py`
2. `tests/test_narrative_v7_api.py`
3. 鎵ц鍛戒护锛歚pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q`
4. 缁撴灉锛歚96 passed`
5. 缂栬瘧妫€鏌ワ細`python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py`

## 5. 寤鸿璇勫閲嶇偣

1. 鑷剤鍘嗗彶鏄惁瀹屾暣瑕嗙洊 dry-run 涓?apply 涓ょ被鎵ц杞ㄨ抗銆?2. 鍘嗗彶鍒嗛〉涓庢帓搴忓彛寰勬槸鍚︾ǔ瀹氬彲澶嶇幇銆?3. 鍘嗗彶瀛楁鏄惁鍙洖鏀惧叧閿墽琛岀粨鏋滐紙emit/prune锛夈€?4. 鍘嗗彶璁℃暟涓庡疄鏃舵墽琛岀粨鏋滐紙auto-remediate response锛夋槸鍚︿竴鑷淬€?

## Round-38 Delta (2026-05-01)

- Scope: governance escalation auto-remediation history gained summary/export capabilities for operational audit.
- New APIs:
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/summary
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/export
- Summary fields: dry_run_count, apply_count, executed_count, emitted_count, pruned_count, latest_record.
- Export contract: summary + paged records with limit/cursor/next_cursor/has_more and malformed_line_count.
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 96 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass




## Round-39 Delta (2026-05-01)

- Scope: add lifecycle governance for escalation auto-remediation history logs (prune with dry-run/apply).
- New API:
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/prune
- Prune outputs:
  - keep_last, total_records_before, kept_count, candidate_count, pruned_count
  - malformed_candidate_count, malformed_dropped_count
  - kept_run_ids, pruned_run_ids
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 96 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-40 Delta (2026-05-01)

- Scope: add auto-prune governance policy for escalation auto-remediation history logs.
- New API:
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-prune
- New policy env vars:
  - AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_PRUNE_TRIGGER_COUNT
  - AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_PRUNE_KEEP_LAST
- Auto-prune outputs:
  - should_prune + prune details (keep_last/kept/pruned/malformed counters)
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 97 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-41 Delta (2026-05-01)

- Scope: add digest observability for escalation auto-remediation history.
- New API:
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/digest
- New policy env var:
  - AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATIONS_STALE_SECONDS
- Digest outputs:
  - stale_threshold_seconds/latest_record_age_seconds/is_stale
  - recommended_action: run_auto_remediate_escalations | auto_prune_remediations | observe
  - summary snapshot with malformed and volume counters
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 99 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-42 Delta (2026-05-01)

- Scope: add one-click remediation orchestrator for escalation auto-remediation history governance.
- New API:
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate
- Orchestration behavior:
  - action=run_auto_remediate_escalations -> invokes escalation auto-remediate pipeline
  - action=auto_prune_remediations -> invokes remediation-history auto-prune pipeline
  - action=observe -> no-op
- Response contract:
  - executed/remediated_escalations/pruned_remediation_history
  - escalation_auto_remediate/remediation_auto_prune details
  - digest_before/digest_after for audit replay
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 101 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-43 Delta (2026-05-01)

- Scope: persist and expose orchestrator run history for remediation auto-remediation governance.
- New API:
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs
- Stored run fields:
  - action/executed/remediated_escalations/pruned_remediation_history
  - digest_before_message/digest_after_message/message
- Pagination contract:
  - limit/cursor/next_cursor/has_more + malformed_line_count
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 101 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-44 Delta (2026-05-01)

- Scope: add summary/export consumption layer for remediation-orchestrator run history.
- New APIs:
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/summary
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/export
- Summary outputs:
  - dry_run/apply/executed/remediated/pruned counters
  - latest_record and malformed_line_count
- Export contract:
  - summary + paged records with limit/cursor/next_cursor/has_more
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 101 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-45 Delta (2026-05-01)

- Scope: add lifecycle prune governance for remediation-orchestrator run history logs.
- New API:
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/prune
- Prune outputs:
  - keep_last/total_records_before/kept_count/candidate_count/pruned_count
  - malformed_candidate_count/malformed_dropped_count
  - kept_run_ids/pruned_run_ids
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 101 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-46 Delta (2026-05-01)

- Scope: add auto-prune governance policy for remediation-orchestrator run history logs.
- New API:
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-prune
- New policy env vars:
  - AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUNS_PRUNE_TRIGGER_COUNT
  - AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUNS_PRUNE_KEEP_LAST
- Auto-prune outputs:
  - should_prune + prune details (keep_last/kept/pruned ids and malformed counters)
  - malformed-triggered pruning with post-prune run-history readback validation
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 101 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-47 Delta (2026-05-01)

- Scope: add digest observability for remediation-orchestrator run history.
- New API:
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/digest
- New policy env var:
  - AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUNS_STALE_SECONDS
- Digest outputs:
  - stale_threshold_seconds/latest_record_age_seconds/is_stale
  - recommended_action: run_auto_remediation_orchestrator | auto_prune_runs | observe
  - summary snapshot with malformed and volume counters
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 103 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-48 Delta (2026-05-01)

- Scope: add one-click remediation orchestrator for remediation-orchestrator run-history governance.
- New API:
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate
- Orchestration behavior:
  - action=run_auto_remediation_orchestrator -> invokes remediation orchestrator pipeline
  - action=auto_prune_runs -> invokes run-history auto-prune pipeline
  - action=observe -> no-op
- Response contract:
  - executed/remediated_orchestrator/pruned_run_history
  - orchestrator_auto_remediate/run_history_auto_prune details
  - digest_before/digest_after for audit replay
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 105 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-49 Delta (2026-05-01)

- Scope: persist and expose run history for orchestrator-run auto-remediate executions.
- New API:
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs
- Stored run fields:
  - action/executed/remediated_orchestrator/pruned_run_history
  - digest_before_message/digest_after_message/message
- Pagination contract:
  - limit/cursor/next_cursor/has_more + malformed_line_count
- Stability hardening:
  - governance-run ordering adds attempt as tie-break key under same timestamp collisions.
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 105 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-50 Delta (2026-05-01)

- Scope: add summary/export consumption layer for orchestrator-run auto-remediate run history.
- New APIs:
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/summary
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/export
- Summary outputs:
  - dry_run/apply/executed/remediated_orchestrator/pruned_run_history counters
  - latest_record and malformed_line_count
- Export contract:
  - summary + paged records with limit/cursor/next_cursor/has_more
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 105 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-51 Delta (2026-05-01)

- Scope: add lifecycle prune governance for orchestrator-run auto-remediate run history logs.
- New API:
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/prune
- Prune outputs:
  - keep_last/total_records_before/kept_count/candidate_count/pruned_count
  - malformed_candidate_count/malformed_dropped_count
  - kept_run_ids/pruned_run_ids
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 105 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-52 Delta (2026-05-01)

- Scope: add auto-prune governance policy for orchestrator-run auto-remediate run-history logs.
- New API:
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-prune
- New policy env vars:
  - AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUN_AUTO_REMEDIATE_RUNS_PRUNE_TRIGGER_COUNT
  - AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUN_AUTO_REMEDIATE_RUNS_PRUNE_KEEP_LAST
- Auto-prune outputs:
  - should_prune + prune details (keep_last/kept/pruned ids and malformed counters)
  - malformed-triggered pruning with post-prune run-history readback validation
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 105 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-53 Delta (2026-05-01)

- Scope: add digest observability for orchestrator-run auto-remediate run-history.
- New API:
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/digest
- New policy env var:
  - AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUN_AUTO_REMEDIATE_RUNS_STALE_SECONDS
- Digest outputs:
  - stale_threshold_seconds/latest_record_age_seconds/is_stale
  - recommended_action: run_auto_remediation_orchestrator_runs | auto_prune_runs | observe
  - summary snapshot with malformed and volume counters
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 105 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-54 Delta (2026-05-01)

- Scope: add one-click auto-remediation orchestrator for orchestrator-run auto-remediate run-history governance.
- New API:
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate
- Orchestration behavior:
  - action=run_auto_remediation_orchestrator_runs -> invokes remediation-orchestrator auto-remediate pipeline
  - action=auto_prune_runs -> invokes run-history auto-prune pipeline
  - action=observe -> no-op
- Response contract:
  - executed/remediated_orchestrator_runs/pruned_run_history
  - orchestrator_runs_auto_remediate/run_history_auto_prune details
  - digest_before/digest_after for audit replay
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 105 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-55 Delta (2026-05-01)

- Scope: persist and expose run history for orchestrator-run auto-remediate run-history auto-remediate executions.
- New API:
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs
- Stored run fields:
  - action/executed/remediated_orchestrator_runs/pruned_run_history
  - digest_before_message/digest_after_message/message
- Pagination contract:
  - limit/cursor/next_cursor/has_more + malformed_line_count
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 105 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-56 Delta (2026-05-01)

- Scope: add summary/export consumption layer for orchestrator-run auto-remediate-runs execution history.
- New APIs:
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/summary
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/export
- Summary outputs:
  - dry_run/apply/executed/remediated_orchestrator_runs/pruned_run_history counters
  - latest_record and malformed_line_count
- Export contract:
  - summary + paged records with limit/cursor/next_cursor/has_more
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 105 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-57 Delta (2026-05-01)

- Scope: add lifecycle prune governance for orchestrator-run auto-remediate-runs execution history logs.
- New API:
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/prune
- Prune outputs:
  - keep_last/total_records_before/kept_count/candidate_count/pruned_count
  - malformed_candidate_count/malformed_dropped_count
  - kept_run_ids/pruned_run_ids
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 105 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-58 Delta (2026-05-01)

- Scope: add auto-prune governance policy for orchestrator-run auto-remediate-runs execution history logs.
- New API:
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/auto-prune
- New policy env vars:
  - AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUN_AUTO_REMEDIATE_RUNS_AUTO_REMEDIATE_RUNS_PRUNE_TRIGGER_COUNT
  - AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUN_AUTO_REMEDIATE_RUNS_AUTO_REMEDIATE_RUNS_PRUNE_KEEP_LAST
- Auto-prune outputs:
  - should_prune + prune details (keep_last/kept/pruned ids and malformed counters)
  - malformed-triggered pruning with post-prune run-history readback validation
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 105 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-59 Delta (2026-05-01)

- Scope: add digest observability for orchestrator-run auto-remediate-runs execution history.
- New API:
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/digest
- New policy env var:
  - AA_V7_BENCH_GOVERNANCE_ESCALATION_REMEDIATION_AUTO_REMEDIATE_RUN_AUTO_REMEDIATE_RUNS_AUTO_REMEDIATE_RUNS_STALE_SECONDS
- Digest outputs:
  - stale_threshold_seconds/latest_record_age_seconds/is_stale
  - recommended_action: run_auto_remediation_orchestrator_runs_auto_remediate_runs | auto_prune_runs | observe
  - summary snapshot with malformed and volume counters
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 105 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-60 Delta (2026-05-01)

- Scope: add one-click auto-remediation orchestrator for orchestrator-run auto-remediate-runs execution-history governance.
- New API:
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/auto-remediate
- Orchestration behavior:
  - action=run_auto_remediation_orchestrator_runs_auto_remediate_runs -> invokes upstream orchestrator-runs auto-remediate chain
  - action=auto_prune_runs -> invokes execution-history auto-prune chain
  - action=observe -> no-op
- Response contract:
  - executed/remediated_orchestrator_runs_auto_remediate_runs/pruned_run_history
  - orchestrator_runs_auto_remediate_runs_auto_remediate/run_history_auto_prune details
  - digest_before/digest_after for audit replay
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 105 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass

## Round-61 Delta (2026-05-01)

- Scope: persist and expose run history for orchestrator-run auto-remediate-runs auto-remediate executions.
- New API:
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs/auto-remediate/runs
- Stored run fields:
  - action/executed/remediated_orchestrator_runs_auto_remediate_runs/pruned_run_history
  - digest_before_message/digest_after_message/message
- Pagination contract:
  - limit/cursor/next_cursor/has_more + malformed_line_count
- Verification:
  - pytest tests/test_narrative_v7_modules.py tests/test_narrative_v7_api.py -q -> 105 passed
  - python -m compileall backend/app/services/narrative_v7 backend/app/api/routes/narrative_v7.py -> pass
