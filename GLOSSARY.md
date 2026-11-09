# Glossary

Terms used by wio-eval, the experiment execution and observability engine. Use
these names in code, docs and commit messages. They describe the intended
domain; they do not imply that every capability is implemented.

| Term | Meaning |
| --- | --- |
| Experiment | A defined collection of executions that varies selected conditions and preserves their evidence under one identity. An external protocol determines the question and how to interpret the results. |
| Experiment definition | The inputs and selection rules used to plan an experiment, including its dimensions and repetitions. |
| Matrix | The set of candidate combinations formed from independently configurable dimensions. Selection rules can choose a subset for execution. |
| Dimension | A named experimental variable, such as harness, model, task, instruction variant or repository fixture. |
| Matrix coordinates | The dimension names and values that identify a selected combination in an experiment. |
| Experiment configuration | One selected combination of experimental conditions, identified by its matrix coordinates and shared by its repetitions. |
| Scenario | A task and its relevant starting conditions as specified by an experiment. A scenario is not an independent repetition. |
| Task | The prompt, specification or other input that tells an agent what to do. |
| Trial | One intended independent execution of a configuration and task, identified by its repetition index. A trial can have multiple attempts but is one observation. |
| Repetition | An independently recorded trial of the same configuration and task, identified by a repetition index. |
| Attempt | One execution try for a trial. An infrastructure retry creates another attempt, not another independent trial. |
| Session | An agent interaction with a harness, with its own identity and boundaries where observable. A trial can contain more than one session. |
| Harness | The agent execution system invoked for a trial, such as Codex CLI or Claude Code. |
| Harness adapter | The integration that runs a harness through a common interface and captures its available native evidence and metadata. |
| Execution driver | The integration that defines how a trial's bounded execution proceeds. |
| Experiment plan | The selected, identified executions and their coordinates before they run, including repetitions and execution conditions. |
| Scheduler | The component that orders and starts planned work, manages concurrency, and handles retries and quota waits. |
| Quota interruption | An execution interruption reliably identified as subscription quota exhaustion, recorded separately from an agent failure. |
| Repository fixture | A specified repository starting state and associated inputs used to prepare a trial workspace. |
| Workspace | The filesystem environment in which a trial executes. An isolated workspace is independent of other trials; a shared workspace is an explicit non-isolated condition. |
| Provenance | The recorded origins and identities of experiment inputs, repository state, environment and execution configuration. |
| Evidence | Observations and artifacts captured from an execution, including available traces, usage, outputs and repository changes. |
| Raw evidence | Evidence preserved in its harness-native or original form, alongside any normalized representation. |
| Event | An individually recorded observation in an execution, such as a message, tool call or usage report, when available from its source. |
| Normalized record | A structured representation of observed execution data in a common format. Its source and whether values are observed, inferred or unavailable must remain distinguishable. |
| Artifact | A preserved file or other output associated with an experiment, trial, attempt or session, such as a raw event stream or repository diff. |
| Aggregate | A descriptive numerical summary of recorded observations, with its scope and denominator preserved. It does not replace the underlying evidence or judge an outcome. |
| Result | The versioned, machine-readable record of an experiment's configuration, execution, evidence references, summaries and completeness. It is not a semantic judgment of success. |
| External evaluator | A system or protocol that consumes evidence and decides how to assess behavior or outcomes. It is outside the execution engine. |
