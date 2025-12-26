from tkinter import ttk


class TeacherDashboardView(ttk.Frame):
    def __init__(self, parent, router, state):
        super().__init__(parent)
        self.router = router
        self.state = state

        top = ttk.Frame(self)
        top.pack(fill="x", padx=12, pady=10)

        ttk.Label(top, text="Dashboard Docente", font=("Segoe UI", 14, "bold")).pack(side="left")

        u = self.state.current_user
        user_txt = "Usuario: (sin sesión)"
        if u:
            user_txt = f"Usuario: {u.nombre} {u.apellido} ({u.rol})"
        ttk.Label(top, text=user_txt).pack(side="left", padx=15)

        ttk.Button(top, text="Cerrar sesión", command=self.logout).pack(side="right")

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        ttk.Label(
            body,
            text="Aquí irá el panel docente:\n"
                 "• Ver programas enviados por alumnos\n"
                 "• Revisar / evaluar\n"
                 "• Asignar proyectos\n"
                 "• Historial y observaciones\n",
            font=("Segoe UI", 11)
        ).pack(anchor="w", pady=10)

        cards = ttk.Frame(body)
        cards.pack(fill="x", pady=10)

        ttk.Label(cards, text="Accesos rápidos (placeholder)", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")

        ttk.Button(cards, text="Ver programas", command=self.not_implemented).grid(row=1, column=0, pady=6, sticky="w")
        ttk.Button(cards, text="Evaluar programa", command=self.not_implemented).grid(row=2, column=0, pady=6, sticky="w")
        ttk.Button(cards, text="Mis alumnos", command=self.not_implemented).grid(row=3, column=0, pady=6, sticky="w")

        ttk.Button(body, text="Volver al inicio", command=lambda: self.router.show("home")).pack(anchor="w", pady=10)

    def logout(self):
        self.state.current_user = None
        self.router.show("home")

    def not_implemented(self):
        from tkinter import messagebox
        messagebox.showinfo("Info", "Todavía no implementado. (Lo hacemos en el siguiente sprint)")
