import tkinter as tk
from tkinter import ttk

from app.config.database import init_db
from app.app_state import AppState

# -------------------------
# Controllers
# -------------------------
from app.controllers.AuthController import AuthController
from app.controllers.ProgramController import ProgramController
from app.controllers.UserController import UserController
from app.controllers.ResetPasswordController import ResetPasswordController

# -------------------------
# Views
# -------------------------
from app.views.MainView import MainView
from app.views.LoginView import LoginView
from app.views.RegisterView import RegisterView
from app.views.ProfileView import ProfileView
from app.views.BlockWorkspaceView import BlockWorkspaceView
from app.views.TeacherDashboardView import TeacherDashboardView
from app.views.ForgotPasswordView import ForgotPasswordView

# -------------------------
# Use Cases
# -------------------------
from app.model.use_cases.EditarPerfil import EditarPerfil

# -------------------------
# Repositories & Services
# -------------------------
from app.model.repositories.UsuarioRepository import UsuarioRepository
from app.utils.file_service import FileService
from app.model.gateways.EmailGateway import EmailGateway


# =====================================================
# Router simple
# =====================================================
class Router:
    def __init__(self, root):
        self.root = root
        self.frames = {}

    def add(self, name, frame):
        self.frames[name] = frame

    def show(self, name):
        for f in self.frames.values():
            f.pack_forget()

        frame = self.frames[name]
        frame.pack(fill="both", expand=True)

        if hasattr(frame, "on_show"):
            frame.on_show()


# =====================================================
# Main
# =====================================================
def main():
    init_db()


    root = tk.Tk()
    root.title("DIJE")
    root.geometry("1100x700")
    root.minsize(900, 600)

    ttk.Style().theme_use("clam")

    state = AppState()
    router = Router(root)

    # -------------------------
    # Infrastructure
    # -------------------------
    usuario_repo = UsuarioRepository()
    file_service = FileService()

    email_gateway = EmailGateway(
        smtp_user="dije.app.eapiis@gmail.com",
        smtp_pass="ntpkwgnrslwiquhu"  
    )

    # -------------------------
    # Use Cases
    # -------------------------
    editar_perfil_uc = EditarPerfil(usuario_repo, file_service)

    # -------------------------
    # Controllers
    # -------------------------
    user_ctrl = UserController(editar_perfil_uc)

    auth_ctrl = AuthController(state)              
    program_ctrl = ProgramController()
    reset_ctrl = ResetPasswordController(email_gateway)

    # -------------------------
    # Views
    # -------------------------
    router.add("home", MainView(root, router))
    router.add("login", LoginView(root, router, auth_ctrl, state))
    router.add("register", RegisterView(root, router, auth_ctrl))
    router.add("workspace", BlockWorkspaceView(root, router, state, program_ctrl, auth_ctrl))
    router.add("teacher_dashboard", TeacherDashboardView(root, router, state, program_ctrl, auth_ctrl))
    router.add("profile", ProfileView(root, router, state, user_ctrl))
    router.add("forgot_password", ForgotPasswordView(root, router, reset_ctrl))

    # -------------------------
    # Start
    # -------------------------
    router.show("home")
    root.mainloop()


if __name__ == "__main__":
    main()
