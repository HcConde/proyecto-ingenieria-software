import tkinter as tk
from tkinter import ttk

from app.config.database import init_db
from app.app_state import AppState

from app.controllers.AuthController import AuthController
from app.controllers.ProgramController import ProgramController
from app.controllers.UserController import UserController

from app.views.ProfileView import ProfileView
from app.views.MainView import MainView
from app.views.LoginView import LoginView
from app.views.RegisterView import RegisterView
from app.views.BlockWorkspaceView import BlockWorkspaceView
from app.views.TeacherDashboardView import TeacherDashboardView

from app.model.gateways.EmailGateway import EmailGateway
from app.controllers.ResetPasswordController import ResetPasswordController
from app.views.ForgotPasswordView import ForgotPasswordView



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


def main():
    init_db()

    root = tk.Tk()
    root.title("DIJE")
    root.geometry("1100x700")
    root.minsize(900, 600)

    ttk.Style().theme_use("clam")

    state = AppState()
    router = Router(root)

    auth = AuthController()
    program_ctrl = ProgramController()
    user_ctrl = UserController()

    email_gateway = EmailGateway(
    smtp_user="dije.app.eapiis@gmail.com",
    smtp_pass="ntpkwgnrslwiquhu"   
    )
    reset_ctrl = ResetPasswordController(email_gateway)


    router.add("home", MainView(root, router))
    router.add("login", LoginView(root, router, auth, state))
    router.add("register", RegisterView(root, router, auth))
    router.add("workspace", BlockWorkspaceView(root, router, state, program_ctrl))
    router.add("teacher_dashboard", TeacherDashboardView(root, router, state, program_ctrl))
    router.add("profile", ProfileView(root, router, state, user_ctrl))
    router.add("forgot_password", ForgotPasswordView(root, router, reset_ctrl))
    router.add("profile", ProfileView(root, router, state, user_ctrl))


    router.show("home")
    root.mainloop()


if __name__ == "__main__":
    main()

    