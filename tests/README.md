# wio-eval test strategy

How wio-eval is tested. Written for a coding agent or human starting work in the
wio-eval repo. It covers the test layers, the directory layout and the
conventions.

## 1. Principles

- **Fast by default.** `uv run pytest` runs the fast tests, and `make slow`
  runs the slow ones.
- **Start small.** Add helpers and vocabulary only when a test needs them.
  Delete tests and helpers that have no observed failure behind them.

## 2. Test layers

| Layer | Location | Use for | Do not use for |
|---|---|---|---|
| Unit | `tests/unit/` (mirrors `src/wio_eval/`) | One component's logic run against fakes of its ports, and its functions on their own when a case is hard to reach through the public entry | Anything with something real behind it (integration); what a user sees (acceptance) |
| Integration | `tests/integration/` (mirrors `src/wio_eval/`) | Code with something real behind it: an adapter on real git or a real disk, the process's working directory and environment, a fresh interpreter (what an import loads), the installed command | Behaviour a user relies on (acceptance); input tables (unit) |
| Tooling | `tests/tooling/` | The repository's own configuration, layout and hygiene as its tools see them: lint rules probed with `ruff`, what git ignores, the stub rules of the ports, that the sources and the sample config agree with the models | The behaviour of wio-eval |
| Acceptance | `tests/acceptance/` (mirrors features) | Behaviour a user relies on: experiment planning, trial execution, evidence and results, recovery, exit codes | Exhaustive input tables, flag parsing details |
| Golden | `tests/golden/` (expected files only) | Byte-stable output (deterministic plans or result fixtures) | Anything with timestamps or ordering that is not deterministic. Update goldens deliberately and review the diff |

The `tests/packaging/` and `tests/scripts/` directories are two more groups,
for the built package and for the scripts of the repository.

**Which group a test belongs to.** Ask in this order, and take the first yes:

1. Does it assert on what a user sees, through the DSL or the CLI channel? It is
   an acceptance test: one independently assessable acceptance criterion, one
   scenario. Only when you write one, read the
   [acceptance test guide](acceptance/README.md).
2. Does it check a tool's configuration or the files of the repository, such as
   a lint rule, an ignored file or the layout of the sources? It is a tooling
   test.
3. Does something real stand behind the code it calls: git, files whose state it
   depends on, the working directory or the environment of the process, a fresh
   interpreter, the installed command? It is an integration test, however fast
   it runs.
4. Otherwise one module is tested with its collaborators replaced, and it is a
   unit test. A `tmp_path` directory that only gives the code an inert input
   does not make a unit test an integration test; a test that asserts on what
   the real disk does does.

A file that mixes the two is split: the unit tests stay in `tests/unit/...`, and
the rest moves to the same path under `tests/integration/` or `tests/tooling/`.

**Markers.** Every directory under `tests/` that holds tests is a group, and
its marker is its name, which `tests/conftest.py` sets from the path, so a test
never carries another group's marker by hand. A new group is a directory, a
registered marker and a module in `tach.toml`.

`slow` is separate from the group. It says that a test spawns a subprocess or
builds the package, and the default run leaves it out. An integration test with
only a temporary directory is not slow and runs by default.

Acceptance tests cover the execution engine and its observable evidence, not
semantic judgments about an agent’s output. Use controlled harness responses
for deterministic tests; real agent behaviour belongs to experiments.

## 3. Directory layout

`tests/` has one directory for each group of section 2, and `fixtures/` for the
static sample repos, experiment inputs and evidence. `conftest.py` holds the
fixtures that every test can ask for, `fakes.py` the fakes that unit and
integration tests share, `sandbox.py` the sandbox of a test, and `support.py`
what several groups need. The unit and integration directories mirror
`src/wio_eval/`.

## 4. Conventions

- Test names state the behaviour:
  `test_retry_does_not_create_an_extra_trial`.
- Every test has `# Given`, `# When` and `# Then` comments, in that order. Each
  comment describes its section in the domain's terms ("When its problems are
  computed"), not the code ("When calling `message_problems`"), so it stays
  true when names change. Assign the result in the When section and assert on
  it in the Then section, rather than computing inside the `assert`. A section
  may be empty only when there is nothing to put in it, and its comment stays
  (`# Given no setup`).
- A test that spawns a subprocess (git, the CLI) or builds the package is
  marked `slow`. `make slow` runs those tests, and CI runs that target.
- A test lives in the group its subject asks for (see section 2).
- Use `tmp_path` and the `sandbox` fixture for every repo, so a test never
  touches the developer's own state: the developer's agent credentials or git
  setup.
- No sleeps. No timestamps in compared output.
