class CerrarSesion:
    def __init__(self, app_state):
        self.state = app_state

    def ejecutar(self):
        self.state.current_user = None
