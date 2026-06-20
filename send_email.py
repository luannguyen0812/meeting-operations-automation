#!/usr/bin/env python3
"""Send meeting minutes via direct SMTP (Mailcow)."""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from config import PROJECTS

SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.yourprovider.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', 'your.email@yourcompany.com')
SMTP_PASS = os.getenv('SMTP_PASS', '')


def send_minutes_email(to_emails, project_name, date_str, body_text, attachment_path=None):
    """Send completed minutes to project team via SMTP."""
    subject = f'[{project_name}] — Meeting Minutes [{date_str}]'

    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = ', '.join(to_emails) if isinstance(to_emails, list) else to_emails
    msg['Subject'] = subject

    msg.attach(MIMEText(body_text, 'plain'))

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, 'rb') as f:
            part = MIMEBase('application', 'vnd.openxmlformats-officedocument.wordprocessingml.document')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
            msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            recipients = to_emails if isinstance(to_emails, list) else [to_emails]
            server.sendmail(SMTP_USER, recipients, msg.as_string())
        print(f'✓ Email sent: {subject}')
        return True
    except Exception as e:
        print(f'✗ Email failed: {subject}')
        print(f'  Error: {e}')
        return False


def test_smtp():
    """Send a test email to verify SMTP works."""
    global SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.yourprovider.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASS = os.getenv('SMTP_PASS')

    return send_minutes_email(
        to_emails=[SMTP_USER],
        project_name='Test Project',
        date_str='2026-06-17',
        body_text='This is a test email. If you received this, SMTP is working correctly.',
    )


if __name__ == '__main__':
    test_smtp()
