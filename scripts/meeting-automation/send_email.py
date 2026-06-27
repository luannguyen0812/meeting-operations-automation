#!/usr/bin/env python3
"""Send meeting minutes via direct SMTP (Mailcow)."""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from config import PROJECTS

SMTP_HOST = os.getenv('SMTP_HOST', 'mail.intrastack.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', 'luan.nguyen@intrastack.com')
SMTP_PASS = os.getenv('SMTP_PASS', '')


CC_ALWAYS = ['stefan.nguyen@intrastack.com']


def send_minutes_email(to_emails, project_name, date_str, body_text,
                       attachment_path=None, attachment_bytes=None, attachment_filename=None,
                       cc_emails=None):
    """Send completed minutes to project team via SMTP.
    Pass either attachment_path (file on disk) or attachment_bytes + attachment_filename.
    """
    subject = f'[{project_name}] — Meeting Minutes [{date_str}]'

    cc = list(CC_ALWAYS)
    if cc_emails:
        cc += [e for e in cc_emails if e not in cc]

    msg = MIMEMultipart()
    msg['From'] = SMTP_USER
    msg['To'] = ', '.join(to_emails) if isinstance(to_emails, list) else to_emails
    msg['CC'] = ', '.join(cc)
    msg['Subject'] = subject

    msg.attach(MIMEText(body_text, 'plain'))

    if attachment_bytes and attachment_filename:
        ext = os.path.splitext(attachment_filename)[1].lower()
        mime_sub = 'pdf' if ext == '.pdf' else 'vnd.openxmlformats-officedocument.wordprocessingml.document'
        part = MIMEBase('application', mime_sub)
        part.set_payload(attachment_bytes)
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{attachment_filename}"')
        msg.attach(part)
    elif attachment_path and os.path.exists(attachment_path):
        ext = os.path.splitext(attachment_path)[1].lower()
        mime_sub = 'pdf' if ext == '.pdf' else 'vnd.openxmlformats-officedocument.wordprocessingml.document'
        with open(attachment_path, 'rb') as f:
            part = MIMEBase('application', mime_sub)
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(attachment_path)}"')
            msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            recipients = (to_emails if isinstance(to_emails, list) else [to_emails]) + cc
            server.sendmail(SMTP_USER, recipients, msg.as_string())
        print(f'✓ Email sent: {subject}')
        return True
    except Exception as e:
        print(f'✗ Email failed: {subject}')
        print(f'  Error: {e}')
        return False


def test_smtp():
    """Send a test email to verify SMTP works."""
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env.intrastack')
    load_dotenv(env_path)

    global SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS
    SMTP_HOST = os.getenv('SMTP_HOST', 'mail.intrastack.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USER = os.getenv('SMTP_USER')
    SMTP_PASS = os.getenv('SMTP_PASS')

    return send_minutes_email(
        to_emails=['minhluan081294@gmail.com'],
        project_name='Test Project',
        date_str='06.17.2026',
        body_text='This is a test email from Sparky. If you got this, SMTP is working.',
    )


if __name__ == '__main__':
    test_smtp()
