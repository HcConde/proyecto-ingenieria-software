import tkinter as tk
from tkinter import ttk, messagebox


class LoginView(ttk.Frame):
    def __init__(self, parent, app_router, auth_controller, state):
        super().__init__(parent)
        self.router = app_router
        self.auth = auth_controller
        self.state = state

        ttk.Label(self, text="Iniciar Sesión", font=("Segoe UI", 18, "bold")).pack(pady=(20, 10))

        form = ttk.Frame(self)
        form.pack(pady=10)

        ttk.Label(form, text="Correo").grid(row=0, column=0, sticky="w")
        self.email = ttk.Entry(form, width=35)
        self.email.grid(row=1, column=0, pady=(0, 10))

        ttk.Label(form, text="Contraseña").grid(row=2, column=0, sticky="w")
        self.password = ttk.Entry(form, width=35, show="*")
        self.password.grid(row=3, column=0, pady=(0, 10))

        ttk.Button(self, text="Entrar", command=self.on_login).pack(pady=8)
        ttk.Button(self, text="Volver", command=lambda: self.router.show("home")).pack()

    def on_login(self):
        try:
            user = self.auth.do_login(self.email.get(), self.password.get())
            self.state.current_user = user

            if user.rol == "ALUMNO":
                self.router.show("workspace")
            else:
                self.router.show("teacher_dashboard")

        except Exception as e:
            messagebox.showerror("Error", str(e))
