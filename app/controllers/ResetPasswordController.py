import random
import hashlib
from datetime import datetime, timedelta

from app.config.database import get_connection


def hash_password(pw: str) -> str:

    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


class ResetPasswordController:
    def __init__(self, email_gateway):
        self.email_gateway = email_gateway

    def request_code(self, correo: str) -> None:
        correo = correo.strip().lower()
        with get_connection() as conn:
            user = conn.execute("SELECT id, correo FROM usuario WHERE lower(correo)=?", (correo,)).fetchone()
            if not user:
                # Tip: por seguridad
                raise ValueError("No existe una cuenta con ese correo.")

            usuario_id = int(user["id"])
            code = f"{random.randint(0, 999999):06d}"
            expira = datetime.now() + timedelta(minutes=10)

            conn.execute(
                "INSERT INTO password_reset (usuario_id, codigo, expira_en, usado) VALUES (?,?,?,0)",
                (usuario_id, code, expira.strftime("%Y-%m-%d %H:%M:%S")),
            )

        # Enviar correo
        self.email_gateway.send_reset_code(correo, code)

    def confirm_reset(self, correo: str, code: str, new_password: str) -> None:
        correo = correo.strip().lower()
        code = code.strip()
        new_password = new_password.strip()

        if len(new_password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")

        with get_connection() as conn:
            user = conn.execute("SELECT id FROM usuario WHERE lower(correo)=?", (correo,)).fetchone()
            if not user:
                raise ValueError("Correo inválido.")

            usuario_id = int(user["id"])

            row = conn.execute(
                """
                SELECT id, expira_en, usado
                FROM password_reset
                WHERE usuario_id=? AND codigo=?
                ORDER BY id DESC
                LIMIT 1
                """,
                (usuario_id, code),
            ).fetchone()

            if not row:
                raise ValueError("Código incorrecto.")

            if int(row["usado"]) == 1:
                raise ValueError("Este código ya fue usado.")

            expira = datetime.strptime(row["expira_en"], "%Y-%m-%d %H:%M:%S")
            if datetime.now() > expira:
                raise ValueError("El código expiró. Solicita uno nuevo.")

            # marcar usado + actualizar password
            conn.execute("UPDATE password_reset SET usado=1 WHERE id=?", (int(row["id"]),))
            conn.execute(
                "UPDATE usuario SET password_hash=? WHERE id=?",
                (hash_password(new_password), usuario_id),
            )
