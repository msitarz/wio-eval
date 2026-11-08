# SPDX-License-Identifier: Apache-2.0
import pytest

from wio_eval.hello import hello


def test_hello():
    assert hello() == "world"


@pytest.mark.slow
def test_hello_slow():
    assert hello() == "world"
