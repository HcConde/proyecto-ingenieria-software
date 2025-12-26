from app.model.repositories.UsuarioRepository import UsuarioRepository
from app.utils.crypto import hash_password


class RegistrarUsuario:
    def __init__(self, user_repo: UsuarioRepository):
        self.user_repo = user_repo

    def execute(self, nombre, apellido, fecha_nacimiento, correo, password, codigo: str = "") -> int:
        if self.user_repo.find_by_correo(correo):
            raise ValueError("Ese correo ya está registrado.")

        codigo = (codigo or "").strip()
        if codigo == "":
            rol = "ALUMNO"
        elif codigo == "4321":
            rol = "DOCENTE"
        else:
            raise ValueError("Código inválido. Si no tienes código, déjalo vacío.")

        pwd_hash = hash_password(password)
        user_id = self.user_repo.create_user(nombre, apellido, fecha_nacimiento, correo, pwd_hash, rol)
        return user_id
