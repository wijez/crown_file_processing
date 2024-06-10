from fastapi_mail import ConnectionConfig, MessageSchema, FastMail

from app.core import get_settings

settings = get_settings()

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USER,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_USER,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS
)


async def send_email(to: str, subject: str, contents: str):
    message = MessageSchema(
        subject=subject,
        recipients=[to],
        body=contents,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
