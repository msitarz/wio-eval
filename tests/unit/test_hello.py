# SPDX-License-Identifier: Apache-2.0
from wio_eval.hello import hello


def test_hello():
    assert hello() == "world"
