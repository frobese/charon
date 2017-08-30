# Copyright (C) frobese GmbH - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Hans Goedeke <hgoedeke@frobese.de>, August 2017

# coding=utf-8

from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG

from conf_local import *

HOST = "www.frobese.de"
IMAP_PORT = 993
SMTP_PORT = 587
INPUTMAILBOX = "INBOX"

REPORT_RECIPIENTS = [
    "nbomsdorf@frobese.de", "singelmann@frobese.de",
    "hgoedeke@frobese.de", "smeyer@frobese.de"
]

REPLYTO_ADRESS = "nbomsdorf@frobese.de"

TEST_DATA = "./subset"

LOG_LEVEL=DEBUG
