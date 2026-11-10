# Execution evidence for normalization

This working document extends the
[proposed session model](normalized-session-model.md) with evidence the runner
and workspace can supply. It describes intended outcomes, not implemented
records or a settled schema. The
[provenance proposal](normalization-provenance.md) applies to these observations
as well as to harness-native records.

Examples use synthetic `jsonc` excerpts. Comments explain fields; identities,
status names and storage layout are proposals. An omitted field is not
necessarily absent in the source.

## 1. Runner lifecycle

The runner knows what it planned to start and what it observed while managing
execution. Its lifecycle evidence connects the experiment plan to attempts and
sessions, including work that fails before a harness creates a session.

```mermaid
flowchart LR
    P[Planned trial] --> A1[Attempt 1]
    A1 --> I[Interruption observed]
    I --> A2[Attempt 2]
    A2 --> E[Process exit observed]
    A1 --> S1[Session evidence, if available]
    A2 --> S2[Session evidence, if available]
```

A trial is one intended independent observation. A retry is another attempt of
that trial, not another repetition. An attempt can contain several sessions or
none; a native session can be linked only when the relationship is supported by
runner or harness evidence. A stage is recorded where the execution driver can
identify its boundary; it is not assumed from a session or process boundary.

### Planned and observed execution

A plan record identifies the trial and intended conditions. It does not prove
that the runner started them. A runner event records an observed lifecycle
transition with a source and available time:

```jsonc
{
  "id": "event-1",
  "kind": "attempt_started",
  "trial_id": "trial-1",
  "attempt_id": "attempt-1",
  "timestamp": "2026-01-01T12:00:00Z",
  "observation_status": "observed", // Runner recorded the transition
  "evidence": [{ "source_id": "runner-log", "locator": {
    "kind": "jsonl_line", "line": 10
  }}]
}
```

The record is an illustrative normalized observation; it does not prescribe a
runner log format. The source and its locator identify preserved evidence.
Wall-clock timestamps, monotonic durations and their clock sources have
different properties and should be recorded when available. Missing end
boundaries remain unknown rather than being filled from the last event.

### Exit, failure and interruption

A process exit is an observation; the meaning of the exit is a separate claim.
For example, a zero exit status does not by itself establish that the task was
successful or that all evidence was captured.

```jsonc
{
  "kind": "process_exit",
  "attempt_id": "attempt-1",
  "data": { "exit_code": 1 },        // Directly observed process status
  "observation_status": "observed",
  "evidence": [{ "source_id": "runner-log", "locator": {
    "kind": "jsonl_line", "line": 25
  }}]
}
```

An interruption classification needs its own basis. A quota interruption can
be identified only when evidence reliably supports it. An unclassified failure
is not automatically an agent failure or a quota event. If a rule infers a
classification, the record should identify the rule and evidence, and retain
the direct observations. The attempt and trial can remain incomplete or
uncertain when recovery cannot safely determine their state.

```jsonc
{
  "kind": "interruption_classification",
  "attempt_id": "attempt-1",
  "data": { "classification": "quota_interruption" },
  "observation_status": "inferred", // Interpretation of separate evidence
  "rule": "example-quota-rule",
  "evidence": [{ "source_id": "stderr-artifact", "locator": {
    "kind": "byte_range", "start": 0, "end": 120
  }}]
}
```

The locator and rule are illustrative; the example does not assert that any
specific stderr text reliably identifies quota exhaustion. An unavailable or
redacted source limits what the classification can establish.

### Waits, retries and completion

A quota wait can have a start, end and reason where observable. A retry event
links the new attempt to the same trial and can state the runner's reason. If a
process stops or restarts before a wait ends, the missing boundary and recovery
state remain visible. Completion is a recorded state under an explicit execution
boundary; it is not a semantic judgment of the agent's answer.

The result should retain lifecycle events and their sources even for failed or
partial attempts. A summary can count attempts, interruptions and wait durations
only with defined scopes and denominators; overlapping or incomplete durations
must not be added as if they were independent complete waits.

### Questions for review: lifecycle

1. Which runner events establish attempt and trial completion, and how are
   uncertain process states resolved after a restart?
2. What source-specific evidence is sufficient to classify quota exhaustion and
   distinguish it from other interruptions?
3. How should a recovered session be linked across attempts without treating
   earlier events as new independent activity?
4. Which clock and interval semantics allow durations and waits to be compared
   without hiding missing boundaries?
