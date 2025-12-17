import tkinter as tk
from tkinter import messagebox

from Src.View.Inicio.FrmInicio import FrmInicio
from Src.View.Login.FrmLogin import FrmLogin
from Src.View.Register.FrmRegister import FrmRegister
from Src.View.Workspace.FrmWorkspace import FrmWorkspace

from Src.Model.DatabaseInit import DatabaseInit


# ================== INICIALIZAR BD ==================
DatabaseInit.initialize()


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("RoboBlock")
        self.geometry("1200x800")
        self.resizable(False, False)

        # -------- SESIÓN --------
        self.usuario_actual = None

        # -------- CONTENEDOR --------
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # -------- VISTA INICIAL --------
        self.show_inicio()

    # ================== VISTAS ==================
    def clear_container(self):
        """Elimina la vista actual"""
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_inicio(self):
        self.clear_container()
        self.inicio = FrmInicio(
            self.container,
            on_login=self.open_login,
            on_register=self.open_register
        )
        self.inicio.pack(fill="both", expand=True)

    def show_workspace(self):
        """Workspace protegido"""
        if self.usuario_actual is None:
            messagebox.showerror(
                "Acceso restringido",
                "Debe iniciar sesión primero"
            )
            return

        self.clear_container()
        self.workspace = FrmWorkspace(
            self.container,
            on_exit=self.show_inicio   # 👈 callback para volver
        )
        self.workspace.pack(fill="both", expand=True)

    # ================== MODALES ==================
    def open_login(self):
        """
        Abre login.
        SOLO entra al workspace si el usuario fue autenticado.
        """
        login = FrmLogin(self)
        self.wait_window(login)   # espera cierre del modal

        # ✔️ SOLO si existe sesión
        if self.usuario_actual is not None:
            self.show_workspace()

    def open_register(self):
        """Registro visual"""
        FrmRegister(self)


# ================== EJECUCIÓN ==================
if __name__ == "__main__":
    app = App()
    app.mainloop()
