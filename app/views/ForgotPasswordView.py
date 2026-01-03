from tkinter import ttk, messagebox


class ForgotPasswordView(ttk.Frame):
    def __init__(self, parent, router, reset_controller):
        super().__init__(parent)
        self.router = router
        self.reset_ctrl = reset_controller

        ttk.Label(self, text="Recuperar contraseña", font=("Segoe UI", 14, "bold")).pack(pady=12)

        form = ttk.Frame(self)
        form.pack(padx=16, pady=8, fill="x")

        ttk.Label(form, text="Correo").grid(row=0, column=0, sticky="w")
        self.correo = ttk.Entry(form, width=40)
        self.correo.grid(row=1, column=0, sticky="w", pady=(0, 10))

        ttk.Button(form, text="Enviar código", command=self.send_code).grid(row=2, column=0, sticky="w", pady=4)

        ttk.Separator(self).pack(fill="x", padx=16, pady=10)

        ttk.Label(form, text="Código (6 dígitos)").grid(row=3, column=0, sticky="w")
        self.codigo = ttk.Entry(form, width=20)
        self.codigo.grid(row=4, column=0, sticky="w", pady=(0, 10))

        ttk.Label(form, text="Nueva contraseña").grid(row=5, column=0, sticky="w")
        self.new_pw = ttk.Entry(form, width=30, show="*")
        self.new_pw.grid(row=6, column=0, sticky="w", pady=(0, 10))

        ttk.Button(form, text="Cambiar contraseña", command=self.confirm).grid(row=7, column=0, sticky="w", pady=4)

        ttk.Button(self, text="Volver al login", command=lambda: self.router.show("login")).pack(pady=12)

    def send_code(self):
        try:
            self.reset_ctrl.request_code(self.correo.get())
            messagebox.showinfo("OK", "Te enviamos un código a tu correo (válido 10 min).")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def confirm(self):
        try:
            self.reset_ctrl.confirm_reset(self.correo.get(), self.codigo.get(), self.new_pw.get())
            messagebox.showinfo("OK", "Contraseña actualizada ✅")
            self.router.show("login")
        except Exception as e:
            messagebox.showerror("Error", str(e))
