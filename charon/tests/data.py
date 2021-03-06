# Copyright (C) frobese GmbH - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Hans Goedeke <hgoedeke@frobese.de>, August 2017

# coding=utf-8
# !/usr/bin/env python3.5

time_re_data = [
    ("1.", []),
    ("01.", []),
    ("1.2", []),
    ("1.2.", ["1.2."]),
    ("1.2.1", []),
    ("1.2.12", ["1.2.12"]),
    ("01.2.12", ["01.2.12"]),
    ("01.02.12", ["01.02.12"]),
    ("01.20.12", []),
    ("50.2.12", []),
    ("1.2.112", []),
    ("01.2.112", []),
    ("01.02.112", []),
    ("01.20.112", []),
    ("50.2.112", []),
    ("1.2.2012", ["1.2.2012"]),
    ("01.2.2012", ["01.2.2012"]),
    ("01.02.2012", ["01.02.2012"]),
    ("01.20.2012", []),
    ("50.2.2012", []),
]
