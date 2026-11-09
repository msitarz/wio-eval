# SPDX-License-Identifier: Apache-2.0
"""The acceptance driver for an injected in-process entry point."""

import contextlib
import os
from typing import TYPE_CHECKING, Protocol
from unittest import mock

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tests.acceptance.drivers.base import RunResult
    from tests.sandbox import Sandbox


class EntryPoint(Protocol):
    """An in-process command entry point supplied by the test setup."""

    def __call__(self, args: Sequence[str]) -> RunResult:
        """Run a command and return its streams and exit status."""
        ...


class InProcessDriver:
    """Run commands in the current process through an injected entry point."""

    def __init__(self, entry_point: EntryPoint, sandbox: Sandbox) -> None:
        """Remember the entry point; wio-eval does not provide one yet."""
        self._entry_point = entry_point
        self._sandbox = sandbox

    def run(self, args: Sequence[str]) -> RunResult:
        """Return the result of the entry point without asserting on it."""
        with (
            contextlib.chdir(self._sandbox.root),
            mock.patch.dict(os.environ, self._sandbox.env, clear=True),
        ):
            return self._entry_point(args)
