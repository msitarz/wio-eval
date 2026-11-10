# Harness comparison: Gemini CLI

This comparison tests the [proposed session model](normalized-session-model.md)
against Gemini CLI's documented programmatic output and published source. It is
an initial design review, not a claim of tested adapter support. It does not
include a live execution or a survey of every release and execution mode.
Examples use synthetic values and `jsonc` comments; they are excerpts, not
complete records.

## 1. Sources and boundaries

Gemini CLI documents a non-interactive `stream-json` mode that emits JSON Lines
for initialization, messages, tool calls and results, errors and a final result.
Its `json` mode returns a single response with statistics and an optional error.
These are different source interfaces and should be identified separately in
the result. [Headless mode reference](https://geminicli.com/docs/cli/headless/)

The CLI also saves project-specific sessions. Its
[session documentation](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/session-management.md)
describes saved conversation, tool activity and usage where available, as well
as retention and cleanup. The current
[session recording types](https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/services/chatRecordingTypes.ts)
include messages, tool calls, token summaries, a main or subagent kind, and
records for patches and rewinds. The reader must preserve the original artifacts
and understand those operations before claiming a reconstructed session is
complete. A source file can change or be cleaned up; capture and preserve it
rather than relying on a live path as durable evidence.

The stream and saved session may overlap, but the documentation examined does
not establish a universal correlation rule between their records. Do not count
both as independent activity or merge them on matching text alone. The runner's
attempt and process exit remain separate from a native `result` event.

## 2. Stream example and mapping

The upstream
[stream types](https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/output/types.ts)
and
[headless test snapshot](https://github.com/google-gemini/gemini-cli/blob/main/packages/cli/src/__snapshots__/nonInteractiveCli.test.ts.snap)
show shapes like these. Each block represents a separate stream event; values
are synthetic and timestamps are omitted for space.

```jsonc
{ "type": "init", "session_id": "session-1", "model": "example-model" }
```

```jsonc
{
  "type": "message",
  "role": "assistant",
  "content": "I will check ",
  "delta": true                      // Incremental message content
}
```

```jsonc
{
  "type": "tool_use",
  "tool_name": "example_tool",
  "tool_id": "call-1",               // Native call identifier
  "parameters": { "command": "pwd" }
}
```

```jsonc
{
  "type": "tool_result",
  "tool_id": "call-1",               // Correlates with the call
  "status": "success",
  "output": "/workspace/project"
}
```

The adapter can map `init` to session and context evidence, `tool_use` to a
tool call and `tool_result` to a linked result when the identifiers match. It
retains the native tool name, status, arguments and raw source. It does not
infer an MCP server or an exit code from the examples.

### Message fragments expose a model gap

The documented stream contains message chunks, and the source type has an
optional `delta` flag. A sequence of chunks is not automatically a complete
message: the inspected event type does not supply a message ID, and the stream
may stop partway through. A tool event or final result should not be assumed to
establish a message boundary without a verified source-specific rule.

The model should therefore preserve each fragment and its native order, exact
content and source reference. A reconstructed message is a derived view only
when a rule establishes which fragments belong together; it cites its inputs
and indicates whether completion is known. This illustrative observation uses
candidate fields, not settled schema names:

```jsonc
{
  "kind": "message_fragment",
  "session_id": "session-1",
  "data": {
    "role": "assistant",
    "content": "I will check ",      // Preserve whitespace exactly
    "native_delta": true,
    "message_id": null               // Not supplied by this stream example
  },
  "evidence": [{ "source_id": "gemini-stream", "locator": {
    "kind": "jsonl_line", "line": 2
  }}]
}
```

The `null` here means the identifier is unavailable in this example; the final
schema must distinguish that state from a known absence. Partial streams,
empty or whitespace-only fragments and unknown events must remain visible.

## 3. Usage, errors and subagents

The final stream `result` can include aggregate and per-model statistics. The
session recording types also include token summaries on messages. These reports
have potentially different scopes; they cannot be added together simply because
they are present in different sources. The usage model can retain them with
source and scope, but the exact category semantics, overlap and completeness
need source- and version-specific verification. A missing final event is not a
zero-usage result.
[Headless reference](https://geminicli.com/docs/cli/headless/),
[recording types](https://github.com/google-gemini/gemini-cli/blob/main/packages/core/src/services/chatRecordingTypes.ts)

Stream `error` events include non-fatal warnings and errors, while `result`
reports a final outcome. The upstream test snapshot includes an error event and
a subsequent success result in the same example. Preserve both native reports
and the independently observed process exit; do not turn any one of them into a
semantic judgment or discard a conflict.
[Upstream test snapshot](https://github.com/google-gemini/gemini-cli/blob/main/packages/cli/src/__snapshots__/nonInteractiveCli.test.ts.snap)

The saved-session types distinguish main and subagent conversations and include
an optional agent identifier on tool calls. These fields support retaining
native identifiers, but the examined sources do not establish a complete
parent-child mapping, child usage inclusion or full subagent observability.
Those remain unknown until verified for each relevant interface and version.

## 4. Compatibility and implications

The examined headless reference documents event kinds, and upstream source
provides current types and examples. It does not establish a schema-version
marker or a compatibility guarantee for every stream or saved-session format.
The `version` field in the recording types belongs to a nested memory
scratchpad, not demonstrably to the session format. Record the CLI version and
source interface separately from any verified native format version. Unknown
fields and events, malformed or partial records, and unsupported versions must
remain visible through preserved evidence and diagnostics.

This comparison suggests two refinements to the proposal:

1. Represent incremental message fragments and derived message reconstruction
   explicitly, including source order, whitespace and uncertain completion.
2. Allow a preserved session source to require replay of patches or rewinds;
   retain the source operations and their interpretation rather than treating
   every line as an independent final observation.

The existing session, tool call and result, lifecycle, source and usage
concepts otherwise provide candidate locations for the documented stream events.
That fit is preliminary: live captures, versioned fixtures and deeper research
are needed before claiming full coverage or fixing an adapter contract.
