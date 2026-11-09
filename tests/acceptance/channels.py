# SPDX-License-Identifier: Apache-2.0
"""Channels through which acceptance scenarios reach wio-eval."""

from enum import Enum


class Channel(Enum):
    """A way to run an acceptance scenario."""

    IN_PROCESS = "in_process"
    CLI = "cli"
