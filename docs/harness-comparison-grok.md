# Harness comparison: Grok Build

This comparison tests the [proposed session model](normalized-session-model.md)
against the official Grok Build coding-agent harness and its `grok` CLI, not the
Grok model API or an unrelated third-party CLI. The
[upstream repository](https://github.com/xai-org/grok-build) describes a coding
agent with interactive, headless and Agent Client Protocol (ACP) interfaces.
This is a documentation and source review, not tested adapter support or a
live run. Examples use synthetic values and `jsonc` comments; they are excerpts.

## 1. Sources and authentication

The
[headless guide](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/docs/user-guide/14-headless-mode.md)
describes a single `json` result, native `streaming-json`, and a
`streaming-messages-json` format with Messages-compatible event shapes. The
[CLI reference](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-shell/README.md)
also describes ACP over stdio. These are distinct interfaces even where their
payloads look alike. A Claude-shaped event produced by Grok is not evidence that
Claude was the harness or that every field has identical semantics.

The CLI documentation describes browser authentication and API-key
configuration; it says an API key takes precedence over browser credentials.
A future adapter needs to identify the effective authentication path where
observable and avoid silently selecting separately billed credentials. This
review does not establish subscription availability, quota detection or safe
recovery for every account and execution mode.

Upstream documentation differs about persistence: the CLI reference describes
session directories with ACP update and chat-history files, while the headless
guide describes session transcripts as SQLite. Treat this as an unresolved
interface or documentation discrepancy, not as a confirmed format transition.
Inspect the actual installed version and its source before relying on either
layout. Preserve raw artifacts and any capture limitations. Neither auth files
nor credentials belong in evidence.
[CLI persistence description](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-shell/README.md#session-persistence),
[headless file locations](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/docs/user-guide/14-headless-mode.md#file-locations)

## 2. Native streaming evidence

The headless guide shows `streaming-json` events for text and thought chunks,
tool calls and updates, per-response usage, errors and an end event. The event
list is not exhaustive. This synthetic example follows the documented shape:

```jsonc
{
  "type": "tool_call",
  "toolCallId": "call-1",            // Native identity across updates
  "toolName": "read_file",
  "kind": "read",
  "status": "in_progress",
  "rawInput": { "path": "src/main.py" },
  "content": [],
  "locations": []
}
```

```jsonc
{
  "type": "tool_call_update",
  "toolCallId": "call-1",            // Same native call
  "status": "completed",
  "rawOutput": { "lines": 42 },
  "content": [],
  "locations": []
}
```

The proposed model can retain the call and later state as related evidence,
with source references and the documented identity. It must preserve structured
output rather than force it into a string. A call update is not automatically a
new call; unknown or missing updates remain visible. Text and thought chunks
need source order and partial-content handling as in the Gemini comparison.

The `usage` stream event is described as a per-response boundary; its
`messageId` and other metadata are populated according to backend capability.
A normalizer must not invent an identifier or associate a usage report with a
response merely because a neighboring chunk looks related.
[Headless output formats](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/docs/user-guide/14-headless-mode.md#output-formats)

## 3. Usage and subagent coverage

The headless guide explicitly describes the scope of its prompt-level usage:
it includes finished subagents whose usage was applied before turn end, while
excluding compaction and other side-model calls. It can flag incomplete usage
when subagent accounting is missing or a drain times out. That is a defined but
potentially **non-exhaustive scope**, even if the emitted report is otherwise
complete under its stated rules.

```jsonc
{
  "type": "end",
  "sessionId": "session-1",
  "usage": {
    "input_tokens": 100,             // Uncached input in this interface
    "cache_read_input_tokens": 70,
    "cache_creation_input_tokens": 30,
    "output_tokens": 40,
    "total_tokens": 240              // Full input plus output
  },
  "usage_is_incomplete": true        // Illustrates reported incomplete usage
}
```

The guide describes the headless input field as uncached and states that the
total includes both cache buckets and output. It separately says ACP prompt
usage reports full input. These source-specific semantics must be retained;
matching field names or a shared protocol do not make the reports additive.
The end report can overlap per-response and child-session usage. It is not safe
to add them without verified scope and deduplication rules. A missing usage
object or missing cost is not zero.

Reported cost and completeness are also qualified: the guide says complete
server cost may be omitted and partial cost is explicitly indicated. Preserve
native qualifiers and currency, and distinguish a reported amount from a
measured charge or an estimate. The presence of a cost field does not by itself
establish the cost of a subscription-backed trial.
[Usage and cost notes](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/docs/user-guide/14-headless-mode.md#json)

## 4. Versions and compatibility

The source documentation shows ACP initialization with a protocol version;
that protocol version, the `grok` producer version, headless output format,
persisted-session format and wio-eval adapter version are separate facts. The
reviewed headless documentation does not establish a universal schema-version
marker or stability policy for all output and storage formats. Preserve unknown
events and fields, record available versions, and report unsupported or partial
interpretation. A compatibility check can exercise a bounded example but cannot
prove support for all backends, formats, subagents or quota states.

## 5. Implications for the model

1. **Coverage needs exclusions as well as completeness.** A source can report
   complete usage for a defined subset while excluding other activity. The
   normalized report should retain inclusion, exclusion and incompleteness
   separately; an inclusive-sounding label alone is insufficient.
2. **One harness, multiple projections.** Native, Messages-compatible and ACP
   outputs need distinct source identities and version-specific mappings, even
   when their record shapes overlap.
3. **Structured and incremental results.** Tool updates can carry structured
   outputs; messages and thoughts can be chunks. Preserve native data and update
   history without fabricating a complete message or tool result.
4. **Cross-source uncertainty.** Documentation disagrees on storage layout and
   does not establish every correlation between streams and saved sessions. Keep
   the sources separate until verified against the installed version.

The session, tool, usage, provenance and lifecycle concepts offer candidate
mappings. The [usage proposal](normalization-usage.md) is refined to explicitly
represent known scope exclusions. Live captures and versioned fixtures are
needed before an adapter contract or broader compatibility claim.
