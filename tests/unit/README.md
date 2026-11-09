# wio-eval unit tests

How to write a unit test. It adds to the [test strategy](../README.md), which
says when a test is a unit test, and covers what a unit test runs, how far it
reaches into a module and where its fakes live.

## 1. What a unit test runs

A unit test runs the logic of one component against fakes of its ports. This is
what ports and adapters buy: the logic runs fast and deterministically, without
git, a disk or the environment, and the adapters are tested apart in
`tests/integration/`. A function with many small inputs and expected outputs,
such as a parser or a validation, is a parametrized table.

`tests/unit/` mirrors `src/wio_eval/`.

## 2. How far a test reaches

Drive the logic through the component's public entry first. Call a function of
a module on its own, a private one included, when the public entry cannot reach
a case without a lot of setup, or when a table of inputs makes the cases clear.
A test of a helper that only raises coverage couples the test to the code and
breaks on a harmless refactor, so look for the case it misses first.

## 3. Fakes

A fake lives in a `fakes.py` beside the tests that use it, such as
`tests/unit/planning/fakes.py`, so it is easy to find. When another package
needs the same fake, move it up one level: to `tests/unit/fakes.py` when several
unit packages use it, and to `tests/fakes.py` when unit and integration tests
both do. Integration tests never import unit tests, so a fake they need is never
under `tests/unit/`.
