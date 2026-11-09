# wio-eval acceptance tests

This guide adds to the [test strategy](../README.md): it describes the
acceptance DSL and the CLI and InProcess channels intended for wio-eval. The
channel selection, facade and driver interfaces are in place; the drivers will
be wired to wio-eval when it has an executable entry point.

## 1. Principles

- **Speak the domain's language.** Scenarios describe experiments, trials and
  evidence through the DSL. Drivers know how to reach wio-eval.
- **One acceptance criterion, one scenario.** Each scenario covers an
  independently assessable behavior.
- **Drivers return data and do not assert.** Scenarios assert on results with
  plain `assert`, keeping drivers reusable and pytest's assertion introspection
  useful.
- **Fast by default.** The InProcess channel is intended to run without a
  subprocess. The CLI channel is the acceptance reference and runs the same
  applicable scenarios through the real command.
- **Start small.** Add DSL vocabulary, builders and drivers when scenarios need
  them.

## 2. Layout and DSL

Organize scenarios by feature, with CLI-specific behavior in `cli/`. Keep the
DSL and its drivers under `tests/acceptance/` until another consumer needs them.
The facade gives scenarios a common vocabulary; a driver implements each
channel. Prefer a generic command operation and add domain-specific operations
when scenarios need them, rather than anticipating the entire interface.

Use builders for experiment definitions or fixtures when they make scenarios
clearer and reduce repeated setup. Use temporary repositories and controlled
harness responses to exercise execution, retries and evidence without depending
on subscriptions, network access or nondeterministic model behavior. Tests must
not touch a developer's credentials or repository state.

Return structured results so scenarios can inspect exit status, output and
artifacts explicitly. If shared DSL modules contain assertion helpers, register
those modules for pytest assertion rewriting. For asynchronous channels, provide
bounded waiting helpers where needed.

## 3. Channels

- **InProcess** runs applicable scenarios in the same process for fast feedback.
- **CLI** runs the installed command as a subprocess and is the reference for
  user-visible behavior, including exit status, streams and process environment.

Run the same applicable scenarios through both channels; a scenario that passes
on one should pass on the other. Select the CLI channel for behavior that only a
real process can expose. CLI scenarios are slow under the test strategy and run
with `make slow`; in-process scenarios run in the default fast suite. The
drivers need a real application entry point and test environment before
scenarios can exercise wio-eval through them.
