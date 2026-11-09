<!-- wio
code = "UPK001"
name = "false-assumption-amends-the-contract"
-->

When an assumption proves false, stop and ask the driver to amend the contract
through the amend action, instead of working around it in the code.

Why: A workaround hides the changed intent from every reader of the contract,
and the next stage builds on the wrong premise. An amendment also makes the
delivered stages stale, so they are proposed again.
