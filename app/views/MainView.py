import tkinter as tk
from tkinter import ttk


class MainView(ttk.Frame):
    def __init__(self, parent, app_router):
        super().__init__(parent)
        self.router = app_router

        ttk.Label(self, text="DIJE", font=("Segoe UI", 28, "bold")).pack(pady=(40, 10))
        ttk.Label(self, text="Programación por bloques para controlar tu carrito", font=("Segoe UI", 12)).pack(pady=(0, 30))

        btns = ttk.Frame(self)
        btns.pack()

        ttk.Button(btns, text="Iniciar sesión", width=20, command=lambda: self.router.show("login")).grid(row=0, column=0, padx=10)
        ttk.Button(btns, text="Registrarse", width=20, command=lambda: self.router.show("register")).grid(row=0, column=1, padx=10)
