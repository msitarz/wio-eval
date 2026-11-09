# SPDX-License-Identifier: Apache-2.0
"""Fixtures shared by tests."""

from typing import TYPE_CHECKING

import pytest

from tests.sandbox import Sandbox

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def sandbox(tmp_path: Path) -> Sandbox:
    """Give a test a temporary working directory and private environment."""
    return Sandbox.under(tmp_path)
