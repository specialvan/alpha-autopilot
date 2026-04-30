# V7 Claude Review Request Prompt

璇峰浠ヤ笅鎻愪氦鎵ц V7 闃舵璇勫锛堢涓夊崄涓冭疆鐢熶骇鍖栧寮洪獙鏀讹級锛?
## 璇勫鐩爣

1. 楠岃瘉娌荤悊鍗囩骇浜嬩欢鑷剤杩愯鍘嗗彶锛坅uto-remediations锛夋帴鍙ｅ绾︺€?2. 楠岃瘉鑷剤鎵ц缁撴灉涓庡巻鍙茶褰曞瓧娈电殑涓€鑷存€с€?3. 楠岃瘉鍘嗗彶鍒嗛〉鑳藉姏鍦ㄥ€肩彮娑堣垂鍦烘櫙涓嬬殑绋冲畾鎬с€?4. 楠岃瘉 dry-run 涓?apply 涓ょ被杞ㄨ抗鍧囧彲瀹¤杩借釜銆?
## 閲嶇偣妫€鏌ラ」

- `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations`
  - 璁℃暟瀛楁锛歚total_records/malformed_line_count`
  - 鍒嗛〉瀛楁锛歚limit/cursor/next_cursor/has_more`
  - 璁板綍瀛楁锛歚action/executed/emitted/pruned/emitted_event_id/auto_prune_*`
- 鍏宠仈鏍搁獙锛?  - `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediate`
  - `GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/digest`
  - `POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-prune`

## 杈撳嚭瑕佹眰

璇锋寜浠ヤ笅缁撴瀯杈撳嚭锛?1. 闃诲闂锛圥0锛?2. 楂樹紭鍏堜慨澶嶏紙P1锛?3. 鍙悗缁凯浠ｄ紭鍖栵紙P2锛?4. 鍙獙鏀剁粨璁猴紙鏄惁閫氳繃绗笁鍗佷竷杞敓浜у寲楠屾敹锛?5. 绗笁鍗佸叓杞缓璁垏鐗囷紙鎸?PR-AA 缂栧彿锛?

## Round-38 Additional Review Targets

Please additionally review the newly added remediation history observability contract:

- GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/summary
  - Validate totals, window statistics, malformed_line_count, and latest_record consistency.
- GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/export
  - Validate summary + records packing, pagination continuity (cursor -> next page), and malformed handling.
- Correlate with:
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediate
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations




## Round-39 Additional Review Targets

Please additionally review remediation history log lifecycle behavior:

- POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/prune
  - Validate dry_run/apply semantics and keep_last retention behavior.
  - Validate malformed_candidate_count and malformed_dropped_count accounting.
  - Validate kept/pruned run-id lists align with list endpoint after pruning.
- Correlate with:
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/export

## Round-40 Additional Review Targets

Please additionally review remediation history auto-prune behavior:

- POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-prune
  - Validate dry_run/apply semantics and should_prune gating.
  - Validate env-policy routing (trigger_count/keep_last) and malformed-triggered pruning behavior.
  - Validate prune detail fields (kept/pruned ids, malformed counters) and post-prune readback consistency.
- Correlate with:
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/prune

## Round-41 Additional Review Targets

Please additionally review remediation history digest behavior:

- GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/digest
  - Validate no_records/stale/threshold/malformed decision branches.
  - Validate recommended_action contract and message routing.
  - Validate latest_record age calculation and stale-threshold env override behavior.
- Correlate with:
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-prune
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediate

## Round-42 Additional Review Targets

Please additionally review remediation-history orchestrator behavior:

- POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate
  - Validate action routing based on remediation digest recommendation.
  - Validate dry_run/apply semantics and executed flags.
  - Validate nested execution payloads and digest_before/digest_after audit consistency.
- Correlate with:
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/digest
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediate
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-prune

## Round-43 Additional Review Targets

Please additionally review remediation-orchestrator run history behavior:

- GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs
  - Validate record ordering and pagination continuity.
  - Validate action/executed/remediated/pruned flags and digest-message trace fields.
  - Validate dry_run/apply tracks are both persisted and queryable.
- Correlate with:
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/digest

## Round-44 Additional Review Targets

Please additionally review orchestrator-run summary/export behavior:

- GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/summary
  - Validate aggregate counters and latest_record consistency.
- GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs/export
  - Validate summary + paged record packing and cursor continuity.
- Correlate with:
  - GET /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate/runs
  - POST /api/narrative/v7/benchmark/maintenance/alerts/governance/runs/escalations/auto-remediations/auto-remediate
