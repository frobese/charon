# Copyright (C) frobese GmbH - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Hans Goedeke <hgoedeke@frobese.de>, August 2017

# coding=utf-8
# !/usr/bin/env python3.5

import pytest
import itertools

from charon.matched import matched


def imap_test_data():
    from charon.connector import _imap_connector

    iconn = _imap_connector()
    data = []
    if iconn.connect():
        for mbox in ['matched', 'unmatched']:
            for _, msg in iconn._fetch('ALL', mbox):
                    data.append((msg, mbox))
    else:
        pytest.fail("IMAP connection failed")
    return data


@pytest.mark.parametrize("msg, mbox", imap_test_data())
def test_matching(msg, mbox):
    match_obj = matched(msg)
    if (mbox == 'matched'):
        assert match_obj.is_matched
    else:
        assert not match_obj.is_matched


def timere_data():
    from data import time_re_data
    data = time_re_data
    for (i1, r1), (i2, r2) in itertools.combinations(time_re_data, 2):
        data.append((i1 + " " + i2, r1 + r2))
    return data


@pytest.mark.parametrize("input, result", timere_data())
def test_time_re(input, result):
    exp = matched.time_re
    assert list(map(str.strip, exp.findall(input))) == result
