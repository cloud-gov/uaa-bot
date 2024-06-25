from email.mime.text import MIMEText
import os
import smtplib
import ssl

from email_validator import validate_email, EmailNotValidError
from jinja2 import Environment, PackageLoader, select_autoescape

from uaa_bot import config, templates

TEMPLATES = os.listdir(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "./templates")
)

TEMPLATE_ENV = Environment(
    loader=PackageLoader("uaa_bot", "templates"), autoescape=select_autoescape(["html"])
)


class Notifier:
    def __init__(self, email: str, smtp_config=config.smtp):
        self.smtp_config = smtp_config
        self.email = email
        self.template_env = TEMPLATE_ENV

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        try:
            valid = validate_email(value)
            self._email = valid.normalized
        except EmailNotValidError as e:
            raise (e)

    @property
    def smtp_config(self):
        return self._smtp_config

    @smtp_config.setter
    def smtp_config(self, value):
        smtp_config = {}
        for k, v in config.smtp.items():
            smtp_config[k] = value.get(k, v)
        self._smtp_config = smtp_config

    def get_email_subject(self, template_name: str):
        name = template_name.replace("_", " ")
        subject = f"Your cloud.gov {name}"

        return subject

    def get_template(self, template_name: str):
        name = str()

        # Add extension if template name given does not have one
        if len(template_name) > 5 and template_name[-4:] == "html":
            name = template_name
        else:
            name = f"{template_name}.html"

        if name not in TEMPLATES:
            raise Exception("Template not found", name)

        return self.template_env.get_template(name)

    def render_template(self, template_name: str, **context):
        """Render an HTML template to send notification"""
        template = self.get_template(template_name)
        return template.render(**context)

    def send_email(self, template_name: str, **context):
        """Send an email via an external SMTP server
        Args:
            template_name(str): The email notification template to use
            **context(kwargs): kwargs to fill in template
        Raises:
            socket.error: Could not connect to the SMTP Server
        Returns:
            True: The mail was accepted for delivery.
        """
        body = self.render_template(template_name, **context)
        subject = self.get_email_subject(template_name)

        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["To"] = self.email
        msg["From"] = self.smtp_config["SMTP_FROM"]

        s = smtplib.SMTP(self.smtp_config["SMTP_HOST"], self.smtp_config["SMTP_PORT"])

        # if we have a cert, then trust it
        sslcontext = ssl.create_default_context()
        if self.smtp_config["SMTP_CERT"] is not None:
            sslcontext.load_verify_locations(cadata=self.smtp_config["SMTP_CERT"])
        s.starttls(context=sslcontext)

        # if smtp credentials were provided, login
        if (
            self.smtp_config["SMTP_USER"] is not None
            and self.smtp_config["SMTP_PASS"] is not None
        ):
            s.login(self.smtp_config["SMTP_USER"], self.smtp_config["SMTP_PASS"])

        s.sendmail(self.smtp_config["SMTP_FROM"], [self.email], msg.as_string())
        s.quit()

        return True
