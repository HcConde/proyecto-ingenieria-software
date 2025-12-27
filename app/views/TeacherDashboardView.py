from tkinter import ttk, messagebox
import tkinter as tk


class TeacherDashboardView(ttk.Frame):
    def __init__(self, parent, router, state, program_controller):
        super().__init__(parent)
        self.router = router
        self.state = state
        self.program_ctrl = program_controller

        top = ttk.Frame(self)
        top.pack(fill="x", padx=12, pady=10)

        ttk.Label(top, text="Dashboard Docente", font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Button(top, text="Refrescar", command=self.load_list).pack(side="right", padx=6)
        ttk.Button(top, text="Cerrar sesión", command=self.logout).pack(side="right")

        self.user_btn = ttk.Button(top, text="👤 Usuario", command=self.open_user_menu)
        self.user_btn.pack(side="right", padx=6)
        ttk.Button(top, text="Cerrar sesión", command=self.logout).pack(side="right")

        self.user_menu = tk.Menu(self, tearoff=0)
        self.user_menu.add_command(label="Editar perfil", command=lambda: self.router.show("profile"))


        # tabla
        self.tree = ttk.Treeview(
            self,
            columns=("id", "programa", "alumno", "estado", "fecha"),
            show="headings",
            height=14
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("programa", text="Programa")
        self.tree.heading("alumno", text="Alumno")
        self.tree.heading("estado", text="Estado")
        self.tree.heading("fecha", text="Fecha")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("programa", width=220)
        self.tree.column("alumno", width=220)
        self.tree.column("estado", width=90, anchor="center")
        self.tree.column("fecha", width=140, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        actions = ttk.Frame(self)
        actions.pack(fill="x", padx=12, pady=(0, 12))
        ttk.Button(actions, text="Ver programa JSON", command=self.open_selected).pack(side="left")

    def on_show(self):
        self.load_list()

    def logout(self):
        self.state.current_user = None
        self.router.show("home")

    def load_list(self):
        self.tree.delete(*self.tree.get_children())
        u = self.state.current_user
        if not u or u.rol != "DOCENTE":
            return

        items = self.program_ctrl.list_for_teacher(u.id)
        for it in items:
            pid = it["programa_id"]
            prog = it["programa_nombre"]
            alumno = f'{it["alumno_nombre"]} {it["alumno_apellido"]}'
            estado = it["estado"]
            fecha = it["createdAt"]
            self.tree.insert("", "end", values=(pid, prog, alumno, estado, fecha))

    def open_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Selecciona un programa.")
            return

        pid = int(self.tree.item(sel[0], "values")[0])
        try:
            data = self.program_ctrl.get_program_json(pid)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        win = tk.Toplevel(self)
        win.title(f"Programa #{pid}")
        win.geometry("700x500")

        txt = tk.Text(win, wrap="none")
        txt.pack(fill="both", expand=True)

        txt.insert("1.0", data)
        txt.configure(state="disabled")


    def on_show(self):
        u = self.state.current_user
        if u:
            self.user_btn.config(text=f"👤 {u.nombre}")
        self.load_list()

    def open_user_menu(self):
        try:
            x = self.user_btn.winfo_rootx()
            y = self.user_btn.winfo_rooty() + self.user_btn.winfo_height()
            self.user_menu.tk_popup(x, y)
        finally:
            self.user_menu.grab_release()