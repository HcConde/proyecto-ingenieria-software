import tkinter as tk
from tkinter import ttk

from app.config.database import init_db
from app.controllers.AuthController import AuthController

from app.app_state import AppState
from app.views.MainView import MainView
from app.views.LoginView import LoginView
from app.views.RegisterView import RegisterView
from app.views.BlockWorkspaceView import BlockWorkspaceView
from app.views.TeacherDashboardView import TeacherDashboardView


class Router:
    def __init__(self, root):
        self.root = root
        self.frames = {}

    def add(self, name, frame):
        self.frames[name] = frame

    def show(self, name):
        for f in self.frames.values():
            f.pack_forget()
        self.frames[name].pack(fill="both", expand=True)


def main():
    init_db()

    root = tk.Tk()
    root.title("DIJE")
    root.geometry("1100x700")
    root.minsize(900, 600)

    style = ttk.Style()
    style.theme_use("clam")

    state = AppState()
    router = Router(root)
    auth = AuthController()

    router.add("home", MainView(root, router))
    router.add("login", LoginView(root, router, auth, state))
    router.add("register", RegisterView(root, router, auth))
    router.add("workspace", BlockWorkspaceView(root, router, state))
    router.add("teacher_dashboard", TeacherDashboardView(root, router, state))


    router.show("home")
    root.mainloop()


if __name__ == "__main__":
    main()
