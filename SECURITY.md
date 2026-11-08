# Security policy

## Supported versions

wio-eval is pre-alpha and has no releases yet. Security fixes land on `main`.

## Reporting a vulnerability

Please do not open a public issue for a security problem.

Report it privately through GitHub:
[Report a vulnerability](https://github.com/msitarz/wio-eval/security/advisories/new).

Include:

- what you found and where (file, command or workflow);
- steps to reproduce it, or a proof of concept;
- the impact you expect, and the version or commit you tested.

I will acknowledge the report and keep you updated while I look into it. This
is a personal project, so responses are best effort.

## Scope

wio-eval reads repository files and runs local tools on them, so reports about
unsafe handling of repository content, path traversal or command injection are
in scope. Problems in a third-party dependency are best reported to that
project, but tell me too if wio-eval is affected.
