# SPDX-License-Identifier: Apache-2.0
"""The data and interface shared by acceptance test drivers."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass(frozen=True)
class RunResult:
    """The output streams and exit status of one command invocation."""

    stdout: str
    stderr: str
    exit_code: int


class Driver(Protocol):
    """Run a command and return data for the scenario to assert on."""

    def run(self, args: Sequence[str]) -> RunResult:
        """Run a command with the arguments after its program name."""
        ...
