import random
from datetime import datetime, timedelta


class RecuperarContrasena:
    def __init__(self, usuario_repo, email_gateway, crypto):
        self.usuario_repo = usuario_repo
        self.email_gateway = email_gateway
        self.crypto = crypto

    # Paso 1: solicitar código
    def solicitar_codigo(self, correo: str):
        usuario = self.usuario_repo.find_by_email(correo)
        if not usuario:
            raise ValueError("No existe una cuenta con ese correo")

        codigo = f"{random.randint(0, 999999):06d}"
        expira = datetime.now() + timedelta(minutes=10)

        self.usuario_repo.save_password_reset(
            usuario.id, codigo, expira
        )

        self.email_gateway.send_reset_code(
            correo, codigo
        )

    # Paso 2: confirmar código + nueva contraseña
    def confirmar_cambio(self, correo, codigo, nueva_password):
        usuario = self.usuario_repo.find_by_email(correo)
        if not usuario:
            raise ValueError("Correo inválido")

        reset = self.usuario_repo.get_valid_reset_code(
            usuario.id, codigo
        )

        if not reset:
            raise ValueError("Código inválido o expirado")

        password_hash = self.crypto.hash_password(nueva_password)

        self.usuario_repo.update_password(usuario.id, password_hash)
        self.usuario_repo.mark_reset_used(reset["id"])
