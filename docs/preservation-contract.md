# Runner preservation contract

This inventory guides the extraction of Ataraxia's `script/eval` into wio-eval.
It records existing behavior to preserve and scenarios to build as each slice
moves. It is a migration contract, not a claim that wio-eval implements these
behaviors today. Source test paths below are relative to the
[Ataraxia repository](https://github.com/msitarz/ataraxia/tree/master).

A scenario checks observable behavior through the acceptance DSL. Use the
InProcess and CLI channels where both can exercise the same behavior; reserve
process-only behavior for CLI. Use controlled harnesses, not live model calls.
Migrate relevant unit and integration tests with their implementation; the
acceptance scenarios do not replace their edge-case coverage.

## Behavior inventory

| Area | Existing behavior to preserve | Ataraxia test evidence | Migration scenario or check | Status |
| --- | --- | --- | --- | --- |
| Inputs | Freeze exact tracked input bytes and instructions from a clean repository; reject changed, invalid or unsuitable inputs rather than silently reading different data. | `test/script/integration/eval/test_inputs.py`; `test/script/integration/eval/test_evidence.py` | Freeze an input, change its source after freezing using a controlled boundary, and verify the attempt uses the frozen bytes. Reject a dirty input before dispatch. | Planned |
| Composition and planning | Compose one selected file per directory with exact separators; preserve ordered context, model and effort products, including repeated directory positions. | `test/script/unit/eval/test_plan.py`; `test/script/unit/eval/test_options.py` | Inspect a known plan and assert its coordinates, order and composed bytes. Check repeated inputs and explicit separators at unit level. | Planned |
| Dry run | Validate and plan without starting Codex or creating execution output; label token counts as estimates. | `test/script/acceptance/eval/test_cli_command.py` (`test_dry_run_requires_no_provider_or_output`); `test/script/unit/eval/test_tokens.py` | Inspect a plan without a harness executable or output directory. Keep unknown and approximate token estimates distinct. | Planned |
| Invocation | Resolve the Codex executable and version, build a request from frozen inputs, and request the existing read-only and approval settings. Preserve unknown effective settings as unknown. | `test/script/integration/eval/test_codex_binding.py`; `test/script/unit/eval/test_runner_codex.py` | Run one controlled fake Codex invocation and verify the supplied input and requested settings. Test executable resolution separately. | Planned |
| Raw evidence | Persist the plan before dispatch, then retain attempt records and raw streams; distinguish empty streams from unavailable observations. A successful process is not a quality verdict. | `test/script/integration/eval/test_evidence.py`; `test/script/acceptance/eval/test_cli_command.py` (`test_command_records_fake_attempt_and_maps_outcome`) | Run a successful fake attempt and inspect its recorded status and exact stdout and stderr. Cover unavailable versus empty streams in integration tests. | Planned |
| Evidence failures | Refuse existing output and artifact collisions; preserve already published evidence. Failed required writes or unsafe cleanup cannot become a successful result. | `test/script/integration/eval/test_evidence.py`; `test/script/unit/eval/test_coordinator.py`; `test/script/acceptance/eval/test_cli_command.py` (`test_recording_obstruction_reports_incomplete_evidence`) | Cause an evidence write to fail through a controlled seam; report incomplete evidence and retain whatever was safely published. Never overwrite an existing run. | Planned |
| Supervision | Bound concurrency and attempt runtime; capture output, enforce configured limits, stop and clean up processes, and retain observed failure or cancellation evidence. | `test/script/integration/test_process_supervisor.py`; `test/script/unit/test_process_supervisor.py`; `test/script/integration/eval/test_coordinator.py` | CLI scenarios cover timeout, output limit and cancellation with a fake child; integration tests cover process cleanup and concurrency slots. | Planned |
| Retries | Keep attempts distinct from scheduled calls. Retry only when policy and evidence permit; infrastructure and capacity allowances are separate. Capacity waits need not block unrelated calls. | `test/script/unit/eval/test_runner_policy.py`; `test/script/unit/eval/test_coordinator.py`; `test/script/acceptance/eval/test_cli_command.py` (`test_capacity_retries_use_the_same_frozen_invocation`) | Induce an eligible retry, verify both attempt records use frozen input and remain attached to one planned execution. Reject ambiguous outcomes. | Planned |
| Quota | Waiting is opt-in. Only verified, fresh, correctly scoped quota evidence can authorize recovery; probes are separate supervised invocations with their own evidence and bounds. | `test/script/acceptance/eval/test_cli_command.py` (`test_quota_wait_resumes_after_two_separate_probes`, `test_quota_wait_refuses_unverified_or_ambiguous_evidence`); `test/script/unit/eval/test_runner_codex_quota.py`; `test/script/unit/eval/test_coordinator_quota.py` | With fake telemetry, pause on verified exhaustion, persist wait and probe evidence, and resume only after a fresh scoped available observation and durable wait closure. Unknown, stale, mismatched or ambiguous telemetry must not resume. | Planned |
| Progress and status | Report calls, attempts and probes separately; progress must not delay execution or cancellation. Exit status distinguishes failure, incomplete evidence and cancellation. | `test/script/acceptance/eval/test_cli_command.py`; `test/script/integration/eval/test_progress_writer.py`; `test/script/unit/eval/test_standalone_status.py` | Verify status and evidence for a failed run and an incomplete run. Test blocked progress and signal handling through CLI. | Planned |

## First vertical slice

The first extraction slice uses one frozen tracked input, one fake Codex
invocation, one attempt, and durable raw evidence. The command surface and
result schema must emerge from that slice; these scenarios do not prescribe
argument names or artifact paths.

1. **Frozen input reaches the harness.** Given a valid source, freeze it;
   change the source at a controlled boundary before dispatch. The fake harness
   receives the exact frozen input, and the plan or evidence identifies it.
   This checks a distinct property: Ataraxia's normal input validation rejects
   dirty sources *before* freezing.
2. **A successful attempt retains evidence.** Given a fake harness that emits
   known stdout and stderr and exits successfully, the result records one
   successful attempt and preserves both streams exactly. The run reports
   execution status, not task quality.
3. **A failed attempt is not success.** Given a fake harness that exits
   unsuccessfully, the run reports failure and preserves the attempt's observed
   status and streams.
4. **A required evidence failure is not success.** Given an injected failure at
   a required write, the run reports incomplete evidence and does not claim a
   successful durable record. Preserve any safely published artifacts.
5. **An existing output is not overwritten.** Given an existing destination,
   preparation refuses it before dispatch and leaves its contents unchanged.

Use both channels for applicable scenarios. For the CLI channel, invoke a fake
executable in the test sandbox; for InProcess, inject controlled collaborators.
Neither requires subscription credentials or network access. Where a behavior
requires a real subprocess, test it through CLI and cover the shared policy
in-process at the appropriate layer.

## Later behavior and explicit gaps

Before migrating retries and quota handling, translate the relevant inventory
rows into executable scenarios and bring their detailed edge-case tests with the
code. In particular, verify no retry follows an ambiguous result, active work
settles before a quota probe, and a failed evidence write cannot open the quota
gate.

Ataraxia's runner requires a fresh output directory and does **not** resume a
previous run. It does not provide independent repetitions, per-trial repository
isolation, arbitrary sparse matrix selection, multiple harnesses, or a versioned
harness-neutral experiment schema. These are future wio-eval capabilities,
not preservation claims. A manual subset rerun to a new output is not resume.
