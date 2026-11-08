# SPDX-License-Identifier: Apache-2.0
"""Check that Mermaid source on standard input renders.

`rumdl` runs this once per `mermaid` code block (see `code-block-tools` in
`pyproject.toml`). It proves the diagram parses and renders, not that it is
right.
"""

import sys
from typing import Literal

import mermaidx


def main() -> Literal[0, 1]:
    """Render standard input as an SVG, in memory, to validate it.

    Returns:
        0 when the diagram renders, 1 when the renderer rejects the source.
    """
    source = sys.stdin.read()
    try:
        mermaidx.render(source, backend="quickjs").svg()
    except RuntimeError as error:
        sys.stderr.write(f"{error}\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
