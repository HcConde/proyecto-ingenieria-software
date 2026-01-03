class CargarInterfazPrincipal:
    def __init__(self, app_state):
        self.state = app_state

    def ejecutar(self) -> str:
        user = self.state.current_user

        if user is None:
            return "home"

        if user.rol == "ALUMNO":
            return "workspace"

        if user.rol == "DOCENTE":
            return "teacher_dashboard"

        return "home"
