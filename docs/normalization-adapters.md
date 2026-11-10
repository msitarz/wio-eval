# Normalization adapters and versioning

This document proposes how adapters turn preserved native evidence into
versioned normalized records. It consolidates the
[session model](normalized-session-model.md),
[provenance proposal](normalization-provenance.md) and harness comparisons. It
is a design for review, not an implemented interface or a compatibility claim.
Examples use synthetic `jsonc`; field names and identifiers are proposals.

## 1. References to native evidence

A normalized record should let a consumer find the retained evidence that
supports it. A **source** identifies an artifact or captured stream and its
origin; a **locator** identifies the relevant portion. The artifact identity and
an integrity digest bind the reference to the retained bytes, not a mutable live
path. The examples omit unrelated fields:

```jsonc
{
  "id": "source-1",
  "artifact_id": "artifact-1",        // Stable reference within the result
  "media_type": "application/x-ndjson",
  "digest": { "algorithm": "sha256", "value": "example-digest" },
  "source_interface": "session_file"
}
```

```jsonc
{
  "source_id": "source-1",
  "locator": {
    "kind": "jsonl_line",
    "line": 7,                        // One-based line in preserved artifact
    "pointer": "/message/content/1"  // JSON Pointer within that line
  }
}
```

The digest is illustrative, not a valid hash. A record can cite multiple
sources, and one source record can support several observations. A pointer to
a content block does not automatically cite the surrounding role or timestamp;
field-level provenance or equivalent references must identify the evidence for
claims from different locations.

Locators depend on the artifact. A captured byte stream can use a byte range;
a JSON document can use a JSON Pointer; a JSON Lines record can use a line and
pointer. A compressed or packed artifact may need a logical event sequence and
a decoding rule in addition to a physical artifact reference. A decoded sequence
is not a physical byte offset. A source without a stable fine-grained locator
can be cited at artifact level with that limitation stated.

The preserved artifact is immutable for the purpose of its reference. If
redaction changes bytes, the retained redacted artifact gets its own identity
and digest, and the redaction and resulting limits are recorded. The model must
not leak withheld content through a locator or diagnostic. The exact digest,
locator variants and field-level encoding remain open for a Work contract.
