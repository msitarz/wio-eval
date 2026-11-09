# SPDX-License-Identifier: Apache-2.0
"""The facade used by acceptance scenarios, independent of their channel."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tests.acceptance.drivers.base import Driver, RunResult


@dataclass(frozen=True)
class WioEval:
    """Expose commands to scenarios through a test driver."""

    driver: Driver

    def run(self, args: Sequence[str]) -> RunResult:
        """Run a command and return data for the scenario to inspect."""
        return self.driver.run(args)
