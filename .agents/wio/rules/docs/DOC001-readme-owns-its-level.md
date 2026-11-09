<!-- wio
code = "DOC001"
name = "readme-owns-its-level"
-->

State in a `README.md` only what is true at its directory's level, for that
directory and its descendants, and link to a farther `README.md` for what holds
above it; a nearer `README.md` adds to a farther one and never overrides it.

Why: A rule stated at the wrong level is copied into every sibling or missed by
every descendant, and if a nearer README could override a farther one, a reader
would have to compare every README on the path to know what holds.
