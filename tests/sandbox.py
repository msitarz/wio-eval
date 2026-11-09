# SPDX-License-Identifier: Apache-2.0
"""A temporary working directory and private environment for tests."""

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# Retain only variables needed to locate programs and support the host runtime.
_INHERITED = ("PATH", "SYSTEMROOT", "WINDIR", "TMPDIR", "TEMP", "TMP")
_GITCONFIG = "[core]\n\texcludesFile = /dev/null\n\tattributesFile = /dev/null\n"
_IDENTITY = {
    "NAME": "wio-eval test",
    "EMAIL": "wio-eval-test@example.invalid",
    "DATE": "2026-01-01T00:00:00+0000",
}


@dataclass(frozen=True)
class Sandbox:
    """A test's working directory and environment, independent of user config."""

    root: Path
    env: dict[str, str]

    @classmethod
    def under(cls, tmp_path: Path) -> Sandbox:
        """Create a working directory, home and isolated Git configuration."""
        root = tmp_path / "repo"
        root.mkdir(parents=True)
        home = tmp_path / "home"
        home.mkdir()
        gitconfig = tmp_path / "gitconfig"
        gitconfig.write_text(_GITCONFIG, encoding="utf-8")
        env = {key: os.environ[key] for key in _INHERITED if key in os.environ}
        env |= {
            "HOME": str(home),
            "USERPROFILE": str(home),
            "XDG_CONFIG_HOME": str(home / ".config"),
            "XDG_CACHE_HOME": str(home / ".cache"),
            "XDG_DATA_HOME": str(home / ".local" / "share"),
            "GIT_CONFIG_GLOBAL": str(gitconfig),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CEILING_DIRECTORIES": str(tmp_path.resolve()),
            "GIT_TERMINAL_PROMPT": "0",
        }
        for role in ("AUTHOR", "COMMITTER"):
            env |= {f"GIT_{role}_{key}": value for key, value in _IDENTITY.items()}
        return cls(root=root, env=env)
