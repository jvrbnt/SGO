import logging
import os
import smtplib
from email.message import EmailMessage
from urllib.parse import urlencode


logger = logging.getLogger("sgo.email")


def send_welcome_email(recipient: str, first_name: str) -> bool:
    """Send the welcome message when outgoing mail is explicitly enabled."""
    if os.getenv("MAIL_ENABLED", "false").lower() not in {"1", "true", "yes"}:
        logger.info("Welcome email skipped because MAIL_ENABLED is not enabled")
        return False

    host = os.getenv("SMTP_HOST")
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("MAIL_FROM", username)
    if not host or not username or not password or not sender:
        logger.error("Mail is enabled but SMTP configuration is incomplete")
        return False

    port = int(os.getenv("SMTP_PORT", "587"))
    use_ssl = os.getenv("SMTP_USE_SSL", "false").lower() in {"1", "true", "yes"}
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes"}

    message = EmailMessage()
    message["Subject"] = "Bienvenido a MiNa"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(
        f"Hola {first_name},\n\n"
        "Tu cuenta en el Servicio de Micro y Nanofabricación (MiNa) se ha creado correctamente.\n\n"
        "Ya puedes iniciar sesión y gestionar tus ofertas.\n\n"
        "Este correo se ha enviado desde una dirección no-reply. Por favor, no responda a este mensaje.\n\n"
    )

    try:
        smtp_class = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
        with smtp_class(host, port, timeout=15) as smtp:
            if use_tls and not use_ssl:
                smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        logger.exception("Could not send welcome email to %s: %s", recipient, exc)
        return False

    return True


def send_password_reset_email(recipient: str, first_name: str, token: str) -> bool:
    """Send a short-lived, single-use password reset link."""
    if os.getenv("MAIL_ENABLED", "false").lower() not in {"1", "true", "yes"}:
        logger.info("Password reset email skipped because MAIL_ENABLED is not enabled")
        return False

    host = os.getenv("SMTP_HOST")
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("MAIL_FROM", username)
    if not host or not username or not password or not sender:
        logger.error("Mail is enabled but SMTP configuration is incomplete")
        return False

    reset_url = os.getenv("RESET_PASSWORD_URL", "http://localhost:8000/reset-password")
    reset_link = f"{reset_url}?{urlencode({'token': token})}"
    message = EmailMessage()
    message["Subject"] = "Restablece tu contraseña MiNa"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(
        f"Hola {first_name},\n\n"
        "Hemos recibido una solicitud para cambiar tu contraseña. "
        "Usa este enlace antes de 30 minutos:\n\n"
        f"{reset_link}\n\n"
        "Si no solicitaste este cambio, puedes ignorar este mensaje. Agradeceríamos que nos notificases la incidencia a mina.imn@csic.es.\n\n"
        "Este correo se ha enviado desde una dirección no-reply."
    )

    port = int(os.getenv("SMTP_PORT", "587"))
    use_ssl = os.getenv("SMTP_USE_SSL", "false").lower() in {"1", "true", "yes"}
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes"}
    try:
        smtp_class = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
        with smtp_class(host, port, timeout=15) as smtp:
            if use_tls and not use_ssl:
                smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        logger.exception("Could not send password reset email to %s: %s", recipient, exc)
        return False

    return True