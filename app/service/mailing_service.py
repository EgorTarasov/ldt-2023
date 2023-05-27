import smtplib
from typing import Any
from email.mime.text import MIMEText

import jinja2
from pydantic import EmailStr

from app.data import models
from app.utils.logging import log
from app.utils.settings import settings
from app.data.constants import MailingTemplate


SMTP_SERVER: smtplib.SMTP | None = None
TEMPLATES: jinja2.Environment | None = None


def init_email_service() -> smtplib.SMTP:
    global TEMPLATES
    server = smtplib.SMTP(settings.SERVICE_MAIL_HOST, settings.SERVICE_MAIL_PORT)
    TEMPLATES = jinja2.Environment(loader=jinja2.FileSystemLoader("app/templates"))
    server.starttls()
    try:
        server.login(settings.SERVICE_MAIL_USER, settings.SERVICE_MAIL_PASSWORD)
    except Exception as e:
        log.error(f"Can't connect to mail server: {e}")
        raise e
    finally:
        log.info("Connected to mail server")

    return server


def send_email(template: MailingTemplate, template_data: dict) -> None:
    # TODO: определиться с тем, какие данные будут приходить в data

    global SMTP_SERVER
    global TEMPLATES
    try:
        if not SMTP_SERVER:
            SMTP_SERVER = init_email_service()
        if not TEMPLATES:
            TEMPLATES = jinja2.Environment(
                loader=jinja2.FileSystemLoader("app/templates")
            )
        data = dict()
        data["template"] = TEMPLATES.get_template(template.value).render(
            **template_data
        )
        msg = MIMEText(data["template"], "html")
        msg["From"] = settings.SERVICE_MAIL_USER
        msg["To"] = data["to"]
        msg["Subject"] = data["subject"]
        SMTP_SERVER.sendmail(settings.SERVICE_MAIL_USER, data["to"], msg.as_string())
    except Exception as e:
        log.error(f"Can't send email: {e}")
        raise e


def create_mailing(
    targets: list[models.User], template: MailingTemplate
) -> None:
    for target in targets:
        send_email(template, template_data | {"to": target.email})


# def create_mailing(targets: models.User, )
# def main():
#     print(send_email())


# if __name__ == "__main__":
#     main()
