import tkinter as tk
from tkinter import ttk, messagebox
import json
import math
import os

from PIL import Image, ImageTk


class TeacherDashboardView(ttk.Frame):
    def __init__(self, parent, router, state, program_controller, auth_controller):
        super().__init__(parent)
        self.router = router
        self.state = state
        self.program_ctrl = program_controller
        self.auth_controller = auth_controller

        self.selected_user_id = None
        self._users_cache = []
        self._user_chip_img = None  # evita que desaparezca la imagen

        # ==========================
        # TOP BAR
        # ==========================
        top = ttk.Frame(self)
        top.pack(fill="x", padx=12, pady=10)

        ttk.Label(top, text="Dashboard Docente", font=("Segoe UI", 14, "bold")).pack(side="left")

        ttk.Button(top, text="Cerrar sesión", command=self.logout).pack(side="right")
        ttk.Button(top, text="Refrescar", command=self.refresh_all).pack(side="right", padx=6)


        self.user_menu_btn = ttk.Menubutton(top, text="👤 Usuario")
        self.user_menu_btn.pack(side="right", padx=6)

        self.user_menu = tk.Menu(self.user_menu_btn, tearoff=0)
        self.user_menu.add_command(label="Editar perfil", command=lambda: self.router.show("profile"))
        self.user_menu_btn["menu"] = self.user_menu

        # ==========================
        # 3 columnas: Usuarios | Proyectos | Bloques
        # ==========================
        content = ttk.PanedWindow(self, orient="horizontal")
        content.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        # ---------- IZQUIERDA: Usuarios + buscador
        left = ttk.Frame(content, width=340)
        content.add(left, weight=0)

        ttk.Label(left, text="Usuarios", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=8, pady=(8, 6))

        search_row = ttk.Frame(left)
        search_row.pack(fill="x", padx=8, pady=(0, 6))

        ttk.Label(search_row, text="Buscar:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_row, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=6)
        ttk.Button(search_row, text="Filtrar", command=self.apply_user_filter).pack(side="left")

        self.user_tree = ttk.Treeview(
            left,
            columns=("usuario", "rol", "correo"),
            show="headings",
            height=14
        )
        self.user_tree.heading("usuario", text="Usuario")
        self.user_tree.heading("rol", text="Rol")
        self.user_tree.heading("correo", text="Correo")

        self.user_tree.column("usuario", width=160)
        self.user_tree.column("rol", width=80, anchor="center")
        self.user_tree.column("correo", width=200)

        self.user_tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.user_tree.bind("<<TreeviewSelect>>", self.on_select_user)

        # ---------- CENTRO: Proyectos del usuario seleccionado
        middle = ttk.Frame(content)
        content.add(middle, weight=1)

        header_mid = ttk.Frame(middle)
        header_mid.pack(fill="x", pady=(8, 6))

        ttk.Label(header_mid, text="Proyectos", font=("Segoe UI", 11, "bold")).pack(side="left")
        self.mid_info = ttk.Label(header_mid, text="(selecciona un usuario)")
        self.mid_info.pack(side="left", padx=10)

        self.proj_tree = ttk.Treeview(
            middle,
            columns=("programa", "fecha"),
            show="headings",
            height=14
        )
        self.proj_tree.heading("programa", text="Programa")
        self.proj_tree.heading("fecha", text="Fecha")

        self.proj_tree.column("programa", width=340)
        self.proj_tree.column("fecha", width=220, anchor="center")

        self.proj_tree.pack(fill="both", expand=True, pady=(0, 8))
        self.proj_tree.bind("<<TreeviewSelect>>", self.on_select_project)

        actions = ttk.Frame(middle)
        actions.pack(fill="x", pady=(0, 8))

        ttk.Button(actions, text="Ejecutar carrito real", command=self.real_car_placeholder).pack(side="left")
        ttk.Button(actions, text="Simular seleccionado", command=self.simulate_selected).pack(side="left", padx=8)

        # ---------- DERECHA: Bloques del proyecto seleccionado
        right = ttk.Frame(content, width=360)
        content.add(right, weight=0)

        ttk.Label(right, text="Bloques del proyecto", font=("Segoe UI", 11, "bold")).pack(
            anchor="w", padx=8, pady=(8, 6)
        )

        self.blocks_text = tk.Text(right, height=16, wrap="word")
        self.blocks_text.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self._set_blocks_preview("Selecciona un proyecto para ver sus bloques…")

        # ==========================
        # SIMULACIÓN (abajo)
        # ==========================
        sim_box = ttk.LabelFrame(self, text="Simulación")
        sim_box.pack(fill="both", expand=False, padx=12, pady=(0, 12))

        sim_bar = ttk.Frame(sim_box)
        sim_bar.pack(fill="x", padx=10, pady=8)

        self.sim_status = ttk.Label(sim_bar, text="Estado: listo")
        self.sim_status.pack(side="left")

        ttk.Button(sim_bar, text="⟲ Reset", command=self.reset_sim).pack(side="right")

        self.sim = tk.Canvas(sim_box, bg="white", highlightthickness=1, highlightbackground="#cccccc", height=260)
        self.sim.pack(fill="x", padx=10, pady=(0, 10))

        # estado simulación
        self.sim_after = None
        self.sim_queue = []
        self.sim_i = 0
        self.car = {"x": 160, "y": 120, "heading": -90}
        self.reset_sim()

    # ---------------------------
    # Lifecycle
    # ---------------------------
    def on_show(self):
        self.refresh_all()
        self.load_user_chip()

    def refresh_all(self):
        self.load_users()
        self.clear_projects()
        self._set_blocks_preview("Selecciona un proyecto para ver sus bloques…")
        self.reset_sim()

    # ---------------------------
    # Sesión
    # ---------------------------
    def logout(self):
        self.auth_controller.logout()
        self.router.show("home")

    # ---------------------------
    # Usuarios (izquierda)
    # ---------------------------
    def load_users(self):
        self.user_tree.delete(*self.user_tree.get_children())

        u = self.state.current_user
        if not u or u.rol != "DOCENTE":
            return

        self._users_cache = self.program_ctrl.list_all_users()

        for usr in self._users_cache:
            uid = str(usr["id"])
            nombre = f'{usr["nombre"]} {usr["apellido"]}'
            rol = usr["rol"]
            correo = usr["correo"]
            self.user_tree.insert("", "end", iid=uid, values=(nombre, rol, correo))

    def apply_user_filter(self):
        q = self.search_var.get().strip().lower()

        self.user_tree.delete(*self.user_tree.get_children())
        for usr in self._users_cache:
            nombre = f'{usr["nombre"]} {usr["apellido"]}'.lower()
            correo = (usr.get("correo") or "").lower()
            rol = (usr.get("rol") or "").lower()

            if q and (q not in nombre and q not in correo and q not in rol):
                continue

            uid = str(usr["id"])
            self.user_tree.insert("", "end", iid=uid, values=(
                f'{usr["nombre"]} {usr["apellido"]}',
                usr["rol"],
                usr["correo"],
            ))

        self.clear_projects()

    def on_select_user(self, event=None):
        sel = self.user_tree.selection()
        if not sel:
            return
        self.selected_user_id = int(sel[0])
        values = self.user_tree.item(sel[0], "values")
        self.mid_info.config(text=f"Usuario: {values[0]}")

        self.load_projects_for_selected_user()
        self._set_blocks_preview("Selecciona un proyecto para ver sus bloques…")
        self.reset_sim()

    # ---------------------------
    # Proyectos (centro)
    # ---------------------------
    def clear_projects(self):
        self.proj_tree.delete(*self.proj_tree.get_children())
        self.selected_user_id = None
        self.mid_info.config(text="(selecciona un usuario)")

    def load_projects_for_selected_user(self):
        self.proj_tree.delete(*self.proj_tree.get_children())

        docente = self.state.current_user
        if not docente or docente.rol != "DOCENTE":
            return
        if not self.selected_user_id:
            return

        items = self.program_ctrl.list_projects_for_teacher_by_student(docente.id, self.selected_user_id)

        for it in items:
            pid = str(it["programa_id"])
            self.proj_tree.insert("", "end", iid=pid, values=(it["programa_nombre"], it["createdAt"]))

    def get_selected_project_id(self):
        sel = self.proj_tree.selection()
        if not sel:
            return None
        return int(sel[0])

    def on_select_project(self, event=None):
        pid = self.get_selected_project_id()
        if not pid:
            self._set_blocks_preview("Selecciona un proyecto para ver sus bloques…")
            return
        self.show_blocks_for_project(pid)

    # ---------------------------
    # Bloques (derecha)
    # ---------------------------
    def show_blocks_for_project(self, programa_id: int):
        try:
            raw = self.program_ctrl.get_program_json(programa_id)
            program = json.loads(raw)
            if not isinstance(program, list):
                raise ValueError("Formato inválido.")
        except Exception as e:
            self._set_blocks_preview(f"No se pudo leer el programa #{programa_id}:\n{e}")
            return

        lines = [f"Programa #{programa_id}", "-" * 28]
        for i, step in enumerate(program, start=1):
            code = step.get("code")
            val = step.get("value")
            if val is None:
                lines.append(f"{i:02d}. [{code}]")
            else:
                lines.append(f"{i:02d}. [{code} {val}]")

        self._set_blocks_preview("\n".join(lines))

    def _set_blocks_preview(self, text: str):
        self.blocks_text.configure(state="normal")
        self.blocks_text.delete("1.0", "end")
        self.blocks_text.insert("1.0", text)
        self.blocks_text.configure(state="disabled")

    # ---------------------------
    # Placeholder (sin función)
    # ---------------------------
    def real_car_placeholder(self):
        messagebox.showinfo("Ejecutar carrito real", "Aún no implementado .")

    # ---------------------------
    # Simulación
    # ---------------------------
    def simulate_selected(self):
        pid = self.get_selected_project_id()
        if not pid:
            messagebox.showinfo("Info", "Selecciona un proyecto.")
            return

        try:
            raw = self.program_ctrl.get_program_json(pid)
            program = json.loads(raw)
            if not isinstance(program, list):
                raise ValueError("Formato inválido de programa.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el programa: {e}")
            return

        queue = []
        for step in program:
            code = step.get("code")
            val = step.get("value")

            if code == "AVANZAR":
                queue.append(("MOVE", int(val)))
            elif code == "RETROCEDER":
                queue.append(("MOVE", -int(val)))
            elif code == "GIRAR_IZQ":
                queue.append(("TURN", -int(val)))
            elif code == "GIRAR_DER":
                queue.append(("TURN", int(val)))
            elif code == "DETENER":
                queue.append(("STOP", 0))
            else:
                queue.append(("UNKNOWN", 0))

        self.reset_sim()
        self.sim_queue = queue
        self.sim_i = 0
        self.sim_status.config(text=f"Estado: simulando programa #{pid}...")
        self.step_sim()

    def reset_sim(self):
        if self.sim_after:
            self.after_cancel(self.sim_after)
            self.sim_after = None

        self.sim_queue = []
        self.sim_i = 0
        self.sim_status.config(text="Estado: listo")

        self.sim.delete("all")
        w = self.sim.winfo_width() or 520
        h = self.sim.winfo_height() or 260

        for x in range(0, int(w), 40):
            self.sim.create_line(x, 0, x, h, fill="#eee")
        for y in range(0, int(h), 40):
            self.sim.create_line(0, y, w, y, fill="#eee")

        self.car = {"x": w / 2, "y": h / 2, "heading": -90}
        self.draw_car()

    def draw_car(self):
        self.sim.delete("car")
        x, y = self.car["x"], self.car["y"]
        heading = math.radians(self.car["heading"])

        size = 14
        self.sim.create_rectangle(x - size, y - size, x + size, y + size,
                                  outline="#333", width=2, fill="#dff3ff", tags="car")
        dx = math.cos(heading) * 24
        dy = math.sin(heading) * 24
        self.sim.create_line(x, y, x + dx, y + dy, width=3, arrow="last", tags="car")

    def step_sim(self):
        if self.sim_i >= len(self.sim_queue):
            self.sim_after = None
            self.sim_status.config(text="Estado: terminado ")
            return

        action, value = self.sim_queue[self.sim_i]
        self.sim_i += 1

        if action == "TURN":
            self.car["heading"] = (self.car["heading"] + value) % 360
            self.draw_car()
            self.sim_after = self.after(180, self.step_sim)
            return

        if action == "STOP":
            self.sim_after = self.after(200, self.step_sim)
            return

        if action == "MOVE":
            self.anim_move(value)
            return

        self.sim_after = self.after(150, self.step_sim)

    def anim_move(self, dist, steps=12, delay=25):
        per = dist / steps
        heading = math.radians(self.car["heading"])

        def tick(i=0):
            if i >= steps:
                self.draw_car()
                self.sim_after = self.after(140, self.step_sim)
                return

            self.car["x"] += math.cos(heading) * per
            self.car["y"] += math.sin(heading) * per

            w = self.sim.winfo_width() or 520
            h = self.sim.winfo_height() or 260

            self.car["x"] = max(18, min(w - 18, self.car["x"]))
            self.car["y"] = max(18, min(h - 18, self.car["y"]))

            self.draw_car()
            self.sim_after = self.after(delay, lambda: tick(i + 1))

        tick()

    # ---------------------------
    # Chip usuario (foto + nombre)
    # ---------------------------
    def load_user_chip(self):
        u = self.state.current_user
        if not u:
            self.user_menu_btn.config(text="👤 Usuario", image="", compound="none")
            self._user_chip_img = None
            return

        self.user_menu_btn.config(text=f"👤 {u.nombre}")

        path = getattr(u, "foto_path", None)
        if path and not os.path.isabs(path):
            # para soportar rutas relativas tipo assets/profiles/user_1.png
            path = os.path.join(os.getcwd(), path)

        if path and os.path.exists(path):
            try:
                img = Image.open(path).resize((18, 18))
                self._user_chip_img = ImageTk.PhotoImage(img)
                self.user_menu_btn.config(image=self._user_chip_img, compound="left")
            except Exception:
                self.user_menu_btn.config(image="", compound="none")
                self._user_chip_img = None
        else:
            self.user_menu_btn.config(image="", compound="none")
            self._user_chip_img = None
