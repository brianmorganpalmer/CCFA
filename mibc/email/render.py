import os
import smtplib
from email.mime.text import MIMEText

from bottle import template

from .. import settings

def render_to_email(context,         address_list, 
                    template_str=None, **kwargs):
    """send an email to someone by rendering a template with 
    the provided context (a dictionary).
    **kwargs are fitted into the fields of the message
    """

    for k, v in { "To":      ", ".join(address_list),
                  "From":    settings.email.default_from_addr,
                  "Subject": settings.email.default_subject, }.items():
        kwargs.setdefault(k, v)

    if not template_str:
        here = os.path.dirname(os.path.realpath(__file__))
        template_str = os.path.join(here, "notification.tpl")

    msg = template(template_str, **context)
    msg = MIMEText(msg)
    for k, v in kwargs.iteritems():
        msg[k] = v

    s = smtplib.SMTP(settings.email.default_smtp_serv)
    s.sendmail( kwargs["From"], address_list, msg.as_string() )
    s.quit()
