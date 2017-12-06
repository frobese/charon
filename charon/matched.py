# Copyright (C) frobese GmbH - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential
# Written by Hans Goedeke <hgoedeke@frobese.de>, August 2017

# coding=utf-8
# !/usr/bin/env python3.5

import logging

import email
import re

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import format_datetime, localtime

# Betreff: Urlaub / Krankheit / Verspätung

# Datum/ Zeitraum*: TT.MM.JJ – TT.MM.JJ / XX Minuten
# Grund: Freitext (optional)
# Zu benachrichtigender Ansprechpartner*: Anrede; Name; Mailadresse
# Name Mitarbeiter*: Vorname; Nachname

TEMPLATE = """Sehr geehrte Damen und Herren,

Herr/Frau {} wird am {} {}sbedingt nicht im Projekt sein.

{}
"""

class matched:
    _date_subexp = r'(?:^|\s)(?:0?[1-9]|[1-3][0-9])\.(?:0?[1-9]|1[0-2])\.(?:(?:\d\d){1,2})?(?!\d)'
    time_re = re.compile(
        r'(?<!\-){}(?:\s-{})?'.format(_date_subexp, _date_subexp)
    )
    reason_re = re.compile(r'(?<=\:)(krankheit|urlaub|schulung)')
    contact_re = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
    employee_re = re.compile(
        r'(?<=\:)(?:\s?\w+){1,3}(?:\,\s?\w+)?(?:\W|$)(?!\w)', re.UNICODE)
    # halftime_re = re.compile(r'(?<=\:)\s?(?:vormittag|nachmittag)')

    pars_lib = [
        (
            ["datum", "zeitraum"],
            time_re,
            lambda line:
                (re.findall(
                    r'(?<=\:)(?:[\d\-\,\.\+\&\;\/\s(?:\sMinuten\s)]*$)',
                    re.sub(
                        r'\s*\-\s*', " - ",
                        line.replace(
                            "bis", '-').replace(
                            chr(8211), '-').replace(
                            "heute", "").replace(
                            "und", "").replace(
                            chr(150), "")
                            )
                    )+[""])[0],
            'DATE',
            lambda result:
                len(result) >= 1 and result != [""]
        ),
        (
            ["grund"],
            reason_re,
            lambda line: line.lower().replace('krank', 'krankheit'),
            'REASON',
            lambda result:
                len(result) == 1 and result != [""]
        ),
        (
            ["ansprechpartner", "benachricht"],
            contact_re,
            lambda line: line.lower(),
            'CONTACT',
            lambda result:
                len(result) >= 1 and result != [""]
        ),
        (
            ["mitarbeiter"],
            employee_re,
            lambda line:
                re.sub(
                    r'(?:;\s*|\s?(Herr|Frau)\s?)', ' ', re.sub(
                        r'\:\s*\+?\s*', ":", line.title()
                    )
        ),
            'EMPLOYEE',
            lambda result:
                len(result) == 1 and result != [""]
        ),
        #  (
        #      ["halbtags"],
        #      halftime_re,
        #      lambda line: line.lower(),
        #      'HALVTIME',
        #      lambda result:
        #          (len(result) == 1 and result != [""]) or len(result) == 0
        #  ),
    ]

    subject_lib = [
        ('urlaub', 'urlaub'),
        ('krank', 'krankheit')
    ]

    def __init__(self, msg, keep_attachment, footer=""):
        logging.debug('MATCHER - init {}'.format(msg['subject']))
        self.msg = msg
        self.footer = footer
        self.results = {key: list() for _, _, _, key, _ in self.pars_lib}

        logging.info('MATCHER - fetching payload')
        self.payload = self._fetch_payload(msg)
        self.match_payload(self.payload)
        if keep_attachment:
            self.attachment = self._fetch_attachment(msg)
        else:
            self.attachment = None

        subj = self._match_subject(msg['subject'])
        if not self.results['REASON'] and subj:
            self.results['REASON'].append(subj)
        logging.debug('MATCHER - done.')

    def __str__(self):
        ret = ""
        template = "{}: {}\n"
        for key, val in self.results.items():
            ret += template.format(key, ", ".join(val) or "<->")
        ret += self.mismatch_reason()
        return ret

    def debug_output(self):
        ret = "{} -- matched: {}\n".format(self.msg['subject'][:20], self.is_matched)
        ret += str(self)
        ret += "+++ Automatic Message Mail " + "=" * 30 + "\n"
        ret += self.string_respone()
        ret += "+++ Postprocessed Mail " + "=" * 30 + "\n"
        lines = [li.strip(' >') for li in self.payload.replace(
                '\n\n', '\n').splitlines()]
        for line in [li for li in lines if li is not ""]:
            if line.strip('-').strip() == '':
                break
            else:
                ret += line + "\n"
        return ret

    def string_respone(self):
        txt = TEMPLATE.format(
            ", ".join(self.results['EMPLOYEE'][:1]),
            ", ".join(self.results['DATE']),
            ", ".join(self.results['REASON'][:1]),
            self.footer)
        #  " {}s ".format(
        #      self.results['HALVTIME'][0]) if self.results['HALVTIME'] else " ")
        return txt 

    def msg_response(self, report=False):
        msg = MIMEMultipart()
        msg['Date'] = format_datetime(localtime())

        if self.is_matched:
            msg.attach(MIMEText(self.string_respone()))
            if self.attachment:
                msg.attach(self.attachment)
                logging.debug('MATCHER - attachment appended')
        elif not report:
            # its not ma match and its not a report
            logging.warning('MATCHER - unmatched response')
            return None

        if not report:
            msg['subject'] = "{} - {}".format(
                self.results['EMPLOYEE'][0], self.results['REASON'][0].title())
        else:
            msg.attach(MIMEText(str(self)))
            msg.attach(MIMEText(self.payload))
            if self.is_matched:
                msg['subject'] = "[MATCH] {}".format(self.msg['subject'])
            else:
                msg['subject'] = "[NO MATCH] {}".format(self.msg['subject'])

        return msg

    @property
    def is_matched(self):
        for _, _, _, key, validator in self.pars_lib:
            if not validator(self.results[key]):
                return False
        return True

    def mismatch_reason(self):
        reason = ""
        for key, val in self.results.items():
            if len(val) == 0:
                reason += "{} hat keine einträge".format(key)
            if (key == 'EMPLOYEE' or key == 'REASON') and len(val) > 1:
                reason += "{} hat zu viele einträge".format(key)
        return reason + '\n'

    def _match_subject(self, subject):
        for buzz, reason in self.subject_lib:
            if buzz in subject.lower():
                return reason
        else:
            return None

    def match_payload(self, payload):
        logging.info('MATCHER - matching payload')
        comp = self._pre_process(payload)
        for line in comp:
            for buzzw, regex, post_proc, res_key, _ in self.pars_lib:
                if any(buzz in line.lower() for buzz in buzzw):
                    logging.debug('MATCHER - match for {}'.format(res_key))
                    self.results[res_key].extend(
                        map(
                            str.strip,
                            regex.findall(post_proc(line))
                        )
                    )

    @property
    def recipient(self):
        return ", ".join(self.results['CONTACT'])

    def _pre_process(self, payload):
        logging.info('MATCHER - pre processing')
        buzzwords = [buzz for subli, _, _, _, _ in self.pars_lib for buzz in subli]
        cut_words = ["gruß", "freundlich", "kind", "grüß"]
        lines = [li for li in payload.splitlines() if li.strip(' >') is not '']
        compressed = [""]

        for line in lines:
            line = re.sub(r'(?:^>+|<mailto:.+>|\*)', "", line)
            if any(buzz in line.lower() for buzz in buzzwords):
                compressed.append(line)
            elif (line.strip('-').strip(' ') == "" or
                    any(mw in line.lower() for mw in cut_words)):
                break
            else:
                compressed[-1] += " + " + line
        return [re.sub(
            r'\*?:\*?\s', ':', re.sub(r'\s\s+', " ", line)) for line in compressed]

    def _fetch_payload(self, msg):
        if msg.is_multipart():
            logging.debug('MATCHER - regular multipart')
            return self._fetch_payload(msg.get_payload()[0])
        elif "multi" in msg.get_content_type():
            logging.info('MATCHER - irregular multipart')
            return self._fetch_payload(email.message_from_string(msg.get_payload()))
        elif msg['Content-Transfer-Encoding'] in ['base64', 'quoted-printable']:
            try:
                logging.debug('MATCHER - decoding (utf-8)')
                payload = msg.get_payload(decode=True).decode('utf-8')
            except:
                logging.info('MATCHER - decoding (unicode escape)')
                payload = msg.get_payload(decode=True).decode('unicode_escape')

            if "html" in msg['Content-Type']:
                logging.info('MATCHER - removing html artifacts')
                payload = payload.replace('<br>', '\n').replace('</span>', '\n')
                return re.sub(r'<.*?>', '', payload)
            return payload
        logging.debug('MATCHER - reached payload')
        return msg.get_payload()

    def _fetch_attachment(self, msg):
        for part in msg.walk():
            if "pdf" in part.get_content_type():
                logging.debug('MATCHER - attachment found')
                return part
        logging.warning('MATCHER - no attachment found')
        return MIMEText("No attachment was found")
