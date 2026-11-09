# AGENTS.md

wio-eval is a standalone, harness-agnostic experiment execution and
observability engine for AI coding agents. It runs experiments and preserves
evidence; external evaluators decide whether outcomes are good. The repository
is an early scaffold, so distinguish intended capabilities from implemented
ones.

Use the terms defined in [GLOSSARY.md](GLOSSARY.md) in code, docs and commit
messages. A `GLOSSARY.md` in a directory binds its terms to that directory and
its descendants, and the nearest one wins. A `README.md` covers its directory
and descendants; a nearer one adds to a farther one and never overrides it. See
[README.md](README.md) for the overview and [tests/README.md](tests/README.md)
for the test strategy.

## Commands

Use `make` for whole-project work (`make help` lists the targets) and `uv run`
for single tools. The checks are defined in `prek.toml` (hooks) and
`pyproject.toml` (tool settings), and the `make` targets only call them.

- `make install`: sync the environment (`uv sync --locked`) and install the git
  hooks (pre-commit and commit-msg). Run it once per clone.
- `make check`: run every hook and the fast tests on all files. Run it before
  declaring work done.
- `make lint`: every hook except pytest.
- `make test`: the fast tests, with the coverage gate (95%).
- `make build`: the slow packaging tests, which build the wheel and sdist and
  verify them.
- `make slow`: every slow test, the packaging tests included. A test is slow
  when it spawns a subprocess (git, the CLI) or builds the package. CI runs
  this target.
- `make secrets`: scan the full git history with gitleaks.
- `make audit`: check the locked dependencies for known vulnerabilities (needs
  network; uv's `audit` command is experimental).

Single tools, for quick feedback:

- `uv run pytest`: the fast tests in random order. Add `-p no:randomly` to
  debug, `-k name` to select, `-m slow` to run the slow tests instead, and
  `-m unit`, `-m integration` or `-m tooling` to run one group of tests (see
  [tests/README.md](tests/README.md)).
- `uv run ruff check --fix` and `uv run ruff format`: lint and format Python.
- `uv run pyrefly check`: strict type check of `scripts`, `src` and `tests`.
- `uv run complexipy src tests`: cognitive complexity.
- `uv run tach check`: check the dependency direction between the packages of
  `src/wio_eval`, and between `scripts` and the groups of `tests` (`tach.toml`),
  counting `TYPE_CHECKING` imports.
- `uv run jscpd src tests`: duplicate code.
- `uv run rumdl check --fix`: lint and format Markdown, and check that every
  Mermaid block renders (`scripts/check_mermaid.py`). A diagram that renders
  can still be wrong.
- `uv add <package>` or `uv add --dev <package>`: change dependencies. Never
  edit `uv.lock` by hand.

## Code conventions

- Start every Python file with `# SPDX-License-Identifier: Apache-2.0` as the
  first line (second after a shebang). Ruff enforces it (`CPY001`).
- Annotate everything, tests included. Run `pyrefly` before declaring done.
- Give every test `# Given`, `# When` and `# Then` comments, in that order, each
  describing its section (see `tests/README.md`).
- Write a Google-style docstring for every module, class and function, private
  helpers too. Ruff enforces it only for public names.
- A `.pyi` stub carries a docstring for each item. Stubs are the architecture
  spec, so say what each item guarantees.
- Write output with `sys.stdout`, not `print`.
- Keep functions small: McCabe complexity 10, cognitive complexity 7, 20
  statements, 3 boolean operands per `if`. Prefer `match` with named guards over
  long `if` chains, and model variants as algebraic data types.
- Python lines are 88 columns. Markdown lines are 80.
- Repository files state intent: what holds and why. They never record
  verification, such as the runs, counts or revisions something was checked
  against: CI and prek verify. Report a manual check to the driver or in a
  commit message. A contract's criteria, which say how a reviewer judges them,
  are the exception.
- Fix the cause when a check fails. Never weaken a test or loosen a rule to get
  green. If a rule seems wrong, say so and propose a config change.

## Workflow

Follow [docs/workflow.md](docs/workflow.md) for work requiring a contract.
Use it manually while wio automation is under development.

- Commit messages follow Conventional Commits. The commitizen hook checks them.
- End each commit message with a `Wio-*` trailer paragraph identifying its Work,
  action and stage; use `Wio-Work: none` for a commit outside a Work. For
  several Works with identical remaining fields, list their ids separated by a
  comma and one space, dependencies and children first. Otherwise use separate
  paragraphs. The commit-msg hook checks record shape. Until `wio trailers`
  exists, write records by hand.

  ```text
  Wio-Work: k3m9xq
  Wio-Action: deliver
  Wio-Stage: architecture
  Wio-Items: AC-1, AC-3
  ```

  | Trailer | Meaning |
  | --- | --- |
  | `Wio-Work` | A Work id, a comma-separated list of ids, or `none`. |
  | `Wio-Action` | The action, such as `define` or `deliver`. |
  | `Wio-Stage` | The stage the commit works on. |
  | `Wio-Items` | Optional item ids addressed, such as `AC-1`. |
  | `Wio-Result` | For a gate: `pass`, `fail` or `unknown`. |
  | `Wio-Judge` | For a gate with a result: `agent` or `human`. |

- Never skip hooks (`--no-verify`).
- Commit when a step is done and checks pass. Keep commits small, one concern
  each.
- Changes with no design decisions need no Work contract. When in doubt, ask.
- Push and open pull requests only when asked. Never push to `main`: work on a
  branch, run `make check`, push the branch and use `gh pr create`.
- The pull request title is a Conventional Commit. Squash merging makes it the
  commit on `main`, and CI checks it.
- Fill in `.github/PULL_REQUEST_TEMPLATE.md` and delete every HTML comment from
  the body. The Records workflow copies commit records into the body for squash
  merges. For a PR from a fork, paste the records shown in the job summary.
