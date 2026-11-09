# wio-eval

**Run the experiment. Keep the evidence. Decide for yourself.**

wio-eval is a standalone experiment execution and observability engine for AI
coding agents. It is being built to run controlled, repeatable experiments
across agent harnesses, models, prompts, repository states, instructions, and
workflows—and preserve the evidence needed to understand what happened.

It does not decide whether an agent was right, whether a workflow was better, or
whether a change should ship. Those decisions belong to your evaluation
protocol.

## Why wio-eval?

A single agent run can be compelling. It can also be misleading. Agent behavior
varies between runs, repository state changes, instructions differ between
harnesses, and long experiments can outlast a subscription quota window.

A useful comparison needs more than a final answer. It needs a known starting
point, independent repetitions, a record of interruptions and retries, and the
raw evidence behind every summary. wio-eval aims to make that foundation
reusable, so you can spend your effort on the questions you actually want to
ask.

## From a question to evidence

Imagine comparing two instruction files across Codex and Claude Code on the same
repository task. You want each combination repeated from the same starting
revision, and you want to know what the agents did—not just what they said.

The intended workflow is:

1. **Define the experiment.** Select harnesses, models, tasks, instruction
   variants, repository fixtures, and repetitions. Inspect the planned runs.
2. **Execute under controlled conditions.** Run independent trials in isolated
   environments, with scheduling and recovery for long-running experiments.
3. **Keep the evidence.** Preserve harness-native traces, execution metadata,
   available usage and tool activity, and repository changes alongside
   normalized records.
4. **Analyze it your way.** Give the results to deterministic checks, an
   LLM-based evaluator, a statistical analysis, or a protocol you have yet to
   invent.

The experiment defines the question. wio-eval is intended to run it and record
what happened. Your evaluator interprets the results.

## Designed for experiments, not just runs

- **Harness-neutral execution.** A common adapter interface is intended to
  support multiple coding agents, starting with Codex CLI and Claude Code,
  while retaining harness-specific behavior and evidence.
- **Controlled comparisons.** Extensible experiment matrices can vary prompts,
  models, instructions, workflows, fixtures, and other conditions. Repetitions
  remain distinct from infrastructure retries.
- **Reproducible starting points.** Trials can use pinned repository revisions,
  isolated workspaces, frozen inputs, and recorded environment provenance.
  Intentional shared-workspace runs are identified as such.
- **Long-running execution.** The scheduler is intended to use existing CLI
  subscriptions, recognize quota interruptions where reliably possible, and
  resume unfinished work without losing completed results.
- **Evidence at every level.** Raw events and artifacts sit alongside normalized
  records and numerical summaries for sessions, trials, configurations, and
  experiments. Unavailable and inferred information must be distinguishable from
  direct observations.
- **Analysis without lock-in.** Versioned, machine-readable results are intended
  to support offline analysis and future evaluators without rerunning agents.

These are design goals, not a claim that every capability is available today.

## Works with wio—and without it

[wio](https://github.com/msitarz/wio) defines workflows, behavioral guidance,
Work contracts, and stage progression. wio-eval is intended to run and compare
locked wio workflows against the same starting task, capturing stage activity
and artifacts for an external evaluator.

wio remains responsible for workflow orchestration. wio-eval remains useful on
its own, including for prompt comparisons, harness comparisons,
repository-guidance experiments, and custom research protocols.

## Project status

wio-eval is in early development. The repository currently contains a Python
project scaffold; the experiment engine and capabilities described above are
planned, not ready-to-use features. The project will build on the existing
[Ataraxia evaluation runner](https://github.com/msitarz/ataraxia/tree/master/script/eval),
with the aim of preserving its execution and quota-aware behavior as it evolves
into an independent engine.

## Development

The project requires Python 3.15 or later and uses
[uv](https://docs.astral.sh/uv/). To set up a clone and run the project checks:

```sh
make install
make check
```

Run `make help` for the available development targets.

## License

[Apache License 2.0](LICENSE).
