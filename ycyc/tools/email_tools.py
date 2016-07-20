#!/usr/bin/env python
# encoding: utf-8

from collections import namedtuple
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.header import Header
import os
import six

from ycyc.base.typeutils import SimpleExceptions, constants
from ycyc.base.filetools import bytes_from

SimpleExceptions = SimpleExceptions()
EMailSendFailed = SimpleExceptions.EMailSendFailed

Attachments = namedtuple("Attachments", ["name", "path"])


class EMail(object):
    SubType = constants(
        Plain="plain",
        HTML="html",
    )

    def __init__(
        self, server, sender=None, receiver=None, subject="", content="",
        subtype="plain", charset="utf-8",
    ):
        if isinstance(receiver, basestring):
            receiver = [receiver]

        self.server = server
        self.sender = sender
        self.receiver = receiver or []
        self.subject = subject
        self.content = content
        self.subtype = subtype
        self.charset = charset
        self.attachment_paths = []

    @property
    def mail(self):
        mail = MIMEMultipart()
        mail['Subject'] = Header(self.subject, self.charset)
        mail['From'] = Header(self.sender, self.charset)
        mail['To'] = Header(",".join(self.receiver), self.charset)
        mail.attach(MIMEText(self.content, self.subtype, self.charset))

        for i in self.attachment_paths:
            attachment = MIMEApplication(bytes_from(i.path))
            attachment.add_header(
                "Content-Disposition",
                "attachment",
                filename=i.name.strip(),
            )
            mail.attach(attachment)
        return mail

    def send(self, passwd=None, user=None):
        server = smtplib.SMTP(self.server)
        user = user or self.sender
        if passwd:
            server.login(user, passwd)

        try:
            server.sendmail(user, self.receiver, self.mail.as_string())
        except smtplib.SMTPRecipientsRefused as e:
            six.raise_from(EMailSendFailed, e)
        finally:
            server.close()

    def add_attachment(self, path, name=None):
        if not name:
            _, name = os.path.split(path)
        self.attachment_paths.append(Attachments(name, path))
