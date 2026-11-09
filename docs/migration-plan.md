# Migration plan

Bring over Ataraxia's execution core and its tests in small, working slices,
then generalize it. Its runner already has substantial quota, process
management, and evidence logic; rewriting those while introducing multi-harness
support would put the most valuable behavior at risk.

Do not import the existing CLI unchanged as wio-eval's permanent public
interface. Its model assumes a matrix of context directories, models, and
reasoning efforts, and its Codex invocation requests a read-only sandbox. Those
are useful starting behaviors, but narrower than wio-eval's intended experiment
model.

## Existing capabilities

The
[Ataraxia runner](https://github.com/msitarz/ataraxia/tree/master/script/eval)
provides:

- **Input freezing and planning:** clean Git input checks, tracked-file
  snapshots, exact context composition, stable ordering, hashes, and Cartesian
  expansion over contexts, models, and efforts.
- **Execution:** bounded concurrency, a separate process supervisor, timeouts,
  output limits, cancellation, cleanup, and separately accounted infrastructure
  and capacity retries.
- **Codex integration:** subscription CLI execution, executable and version
  detection, raw JSONL capture, and conservative quota handling. Quota waiting
  is opt-in and fails closed when telemetry cannot be verified.
- **Evidence:** frozen plans, per-attempt streams and records, lifecycle events,
  and run summaries. The evidence store uses atomic publication and fsync for
  relevant writes.
- **Tests:** unit, integration, and acceptance coverage, including fake Codex
  executables and quota scenarios.

The runner does not resume a previous run, model repetitions as independent
trials, select arbitrary sparse matrix subsets in one run, isolate a repository
per trial, or support multiple harnesses. Its raw evidence is useful, but is not
alone the planned harness-neutral, versioned experiment result format.

Extraction requires more than `script/eval`: the runner depends on
`script/process_supervisor.py`, Pydantic, and `tiktoken`. The Codex adapter also
has an Ataraxia-specific package-version lookup.

## 1. Establish the preservation contract

Inventory existing tests and map observable behavior to wio-eval acceptance
scenarios: input freezing, matrix order, raw attempt evidence, retries,
cancellation, quota pause and recheck, and incomplete evidence.

Use the acceptance DSL with controlled fake harnesses. Wire InProcess and CLI
to the first real entry point as it emerges. Keep the Ataraxia tests as a
reference and migrate relevant tests alongside their code.

**Outcome:** a concrete list of behavior that must survive extraction,
including failure paths.

## 2. Extract a working Codex execution slice

Bring over the process supervisor, required models and ports, coordinator,
Codex adapter, evidence store, and supporting tests together. Adapt imports
and package metadata, declare dependencies, and provide a minimal wio-eval
entry point.

Initially retain existing behavior and conservative quota checks. Keep the
Codex-specific read-only and approval settings explicit rather than suggesting
they already support repository-editing experiments.

**Outcome:** standalone wio-eval can reproduce an Ataraxia-style Codex run
with controlled inputs and durable evidence.

## 3. Define the first versioned result contract

Introduce a documented result format that distinguishes experiment,
configuration, trial, attempt, and session. Preserve native streams and existing
operational records as artifacts, with explicit references and completeness
states.

Do not promise fields the source cannot observe. Distinguish inferred,
unavailable, and directly observed values. Preserve the evidence store's
no-overwrite and durability properties while evolving its records.

**Outcome:** external consumers have a stable foundation, and retries cannot
be mistaken for independent trials.

## 4. Generalize planning and repetitions

Separate input composition from matrix expansion. Add extensible dimensions,
explicit combination selection, stable coordinates and identities, repetition
indices, and inspectable plans. Preserve the existing composition and ordering
as supported behavior where appropriate.

Make scheduling order an explicit experiment condition so a protocol can
supply interleaved or randomized order without the engine making statistical
decisions.

**Outcome:** a plan can describe controlled comparisons without being
hard-coded to model and effort.

## 5. Add trial workspaces and repository evidence

Implement isolated trial workspaces from a pinned revision, plus an explicitly
declared shared-workspace mode. Capture the starting state, relevant
environment provenance, final status, diff, and recoverable artifacts.

Make execution permissions and Codex's current read-only request explicit
configuration: a coding task that edits a repository cannot be represented
honestly as the current read-only invocation.

**Outcome:** repetitions can start independently and their repository changes
can be inspected.

## 6. Make recovery durable

Build restart and resume on the versioned plan and evidence format. Reconcile
completed trials, interrupted attempts, uncertain process outcomes, and
evidence-write failures before dispatching more work. Preserve prior attempts
and never silently rerun a completed trial.

Keep quota interruptions distinct from agent failures, and retain Ataraxia's
fail-closed telemetry behavior.

**Outcome:** long experiments can resume safely across process restarts and
quota windows.

## 7. Generalize the harness boundary

Extract a harness-neutral adapter interface from the working Codex path,
keeping command construction, authentication behavior, quota interpretation,
and native event parsing provider-specific. Then add Claude Code against the
same contract and controlled acceptance scenarios.

Do not claim equivalent observability or quota recovery between harnesses
unless each adapter can establish it.

**Outcome:** harness becomes a matrix dimension without reducing all adapters
to Codex's assumptions.

## 8. Normalize and aggregate evidence

Incrementally normalize available session, usage, tool, MCP, and repository
observations while retaining raw artifacts. Add descriptive summaries at the
appropriate levels, preserving individual observations and denominators.

Leave semantic grading, statistical tests, and acceptance decisions to external
consumers.

**Outcome:** finished experiments are useful for offline analysis without
rerunning agents.

## First implementation step

Start with steps 1 and 2 as one narrow vertical slice: a frozen input, one fake
Codex invocation, one attempt, and durable raw evidence through both applicable
acceptance channels. Then add retries and quota scenarios before broadening the
planner. This brings a working execution path into the repository early while
keeping quota and evidence behavior under test.
