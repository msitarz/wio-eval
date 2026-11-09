# SPDX-License-Identifier: Apache-2.0
"""Helpers for running Git in a test sandbox."""

import os
import subprocess
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest

    from tests.sandbox import Sandbox


def git(
    sandbox: Sandbox, *args: str, check: bool = False
) -> subprocess.CompletedProcess[str]:
    """Run Git in the sandbox's working directory and environment."""
    return subprocess.run(
        ["git", *args],
        cwd=sandbox.root,
        env=sandbox.env,
        capture_output=True,
        text=True,
        check=check,
    )


def enter(sandbox: Sandbox, monkeypatch: pytest.MonkeyPatch) -> None:
    """Use the sandbox's directory and environment until pytest restores them."""
    for name in set(os.environ) - set(sandbox.env):
        monkeypatch.delenv(name)
    for name, value in sandbox.env.items():
        monkeypatch.setenv(name, value)
    monkeypatch.chdir(sandbox.root)
