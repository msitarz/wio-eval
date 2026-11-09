# SPDX-License-Identifier: Apache-2.0
"""The common command interface of acceptance drivers."""

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.acceptance.drivers.base import RunResult
from tests.acceptance.drivers.cli import CliDriver
from tests.acceptance.drivers.in_process import InProcessDriver
from tests.acceptance.dsl.wio_eval import WioEval

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tests.sandbox import Sandbox


def test_facade_returns_in_process_result(sandbox: Sandbox) -> None:
    """The facade passes arguments and returns the driver's data."""

    # Given an entry point that reports its arguments
    def entry_point(args: Sequence[str]) -> RunResult:
        return RunResult(",".join(args), "diagnostic", 3)

    # When a scenario runs a command through the facade
    output = WioEval(InProcessDriver(entry_point, sandbox)).run(["plan", "inspect"])

    # Then it receives the entry point's streams and status
    assert output == RunResult("plan,inspect", "diagnostic", 3)


@pytest.mark.slow
def test_cli_driver_captures_process_output(sandbox: Sandbox) -> None:
    """The CLI driver captures streams and exit status from a subprocess."""
    # Given a command and an isolated working directory
    driver = CliDriver(Path(sys.executable), sandbox)
    code = 'import sys; sys.stdout.write("out"); sys.stderr.write("err"); sys.exit(3)'

    # When it runs the command
    output = driver.run(["-c", code])

    # Then it returns both streams and the exit status
    assert output == RunResult("out", "err", 3)
