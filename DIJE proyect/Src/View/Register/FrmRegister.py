import tkinter as tk
from tkinter import messagebox
from Src.Model.UserModel import UsuarioModel


class FrmRegister(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Crear Cuenta")
        self.geometry("420x520")
        self.resizable(False, False)
        self.configure(bg="white")

        # Modal real
        self.transient(master)
        self.grab_set()

        self.build()

    def build(self):
        container = tk.Frame(self, bg="white")
        container.pack(expand=True, padx=30, pady=20)

        tk.Label(
            container,
            text="Crear Cuenta",
            font=("Arial", 24, "bold"),
            fg="#7A3DF0",
            bg="white"
        ).pack(pady=20)

        # --- NOMBRE ---
        tk.Label(container, text="Nombre Completo", bg="white").pack(anchor="w")
        self.nombre = tk.Entry(container, width=35)
        self.nombre.pack(pady=6)

        # --- CORREO ---
        tk.Label(container, text="Correo Electrónico", bg="white").pack(anchor="w")
        self.email = tk.Entry(container, width=35)
        self.email.pack(pady=6)

        # --- PASSWORD ---
        tk.Label(container, text="Contraseña", bg="white").pack(anchor="w")
        self.password = tk.Entry(container, width=35, show="*")
        self.password.pack(pady=6)

        # BOTÓN REGISTRAR
        tk.Button(
            container,
            text="Crear Cuenta",
            bg="#7A3DF0",
            fg="white",
            width=25,
            command=self.register
        ).pack(pady=20)

        # CERRAR
        tk.Button(
            container,
            text="✕",
            bg="white",
            bd=0,
            fg="gray",
            command=self.destroy
        ).place(x=380, y=10)

    def register(self):
        nombre = self.nombre.get().strip()
        correo = self.email.get().strip()
        password = self.password.get().strip()

        if not nombre or not correo or not password:
            messagebox.showerror("Error", "Complete todos los campos")
            return

        registrado = UsuarioModel.registrar(nombre, correo, password)

        if not registrado:
            messagebox.showerror("Error", "El correo ya está registrado")
            return

        messagebox.showinfo("Éxito", "Cuenta creada correctamente")
        self.destroy()

