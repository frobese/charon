# coding=utf-8
# !/usr/bin/env python3.5

import email
import re

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Betreff: Urlaub / Krankheit / Verspätung

# Datum/ Zeitraum*: TT.MM.JJ – TT.MM.JJ / XX Minuten
# Grund: Freitext (optional)
# Zu benachrichtigender Ansprechpartner*: Anrede; Name; Mailadresse
# Name Mitarbeiter*: Vorname; Nachname

TEMPLATE = """Sehr geehrte Damen und Herren,

Herr/Frau {} wird am {} {}sbedingt nicht im Projekt sein.

Diese Nachricht wurde maschinell erzeugt.
----
frobese GmbH
Andertensche Wiese 14
D-30169 Hannover

Rechtsform: GmbH
Amtsgericht Hannover, Handelsregister: HRB 60066
Vertretungsberechtigte Geschäftsführer:
Dr. Dirk Frobese, Dr. Jochen Böhnke
"""


class matched:
    _date_subexp = r'(?:^|\s)(?:0?[1-9]|[1-3][0-9])\.(?:0?[1-9]|1[0-2])\.(?:(?:\d\d){1,2})?(?!\d)'
    time_re = re.compile(
        r'(?<!\-){}(?:\s-{})?'.format(_date_subexp, _date_subexp)
    )
    reason_re = re.compile(r'(krankheit|urlaub)')
    contact_re = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
    employee_re = re.compile(r'(?<=\:)(?:\w+\s?)+(?:\,\s?\w+)?', re.UNICODE)

    pars_lib = [
        (["datum", "zeitraum"],
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
            'DATE'),
        (["grund"],
            reason_re,
            lambda line: line.lower().replace('krank', 'krankheit'),
            'REASON'),
        (["ansprechpartner", "benachricht"],
            contact_re,
            lambda line: line.lower(),
            'CONTACT'),
        (["mitarbeiter"],
            employee_re,
            lambda line:
                re.sub(
                    r'(?:;\s*|\s?(Herr|Frau)\s?)', ' ', re.sub(
                        r'\:\s*\+?\s*', ":", line.title()
                    )
                ),
            'EMPLOYEE')
    ]

    subject_lib = [
        ('urlaub', 'urlaub'),
        ('krank', 'krankheit')
    ]

    def __init__(self, msg):
        self.msg = msg
        # TODO could be generated from the pars_lib
        self.results = {
            'DATE': [],
            'REASON': [],
            'CONTACT': [],
            'EMPLOYEE': [],
        }

        self.payload = self.fetch_payload(msg)
        self.match_payload(self.payload)

        subj = self.match_subject(msg['subject'])
        if not self.results['REASON'] and subj:
            self.results['REASON'].append(subj)

    def __str__(self):
        ret = ""
        template = "{}: {}\n"
        for key, val in self.results.items():
            ret += template.format(key, ", ".join(val) or "<->")
        return ret

    def debug_output(self):
        ret = "{} -- matched: {}\n".format(self.msg['subject'][:20], self.is_matched)
        ret += str(self)
        ret += self.mismatch_reason()
        ret += "+++ Automatic Message Mail " + "=" * 30 + "\n"
        ret += self.string_respone()
        ret += "+++ Postproccesed Mail " + "=" * 30 + "\n"
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
            ", ".join(self.results['REASON'][:1]))
        return txt

    def msg_response(self, report=False):
        msg = MIMEMultipart()

        if self.is_matched:
            msg.attach(MIMEText(self.string_respone()))
        elif not report:
            # its not ma match and its not a report
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
        return (
            ([] not in self.results.values())
            and ([""] not in self.results.values())
            and len(self.results['EMPLOYEE']) == 1
            and len(self.results['REASON']) == 1)

    def mismatch_reason(self):
        reason = ""
        for key, val in self.results.items():
            if len(val) == 0:
                reason += "{} hat keine einträge".format(key)
            if (key == 'EMPLOYEE' or key == 'REASON') and len(val) > 1:
                reason += "{} hat zu viele einträge".format(key)
        return reason + '\n'

    def match_subject(self, subject):
        for buzz, reason in self.subject_lib:
            if buzz in subject.lower():
                return reason
        else:
            return None

    def match_payload(self, payload):
        comp = self.post_process(payload)
        for line in comp:
            for buzzw, regex, post_proc, res_key in self.pars_lib:
                if any(buzz in line.lower() for buzz in buzzw):
                    self.results[res_key].extend(
                        map(
                            str.strip,
                            regex.findall(post_proc(line))
                        )
                    )

    @property
    def recipient(self):
        return ", ".join(self.results['CONTACT'])

    def post_process(self, payload):
        buzzwords = [buzz for subli, _, _, _ in self.pars_lib for buzz in subli]
        cut_words = ["gruß", "freundlich", "kind", "grüß"]
        lines = [li for li in payload.splitlines() if li.strip(' >') is not '']
        compressed = [""]

        for line in lines:
            line = re.sub(r'(?:^>+|<mailto:.+>|\*)', "", line)
            # line = re.sub(r'^>+', "", line)
            if any(buzz in line.lower() for buzz in buzzwords):
                compressed.append(line)
            elif (line.strip('-').strip(' ') == "" or
                    any(mw in line.lower() for mw in cut_words)):
                break
            else:
                compressed[-1] += " + " + line
        return [re.sub(
            r'\*?:\*?\s', ':', re.sub(r'\s\s+', " ", line)) for line in compressed]

    def fetch_payload(self, msg):
        if msg.is_multipart():
            return self.fetch_payload(msg.get_payload()[0])
        elif "multi" in msg.get_content_type():
            return self.fetch_payload(email.message_from_string(msg.get_payload()))
        elif msg['Content-Transfer-Encoding'] in ['base64', 'quoted-printable']:
            try:
                payload = msg.get_payload(decode=True).decode('utf-8')
            except:
                payload = msg.get_payload(decode=True).decode('unicode_escape')
            if "html" in msg['Content-Type']:
                payload = payload.replace('<br>', '\n').replace('</span>', '\n')
                return re.sub(r'<.*?>', '', payload)
            return payload
        return msg.get_payload()
