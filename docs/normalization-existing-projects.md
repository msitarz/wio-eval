# Existing normalization projects

This report compares existing open-source session normalizers and schemas with
the outcomes in the [proposed session model](normalized-session-model.md) and
[adapter design](normalization-adapters.md). The projects are useful references
and possible integration candidates; none of the findings establishes that a
project covers every harness version or preserves all native evidence.

wio-eval needs to retain raw evidence, identify the source and interpretation
of normalized observations, distinguish missing values from zero, and keep
trials and infrastructure attempts distinct. A convenient conversation view can
be useful without meeting all of those requirements. Evaluation, behavioral
classification and acceptance decisions remain outside wio-eval.

## Candidates

| Project | Main value | Boundary to investigate |
| --- | --- | --- |
| [GitHub Agentic Workflows](https://github.com/github/gh-aw) | Unified event specification, schemas and harness parsers. | CommonJS code is integrated with a workflow system; published views can be projections. |
| [Letta trajectory](https://github.com/letta-ai/trajectory) | Reusable normalization library with a wide source list and diagnostics. | Model-ready records do not preserve all native usage and events. |
| [Harbor ATIF](https://github.com/harbor-framework/harbor/blob/main/rfcs/0001-trajectory-format.md) | Versioned trajectory format, Python models and validator. | A trajectory is narrower than the whole experiment result and its provenance. |
| [agentminutes](https://github.com/agent-ecosystem/agentminutes) | Common events and explicit accounting for source lines. | Fewer supported harnesses; Go integration and fidelity need assessment. |
| [Entire transcript](https://github.com/entireio/cli/blob/main/transcript/README.md) | Cross-harness conversion and tool/usage correlation. | Some native details and branches are intentionally omitted. |
| [minitrace](https://github.com/fukami/minitrace) | Versioned trace, adapters and format-change checks. | Selected-branch and analysis-oriented views do not preserve all evidence. |
| [agent-session-to-atif](https://github.com/rushabhpat/agent-session-to-atif) | Claude, Codex and Cursor conversion to ATIF. | Missing or malformed input needs stronger diagnostics for our use. |

## GitHub Agentic Workflows

The
[unified session specification](https://github.github.com/gh-aw/specs/unified-agent-session-specification/)
describes a common event vocabulary, source provenance, ordering, partial
streams, tool correlation and accounting. The repository has machine-readable
schemas and source-specific parsers under `actions/setup/js/`. Its parser
registry covers several harnesses, but a registered name does not mean every
native interface is supported: the DeepSeek parser, for example, targets a
limited headless output profile rather than the full persisted-session format.
[Parser registry](https://github.com/github/gh-aw/blob/main/actions/setup/js/engine_log_parser.cjs),
[DeepSeek parser](https://github.com/github/gh-aw/blob/main/actions/setup/js/parse_deepseek_log.cjs)

The full merged artifact is an essential, redacted projection; native artifacts
are separate, and the compact profile is intentionally lossy. Its CommonJS
implementation is connected to GitHub Actions and workflow artifacts rather
than presented as a standalone Python library. It is a strong source of
requirements, event shapes and fixtures, but direct dependency reuse needs a
packaging and coverage assessment. The specification's loss-preservation
requirements should be evaluated at the level of each supported field and
source, not assumed to preserve every native record.

## Letta trajectory

[trajectory](https://github.com/letta-ai/trajectory) converts specified native
session inputs from Claude, Codex, Gemini, OpenCode, Pi and other sources into
shared, validated records and diagnostics. Its input interfaces are specific:
for example, its listed Gemini and OpenCode inputs are session JSON, not every
stream or persistence format those harnesses expose. Its Python package wraps a
bundled JavaScript runtime and requires Node; it is not a native Python parser.

The library is designed for model-ready trajectories. Some source data is
filtered or transformed, and its primary normalized records do not carry all
native usage and cost fields. A consumer must not assume that an empty
`diagnostics` array proves that every source field was represented. Its
[canonical format](https://github.com/letta-ai/trajectory/blob/main/CANONICAL.md),
[adapters](https://github.com/letta-ai/trajectory/tree/main/src/adapters) and
[source-version audit](https://github.com/letta-ai/trajectory/blob/main/SOURCE_VERSION_AUDIT.md)
are useful references for mappings and compatibility fixtures. A wio-eval
integration would still need raw artifact retention, usage handling, scope and
loss diagnostics outside the model-ready view.

## ATIF and conversion

Harbor's
[Agent Trajectory Interchange Format](https://github.com/harbor-framework/harbor/blob/main/rfcs/0001-trajectory-format.md)
provides a versioned JSON trajectory with messages, tool calls and observations,
metrics, extension fields and subagent trajectories. Harbor publishes
[Pydantic models and a validator](https://github.com/harbor-framework/harbor/blob/main/docs-mintlify/agents/atif.mdx).
It is a concrete candidate for a session or trajectory export, and its schema
should be compared field by field with the proposed normalized records.

ATIF does not by itself define the full wio-eval experiment plan, workspace
provenance, attempt lifecycle and raw artifact guarantees. An exporter must not
invent missing values to satisfy a trajectory shape, nor confuse its evaluation
or training-related extension fields with wio-eval's own responsibilities.

[agent-session-to-atif](https://github.com/rushabhpat/agent-session-to-atif)
is a concrete converter and documents native source limitations and Claude
message-ID usage deduplication. Its reader can skip invalid lines, and some
usage calculations treat missing components as zero. Those behaviors require
additional checks before using its output as authoritative evidence.

## Other parser and trace designs

[agentminutes](https://github.com/agent-ecosystem/agentminutes) exposes a Go
library and CLI with a versioned event schema, optional raw records and source
line locations. Its accounting for every input line as an event, counted skip or
error is a valuable compatibility-check pattern. Counted skips are not a
substitute for preserved raw artifacts; its version hint does not itself select
a version-specific parser.

[Entire transcript](https://github.com/entireio/cli/blob/main/transcript/README.md)
contains useful examples of linking tool results and handling repeated usage.
Its converters document omitted thinking, unsupported Codex items and excluded
Pi branches. A derived transcript may therefore be useful to consumers while
being incomplete as an execution record. The package and its format are
versioned with its CLI and may change.

[minitrace](https://github.com/fukami/minitrace) offers cross-harness adapters,
a versioned format and a tool to detect native-format changes. Its selected
conversation branch, possible truncation and quality or behavioral annotations
are choices for a particular analysis view. The full source evidence and the
meaning of missing usage must remain available if wio-eval uses such a view.

## Direction for wio-eval

The evidence supports a layered design: preserve native artifacts first; produce
versioned, traceable normalized records with explicit gaps; then offer derived
or interoperable views such as ATIF where appropriate. No project should be
adopted as the only evidence representation without testing whether it retains
or reports unknown records, partial sources, usage semantics, updates, branches
and source locations.

The next evaluation can use the same sanitized fixtures for each candidate,
including incomplete and multi-session examples. Compare the normalized outputs
and diagnostics against the raw inputs before deciding whether to depend on a
library, adapt its code or implement a narrower interface. The
[Harbor and Ataraxia comparison](execution-engine-comparison.md) considers the
separate question of execution and scheduling.
