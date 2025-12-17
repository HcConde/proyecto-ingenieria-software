import tkinter as tk
from tkinter import messagebox
from Src.Model.UserModel import UsuarioModel


class FrmLogin(tk.Toplevel):

    def __init__(self, master):
        super().__init__(master)

        self.title("Iniciar Sesión")
        self.geometry("400x450")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.build()

    def build(self):
        tk.Label(
            self,
            text="RoboBlock",
            font=("Arial", 20, "bold"),
            fg="#7A3DF0"
        ).pack(pady=20)

        tk.Label(self, text="Correo Electrónico").pack()
        self.email = tk.Entry(self, width=30)
        self.email.pack(pady=5)

        tk.Label(self, text="Contraseña").pack()
        self.password = tk.Entry(self, width=30, show="*")
        self.password.pack(pady=5)

        tk.Button(
            self,
            text="Iniciar Sesión",
            bg="#7A3DF0",
            fg="white",
            command=self.login
        ).pack(pady=20)

    def login(self):
        email = self.email.get().strip()
        password = self.password.get().strip()

        if not email or not password:
            messagebox.showwarning(
                "Campos vacíos",
                "Ingrese correo y contraseña"
            )
            return

        usuario = UsuarioModel.login(email, password)

        # ❌ Usuario NO existe
        if usuario is None:
            messagebox.showerror(
                "Acceso denegado",
                "Usuario no registrado o credenciales incorrectas"
            )
            return

        # ✔ Usuario válido
        self.master.usuario_actual = usuario
        messagebox.showinfo(
            "Bienvenido",
            f"Bienvenido {usuario['nombre']}"
        )

        self.destroy()  # CIERRA LOGIN
