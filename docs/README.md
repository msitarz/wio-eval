# Project boundaries

- Keep experiment planning, execution, evidence collection and external
  evaluation distinct. Numerical summaries belong here; semantic grading,
  statistical decisions and acceptance judgments do not.
- Preserve raw harness-native evidence alongside normalized results. Distinguish
  observed, inferred and unavailable data; never invent observability.
- Keep trials, execution attempts and sessions distinct.
  Retries must not silently become independent observations.
- Favor isolation, provenance, resumability and accurate incomplete records.
  Support shared workspaces only as an explicit experimental condition.
- Keep harnesses behind adapters. External systems can use wio-eval as an
  execution stage; workflow definitions and orchestration stay outside the
  engine.
- Build on the existing Ataraxia runner, preserving proven functionality,
  including subscription-aware quota handling. Inspect existing code before
  proposing migration changes and avoid assuming planned features already exist.
- Acceptance tests use a domain DSL with CLI and InProcess channels, following
  [the acceptance guide](../tests/acceptance/README.md). The DSL and channels
  are planned, not yet implemented.
