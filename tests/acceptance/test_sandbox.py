# SPDX-License-Identifier: Apache-2.0
"""Isolation of test environments for both acceptance channels."""

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from tests.acceptance.drivers.in_process import InProcessDriver
from tests.sandbox import Sandbox

if TYPE_CHECKING:
    from collections.abc import Sequence

    from tests.acceptance.drivers.base import RunResult


def test_sandbox_excludes_credentials_and_git_redirects(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The sandbox does not inherit credentials or Git redirection."""
    # Given user credentials and a Git redirect in the process environment
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-secret")
    monkeypatch.setenv("GIT_DIR", "/outside/repo")

    # When a sandbox is created
    sandbox = Sandbox.under(tmp_path)

    # Then its environment uses a private home without those variables
    assert "ANTHROPIC_API_KEY" not in sandbox.env
    assert "GIT_DIR" not in sandbox.env
    assert Path(sandbox.env["HOME"]).is_relative_to(tmp_path)
    assert sandbox.env["GIT_CONFIG_NOSYSTEM"] == "1"


def test_in_process_restores_environment_after_failure(
    sandbox: Sandbox, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The driver restores the process state even if the entry point fails."""
    # Given a caller environment and an entry point that raises
    monkeypatch.setenv("WIO_EVAL_TEST_SENTINEL", "outside")
    original_directory = Path.cwd()

    def entry_point(args: Sequence[str]) -> RunResult:
        assert not args
        assert Path.cwd() == sandbox.root
        assert "WIO_EVAL_TEST_SENTINEL" not in os.environ
        message = "test failure"
        raise ValueError(message)

    driver = InProcessDriver(entry_point, sandbox)

    # When the entry point fails inside the sandbox
    with pytest.raises(ValueError, match="test failure"):
        driver.run([])

    # Then the caller's directory and environment are restored
    assert Path.cwd() == original_directory
    assert os.environ["WIO_EVAL_TEST_SENTINEL"] == "outside"
