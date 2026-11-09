# SPDX-License-Identifier: Apache-2.0
"""The acceptance driver for a command in a subprocess."""

import subprocess
from typing import TYPE_CHECKING

from tests.acceptance.drivers.base import RunResult

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from tests.sandbox import Sandbox


class CliDriver:
    """Run an explicitly supplied command in an isolated test environment."""

    def __init__(self, command: Path, sandbox: Sandbox) -> None:
        """Remember the command and the test's working directory and environment."""
        self._command = command
        self._sandbox = sandbox

    def run(self, args: Sequence[str]) -> RunResult:
        """Return the command's output streams and exit status."""
        result = subprocess.run(
            [str(self._command), *args],
            cwd=self._sandbox.root,
            env=self._sandbox.env,
            capture_output=True,
            text=True,
            check=False,
        )
        return RunResult(result.stdout, result.stderr, result.returncode)
