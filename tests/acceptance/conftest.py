# SPDX-License-Identifier: Apache-2.0
"""Channel selection for acceptance scenarios."""

import pytest

from tests.acceptance.channels import Channel


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    """Parametrize marked scenarios and mark CLI invocations slow."""
    marker = metafunc.definition.get_closest_marker("channels")
    if marker is None:
        return
    params = [
        pytest.param(
            channel,
            id=channel.value,
            marks=[pytest.mark.slow] if channel is Channel.CLI else [],
        )
        for channel in marker.args
    ]
    metafunc.parametrize("channel", params)


@pytest.fixture
def channel() -> Channel:
    """Give unmarked scenarios the fast in-process channel."""
    return Channel.IN_PROCESS
