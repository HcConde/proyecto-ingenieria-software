from app.model.repositories.UsuarioRepository import UsuarioRepository
from app.utils.crypto import verify_password
from app.model.entities.Usuario import Usuario


class IniciarSesion:
    def __init__(self, user_repo: UsuarioRepository):
        self.user_repo = user_repo

    def execute(self, correo: str, password: str) -> Usuario:
        row = self.user_repo.find_auth_row(correo)
        if not row:
            raise ValueError("Correo o contraseña incorrectos.")

        if not verify_password(password, row["password_hash"]):
            raise ValueError("Correo o contraseña incorrectos.")

        return Usuario(
            id=row["id"],
            nombre=row["nombre"],
            apellido=row["apellido"],
            fecha_nacimiento=row["fecha_nacimiento"],
            correo=row["correo"],
            rol=row["rol"],
        )
