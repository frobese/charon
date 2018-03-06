# Copyright (C) frobese GmbH - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Hans Goedeke <hgoedeke@frobese.de>, August 2017

# coding=utf-8
# !/usr/bin/env python3.5

import pytest
import itertools

import sys
import os

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from matched import matched
from config import config

def imap_test_data():
    from connector import _imap_connector

    try:
        conf = config()
    except:
        pytest.fail("Config missing")

    iconn = _imap_connector(conf)
    data = []
    for mbox in ['matched', 'unmatched']:
        conf._conf['MAIL']['INPUTMAILBOX'] = mbox
        iconn = _imap_connector(conf)
        if iconn.connect():
            for _, msg in iconn._fetch('ALL'):
                data.append((msg, mbox))
        else:
            pytest.fail("IMAP connection failed")
    return data


@pytest.mark.parametrize("msg, mbox", imap_test_data())
def test_matching(msg, mbox):
    match_obj = matched(msg, False)
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
