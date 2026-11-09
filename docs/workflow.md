# wio-eval's development workflow

This workflow adapts
[wio's own workflow](https://github.com/msitarz/wio/blob/master/docs/workflow.md)
for developing wio-eval. It governs work on this repository; wio-eval itself
remains independent of wio. The workflow is described by the local
[configuration](../.agents/wio/config.toml),
[templates](../.agents/wio/templates), and [rules](../.agents/wio/rules).

wio is still being built. Until its commands and workflow features support this
configuration, follow the process manually. The configuration expresses the
intended workflow; it does not establish that automated progression, checks,
records, or gates are available here. Follow the repository's existing checks
and [agent instructions](../AGENTS.md) in the meantime.

## When to use it

Use a Work contract for a change that makes design decisions or establishes
behavior, such as a migration slice. Small changes with no design decisions do
not need one. A contract states an outcome and how to recognize it; it is not a
task list or a record of progress.

One Work is a **leaf** when it delivers one coherent outcome. Split it into a
**parent** and child Works when the outcomes can be delivered independently.
Define the parent before its children, deliver shared boundaries first, and
integrate the children after they are delivered. Investigate an uncertain split
only enough to resolve it; exploration does not authorize implementation.

## Define a Work

Start with the draft template's purpose and intent. Clarify the outcome, choose
leaf or parent, and write the corresponding contract in
`.agents/wio/works/`. The templates define sections for goals, non-goals,
assumptions, mechanisms, constraints, acceptance criteria, and other context.
A parent also describes the structural change and constraints its children
inherit. Identify assumptions and make each acceptance criterion independently
assessable.

Review the contract before delivery. The reviewer checks it against the
contract rules; the human driver confirms that it states the intended outcome.
A review result is `pass`, `fail`, or `unknown`. Only a pass permits the next
stage; `unknown` means the reviewer could not decide.

## Deliver a Work

A leaf follows the `typed-boundary` pipeline:

1. **Architecture:** establish the typed boundaries and test stubs needed by
   the contract; review them against it.
2. **Wiring:** compose a running skeleton with stubbed leaves; review the
   composition and boundaries.
3. **Implementation:** implement the leaves until tests and checks pass;
   review the behavior against the contract.
4. **Promote docs:** carry lasting guarantees and reasons into the appropriate
   repository documentation or link to source and tests that state them; review
   the result for lost guarantees.

A parent follows the `integrate` pipeline: join delivered children, add tests
for the parent's system-level criteria, review the integrated result, and
promote the lasting documentation.

Each authoring stage has a gate. Review the exact committed revision in a fresh
session or by a person other than the author. Passing automated checks are
supporting evidence, not the review verdict. Contract and documentation gates
require the human driver's confirmation; the delivery gates are agent reviews.

A top-level Work's spent contracts are removed only after their guarantees are
promoted and the driver confirms. Contracts beneath a parent stay until the top
Work is promoted. The documentation review still needs its own confirmation;
confirmation of deletion is not a substitute. If review fails, restore any
removed contracts and correct the promotion.

## Change a contract

When delivery exposes a problem, propose the change and let the driver decide:

- **Amend** when intent, criteria, assumptions, or constraints change. Identify
  the changed items, review and confirm the amendment, and redo delivery work
  invalidated by it.
- **Ratify** when wording, diagrams, or links need to match what was built
  without changing a guarantee. Review that no guarantee changed; otherwise
  amend instead.
- **Abandon** when the driver decides to stop the Work. Update any dependent
  Works along with it.

A failed gate can send work back to an earlier stage. Repeated returns to the
same stage are a reason to revisit assumptions or the Work's scope.

## Configuration and checks

The local config defines the `feature` kind, its draft, leaf and parent
templates, the `define`, `deliver`, `amend`, and `ratify` actions, and the
stage pipelines. The `contract` root selects authoring rules for Works;
`wio-eval` selects the code and test paths; and `repo` covers repository-wide
documentation. Rules and templates are local so this repository owns the
workflow it follows.

When the wio CLI supports this workflow, validate changes to the config and
contracts with its checks and record stage results using its supported
interfaces. Until then, inspect these files directly and run `make check` for
the checks this repository actually provides. No wio hook or automatic
progression is assumed by this workflow.
