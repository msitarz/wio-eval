<!-- wio
code = "DOC002"
name = "describe-the-current-state"
-->

Describe in a `README.md` its directory as it is now, with its architecture,
its conventions and the reasons behind them, and carry into that description
every guarantee of the promoted contract that the source does not state, or tell
the driver which one is dropped and why.

Why: A contract describes a change and goes stale once delivered, while a README
that describes the current state lets an agent work in the directory without
reading a contract and stays true as later Works edit it; a guarantee left out
of it is lost once the contract is retired.
