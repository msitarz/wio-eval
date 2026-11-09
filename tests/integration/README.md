# wio-eval integration tests

How to write an integration test. It adds to the [test strategy](../README.md),
which says when a test is an integration test and what its subject is. Fake only
what is not the subject. A fake that unit tests also use lives in
`tests/fakes.py`, and an integration test never imports a unit test.
`tests/integration/` mirrors `src/wio_eval/`.
