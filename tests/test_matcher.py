# coding=utf-8
# !/usr/bin/env python3.5

import pytest
import itertools

from matched import matched


def imap_test_data():
    from connector import imap_connector

    iconn = imap_connector()
    data = []
    if 'OK' == iconn.connect()[0]:
        for mbox in ['matched', 'unmatched']:
            for _, msg in iconn._fetch('ALL', mbox).items():
                    data.append((msg, mbox))
    else:
        pytest.fail("IMAP connection failed")
    return data


@pytest.mark.parametrize("msg, mbox", imap_test_data())
def test_matching(msg, mbox):
    match_obj = matched(msg)
    assert (match_obj.is_matched) == (mbox == 'matched')


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
