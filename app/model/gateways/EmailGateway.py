import smtplib
from email.mime.text import MIMEText


class EmailGateway:
    def __init__(self, smtp_user: str, smtp_pass: str):
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass

    def send_reset_code(self, to_email: str, code: str):
        subject = "DIJE - Recuperación de contraseña"
        body = (
            "Hola,\n\n"
            f"Tu código de recuperación es: {code}\n"
            "Este código expira en 10 minutos.\n\n"
            "Si no solicitaste este código, ignora este correo.\n\n"
            "— DIJE"
        )

        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = self.smtp_user
        msg["To"] = to_email

        with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.smtp_user, self.smtp_pass)  
            server.send_message(msg)
