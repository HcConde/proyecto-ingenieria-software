import tkinter as tk
from tkinter import ttk, messagebox


class RegisterView(ttk.Frame):
    def __init__(self, parent, app_router, auth_controller):
        super().__init__(parent)
        self.router = app_router
        self.auth = auth_controller

        ttk.Label(self, text="Registro", font=("Segoe UI", 18, "bold")).pack(pady=(20, 10))

        form = ttk.Frame(self)
        form.pack(pady=10)

        self.nombre = self._field(form, "Nombre", 0)
        self.apellido = self._field(form, "Apellido", 1)
        self.fecha = self._field(form, "Fecha nacimiento (YYYY-MM-DD)", 2)
        self.correo = self._field(form, "Correo", 3)

        ttk.Label(form, text="Contraseña (min 6)").grid(row=8, column=0, sticky="w")
        self.password = ttk.Entry(form, width=35, show="*")
        self.password.grid(row=9, column=0, pady=(0, 10))

        ttk.Label(form, text="Código (opcional)").grid(row=10, column=0, sticky="w")
        self.codigo = ttk.Entry(form, width=35)
        self.codigo.grid(row=11, column=0, pady=(0, 10))

        ttk.Button(self, text="Crear cuenta", command=self.on_register).pack(pady=8)
        ttk.Button(self, text="Volver", command=lambda: self.router.show("home")).pack()

    def _field(self, parent, label, idx):
        r = idx * 2
        ttk.Label(parent, text=label).grid(row=r, column=0, sticky="w")
        e = ttk.Entry(parent, width=35)
        e.grid(row=r+1, column=0, pady=(0, 10))
        return e

    def on_register(self):
        try:
            data = {
                "nombre": self.nombre.get(),
                "apellido": self.apellido.get(),
                "fecha_nacimiento": self.fecha.get(),
                "correo": self.correo.get(),
                "password": self.password.get(),
                "codigo": self.codigo.get(),
            }
            user_id = self.auth.register(data)
            messagebox.showinfo("OK", f"Usuario creado con ID: {user_id}")
            self.router.show("login")
        except Exception as e:
            messagebox.showerror("Error", str(e))
