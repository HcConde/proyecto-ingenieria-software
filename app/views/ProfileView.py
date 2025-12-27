from tkinter import ttk, messagebox


class ProfileView(ttk.Frame):
    def __init__(self, parent, router, state, user_controller):
        super().__init__(parent)
        self.router = router
        self.state = state
        self.user_ctrl = user_controller

        top = ttk.Frame(self)
        top.pack(fill="x", padx=12, pady=10)

        ttk.Label(top, text="Editar perfil", font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Button(top, text="Volver", command=self.go_back).pack(side="right")

        self.form = ttk.Frame(self)
        self.form.pack(fill="x", padx=12, pady=12)

        ttk.Label(self.form, text="Nombre").grid(row=0, column=0, sticky="w")
        self.nombre = ttk.Entry(self.form, width=40)
        self.nombre.grid(row=1, column=0, pady=(0, 10), sticky="w")

        ttk.Label(self.form, text="Apellido").grid(row=2, column=0, sticky="w")
        self.apellido = ttk.Entry(self.form, width=40)
        self.apellido.grid(row=3, column=0, pady=(0, 10), sticky="w")

        ttk.Label(self.form, text="Fecha nacimiento (YYYY-MM-DD)").grid(row=4, column=0, sticky="w")
        self.fecha = ttk.Entry(self.form, width=40)
        self.fecha.grid(row=5, column=0, pady=(0, 10), sticky="w")

        ttk.Button(self, text="Guardar cambios", command=self.save).pack(padx=12, pady=10, anchor="w")

    def on_show(self):
        # carga datos del usuario actual
        u = self.state.current_user
        if not u:
            self.router.show("home")
            return
        self.nombre.delete(0, "end")
        self.nombre.insert(0, u.nombre)
        self.apellido.delete(0, "end")
        self.apellido.insert(0, u.apellido)
        self.fecha.delete(0, "end")
        self.fecha.insert(0, u.fecha_nacimiento)

    def save(self):
        u = self.state.current_user
        if not u:
            return
        try:
            updated = self.user_ctrl.update_profile(
                u.id,
                self.nombre.get(),
                self.apellido.get(),
                self.fecha.get(),
            )
            self.state.current_user = updated
            messagebox.showinfo("OK", "Perfil actualizado ✅")
            self.go_back()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def go_back(self):
        # vuelve según rol
        u = self.state.current_user
        if not u:
            self.router.show("home")
        elif u.rol == "DOCENTE":
            self.router.show("teacher_dashboard")
        else:
            self.router.show("workspace")
