# SPDX-License-Identifier: Apache-2.0
"""Acceptance channel selection."""

import pytest

from tests.acceptance.channels import Channel


def test_default_channel_is_in_process(channel: Channel) -> None:
    """An unmarked scenario uses the in-process channel."""
    # Given an unmarked scenario

    # When it requests its channel
    selected = channel

    # Then it gets the in-process channel
    assert selected is Channel.IN_PROCESS


@pytest.mark.channels(Channel.IN_PROCESS, Channel.CLI)
def test_selected_channel_is_available(channel: Channel) -> None:
    """A marked scenario receives each selected channel."""
    # Given a scenario selecting both channels

    # When it requests its channel
    selected = channel

    # Then it receives one of the selected channels
    assert selected in (Channel.IN_PROCESS, Channel.CLI)
