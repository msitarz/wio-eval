<!-- wio
code = "UPK002"
name = "correct-diagrams-to-the-implementation"
-->

When the verified implementation differs from a diagram in the contract, stop
and ask the driver to ratify the contract through the ratify action, whose
`review-ratify` gate checks that no guarantee changed, instead of editing the
contract from the delivery stage.

Why: A stale diagram is believed over the code by every reader who does not
check. The driver decides on changes to a contract, and a ratify keeps the
correction visible and reviewed without making the delivered stages stale.
