from app.model.repositories.UsuarioRepository import UsuarioRepository
from app.model.use_cases.RegistrarUsuario import RegistrarUsuario
from app.model.use_cases.IniciarSesion import IniciarSesion
from app.model.use_cases.CerrarSesion import CerrarSesion
from app.model.use_cases.CargarInterfazPrincipal import CargarInterfazPrincipal


class AuthController:
    def __init__(self, app_state):
        self.user_repo = UsuarioRepository()
        self.state = app_state 

        self.registrar = RegistrarUsuario(self.user_repo)
        self.login = IniciarSesion(self.user_repo)
        self.cerrar_sesion = CerrarSesion(app_state)
        self.cargar_interfaz = CargarInterfazPrincipal(app_state)

    def register(self, data: dict) -> int:
        return self.registrar.execute(
            data["nombre"],
            data["apellido"],
            data["fecha_nacimiento"],
            data["correo"],
            data["password"],
            data.get("codigo", ""),
        )

    def do_login(self, correo: str, password: str) -> str:
        user = self.login.execute(correo, password)
        self.state.current_user = user
        return self.cargar_interfaz.ejecutar()


    def logout(self):
        self.cerrar_sesion.ejecutar()
