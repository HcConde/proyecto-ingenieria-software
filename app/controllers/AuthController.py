from app.model.repositories.UsuarioRepository import UsuarioRepository
from app.model.use_cases.RegistrarUsuario import RegistrarUsuario
from app.model.use_cases.IniciarSesion import IniciarSesion


class AuthController:
    def __init__(self):
        self.user_repo = UsuarioRepository()
        self.registrar = RegistrarUsuario(self.user_repo)
        self.login = IniciarSesion(self.user_repo)

    def register(self, data: dict) -> int:
        return self.registrar.execute(
            data["nombre"],
            data["apellido"],
            data["fecha_nacimiento"],
            data["correo"],
            data["password"],
            data.get("codigo", ""),
        )

    def do_login(self, correo: str, password: str):
        return self.login.execute(correo, password)
