<!-- wio
code = "CST002"
name = "name-the-verification-level"
-->

For every non-functional requirement, say whether the Work itself, an
architectural integration or the full system verifies it, and name the verifier;
a child's local check never claims the system-level guarantee, which the parent
verifies.

Why: A requirement whose verifier is unnamed is verified by nobody, and a route
that is fast alone says nothing about the service under its full workload.
