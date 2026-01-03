import tkinter as tk
import os
import math
import json

from tkinter import ttk, messagebox, filedialog, simpledialog
from PIL import Image, ImageTk


class BlockWorkspaceView(ttk.Frame):
    COL_X = 60
    COL_Y0 = 30
    SLOT_H = 60
    BW = 280
    BH = 44

    def __init__(self, parent, router, state, program_controller):
        super().__init__(parent)
        self.router = router
        self.state = state
        self.program_ctrl = program_controller
        self.last_saved_program_id = None

        self._user_chip_img = None

        # ==========================
        # TOP BAR
        # ==========================
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=8)

        ttk.Label(top, text="Editor de Bloques", font=("Segoe UI", 13, "bold")).pack(side="left")

        # Menú usuario
        self.user_btn = ttk.Menubutton(top, text="👤 Usuario")
        self.user_btn.pack(side="right", padx=6)

        self.user_menu = tk.Menu(self.user_btn, tearoff=0)
        self.user_menu.add_command(label="Editar perfil", command=lambda: self.router.show("profile"))
        self.user_btn["menu"] = self.user_menu

        ttk.Button(top, text="Cerrar sesión", command=self.logout).pack(side="right", padx=6)

        # ==========================
        # PANED LAYOUT
        # ==========================
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        left = ttk.Frame(paned, width=240)
        center = ttk.Frame(paned)
        right = ttk.Frame(paned, width=360)

        paned.add(left, weight=0)
        paned.add(center, weight=1)
        paned.add(right, weight=0)

        # ==========================
        # BIBLIOTECA DE BLOQUES
        # ==========================
        ttk.Label(left, text="Bloques", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=(10, 6))

        self.block_defs = [
            ("AVANZAR", "Avanzar"),
            ("RETROCEDER", "Retroceder"),
            ("GIRAR_IZQ", "Girar Izq"),
            ("GIRAR_DER", "Girar Der"),
            ("DETENER", "Detener"),
        ]

        for code, label in self.block_defs:
            ttk.Button(
                left,
                text=label,
                command=lambda c=code, l=label: self.add_block(c, l)
            ).pack(fill="x", padx=10, pady=4)

        # ==========================
        # SECUENCIA (SNAP)
        # ==========================
        ttk.Label(center, text="Secuencia (snap vertical)", font=("Segoe UI", 11, "bold")).pack(
            anchor="w", padx=10, pady=(10, 6)
        )

        btn_row = ttk.Frame(center)
        btn_row.pack(fill="x", padx=10, pady=(0, 8))

        ttk.Button(btn_row, text="Limpiar", command=self.clear_all).pack(side="left", padx=4)
        ttk.Button(btn_row, text="Guardar", command=self.save_program).pack(side="left", padx=4)
        ttk.Button(btn_row, text="Enviar al docente", command=self.send_to_teacher).pack(side="left", padx=4)
        ttk.Button(btn_row, text="Cargar", command=self.load_from_file).pack(side="left", padx=4)
        ttk.Button(btn_row, text="Descargar", command=self.download_to_file).pack(side="left", padx=4)

        self.ws = tk.Canvas(center, bg="#f7f7f7", highlightthickness=1, highlightbackground="#cccccc")
        self.ws.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._id = 1
        self.sequence = []
        self.blocks = {}

        self._drag = {"tag": None, "x": 0, "y": 0}
        self.ws.tag_bind("drag", "<ButtonPress-1>", self.drag_start)
        self.ws.tag_bind("drag", "<B1-Motion>", self.drag_move)
        self.ws.tag_bind("drag", "<ButtonRelease-1>", self.drag_end)
        self.ws.tag_bind("del", "<Button-1>", self.on_delete_click)

        # ==========================
        # SIMULACIÓN
        # ==========================
        ttk.Label(right, text="Simulación", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=10, pady=(10, 6))

        sim_bar = ttk.Frame(right)
        sim_bar.pack(fill="x", padx=10)

        ttk.Button(sim_bar, text="▶ Simular", command=self.run_sim).pack(side="left")
        ttk.Button(sim_bar, text="⟲ Reset", command=self.reset_sim).pack(side="left", padx=8)
        ttk.Button(sim_bar, text="Simular carrito real", command=self.sim_real_placeholder).pack(side="left")

        self.sim_status = ttk.Label(right, text="Estado: listo")
        self.sim_status.pack(anchor="w", padx=10, pady=(8, 0))

        self.sim = tk.Canvas(right, bg="white", highlightthickness=1, highlightbackground="#cccccc")
        self.sim.pack(fill="both", expand=True, padx=10, pady=10)

        self.sim_after = None
        self.sim_queue = []
        self.sim_i = 0
        self.car = {"x": 160, "y": 200, "heading": -90}
        self.reset_sim()

    # ==========================
    # SESIÓN
    # ==========================
    def logout(self):
        self.state.current_user = None
        self.router.show("home")

    # ==========================
    # PERFIL USUARIO (SEGURO)
    # ==========================
    def on_show(self):
        self.load_user_chip()

    def load_user_chip(self):
        u = self.state.current_user
        if not u:
            self.user_btn.config(text="👤 Usuario")
            return

        self.user_btn.config(text=f"👤 {u.nombre}")

        path = getattr(u, "foto_path", None)
        if path and os.path.exists(path):
            try:
                img = Image.open(path).resize((18, 18))
                self._user_chip_img = ImageTk.PhotoImage(img)
                self.user_btn.config(image=self._user_chip_img, compound="left")
            except Exception:
                self.user_btn.config(image="", compound="none")
        else:
            self.user_btn.config(image="", compound="none")

    # ==========================
    # BLOQUES
    # ==========================
    def param_info(self, code):
        if code in ("AVANZAR", "RETROCEDER"):
            return {"min": 10, "max": 200, "default": 50}
        if code in ("GIRAR_IZQ", "GIRAR_DER"):
            return {"min": 0, "max": 180, "default": 90}
        return None

    def add_block(self, code, label, preset_value=None):
        tag = f"b{self._id}"
        self._id += 1

        x = self.COL_X
        y = self.COL_Y0 + len(self.sequence) * self.SLOT_H + 8

        self.ws.create_rectangle(x, y, x + self.BW, y + self.BH,
                                 outline="#333", width=2, fill="#fff", tags=(tag, "drag"))
        self.ws.create_text(x + 12, y + self.BH // 2, text=label,
                            anchor="w", font=("Segoe UI", 10, "bold"), tags=(tag, "drag"))

        self.ws.create_text(x + self.BW - 12, y + 10, text="×",
                            font=("Segoe UI", 14, "bold"),
                            fill="#aa0000", tags=(tag, "del"))

        info = self.param_info(code)
        param_var = None

        if info:
            val = info["default"] if preset_value is None else preset_value
            param_var = tk.StringVar(value=str(val))
            entry = ttk.Entry(self.ws, width=6, textvariable=param_var, justify="center")
            self.ws.create_window(x + self.BW - 55, y + self.BH // 2, window=entry, tags=(tag,))
            entry.bind("<Button-1>", lambda e: (entry.focus_set(), "break"))

            self.ws.create_text(x + self.BW - 105, y + self.BH // 2,
                                text=f'{info["min"]}-{info["max"]}',
                                anchor="e", font=("Segoe UI", 8), fill="#666", tags=(tag, "drag"))

        self.blocks[tag] = {"code": code, "label": label, "param": param_var}
        self.sequence.append(tag)
        self.relayout()

   
    def on_delete_click(self, event):
        item = self.ws.find_withtag("current")
        if not item:
            return
        tags = self.ws.gettags(item[0])
        tag = next((t for t in tags if t.startswith("b")), None)
        if tag:
            self.delete_block(tag)

    def delete_block(self, tag):
        if tag in self.sequence:
            self.sequence.remove(tag)
        self.blocks.pop(tag, None)
        self.ws.delete(tag)
        self.relayout()

    def relayout(self):
        for idx, tag in enumerate(self.sequence):
            x = self.COL_X
            y = self.COL_Y0 + idx * self.SLOT_H + 8
            bbox = self.ws.bbox(tag)
            if bbox:
                x1, y1, *_ = bbox
                self.ws.move(tag, x - x1, y - y1)


    # Drag
    def drag_start(self, event):
        item = self.ws.find_withtag("current")
        if not item:
            return
        tags = self.ws.gettags(item[0])
        tag = next((t for t in tags if t.startswith("b")), None)
        if not tag:
            return
        self._drag.update(tag=tag, x=event.x, y=event.y)

    def drag_move(self, event):
        tag = self._drag["tag"]
        if not tag:
            return
        dx = event.x - self._drag["x"]
        dy = event.y - self._drag["y"]
        self.ws.move(tag, dx, dy)
        self._drag["x"] = event.x
        self._drag["y"] = event.y

    def drag_end(self, event):
        tag = self._drag["tag"]
        if not tag:
            return
        idx = int((event.y - self.COL_Y0) / self.SLOT_H)
        idx = max(0, min(len(self.sequence) - 1, idx))

        old = self.sequence.index(tag)
        self.sequence.pop(old)
        self.sequence.insert(idx, tag)
        self._drag["tag"] = None
        self.relayout()

   
    # Programa
    def get_program(self):
        prog = []
        for tag in self.sequence:
            b = self.blocks[tag]
            code = b["code"]
            info = self.param_info(code)

            if not info:
                prog.append({"code": code, "value": None})
                continue

            raw = (b["param"].get() if b["param"] else "").strip()
            if raw == "":
                raise ValueError(f"Falta parámetro en {b['label']}.")

            val = int(raw)  # si falla, lanza
            if not (info["min"] <= val <= info["max"]):
                raise ValueError(f"Parámetro fuera de rango en {b['label']}: {info['min']}..{info['max']}")

            prog.append({"code": code, "value": val})
        return prog

    #  Guardar en DB (tabla programa)
    def save_program(self):
        if not self.state.current_user:
            messagebox.showerror("Error", "No hay sesión.")
            return
        if not self.sequence:
            messagebox.showinfo("Guardar", "No hay bloques.")
            return

        try:
            program = self.get_program()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        nombre = simpledialog.askstring("Guardar", "Nombre del programa:", parent=self)
        if not nombre:
            return

        try:
            pid = self.program_ctrl.save_program(self.state.current_user.id, nombre, program)
            self.last_saved_program_id = pid
            messagebox.showinfo("OK", f"Programa guardado (ID: {pid}).")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    #  Enviar al docente 
    def send_to_teacher(self):
        if not self.last_saved_program_id:
            messagebox.showwarning("Enviar", "Primero guarda el programa.")
            return

        correo = simpledialog.askstring("Enviar al docente", "Correo del docente:", parent=self)
        if not correo:
            return

        try:
            self.program_ctrl.send_to_teacher(self.last_saved_program_id, correo)
            messagebox.showinfo("OK", "Enviado al docente ✅ (aparecerá en su dashboard).")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Cargar (importar )
    def load_from_file(self):
        path = filedialog.askopenfilename(
            title="Cargar proyecto",
            filetypes=[("Proyecto JSON", "*.json"), ("Todos", "*.*")]
        )
        if not path:
            return

        try:
            content = open(path, "r", encoding="utf-8").read()
            program = json.loads(content)
            if not isinstance(program, list):
                raise ValueError("Formato inválido: se esperaba una lista.")

            # limpiar y reconstruir
            self.clear_all()
            code_to_label = {c: l for c, l in self.block_defs}
            for step in program:
                code = step.get("code")
                value = step.get("value")
                if code not in code_to_label:
                    raise ValueError(f"Bloque desconocido en archivo: {code}")
                self.add_block(code, code_to_label[code], preset_value=value)

            messagebox.showinfo("OK", "Proyecto cargado ")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar: {e}")

    #  Descargar (exportar)
    def download_to_file(self):
        if not self.sequence:
            messagebox.showinfo("Descargar", "No hay bloques.")
            return
        try:
            program = self.get_program()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        path = filedialog.asksaveasfilename(
            title="Descargar proyecto",
            defaultextension=".json",
            filetypes=[("Proyecto JSON", "*.json")]
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(program, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("OK", "Proyecto descargado ")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_all(self):
        self.ws.delete("all")
        self.sequence.clear()
        self.blocks.clear()
        self._drag = {"tag": None, "x": 0, "y": 0}
        self.last_saved_program_id = None
        self.reset_sim()


    # Simulación real 
    def sim_real_placeholder(self):
        messagebox.showinfo("Simular carrito real", "Aún no implementado (placeholder).")

    def reset_sim(self):
        if self.sim_after:
            self.after_cancel(self.sim_after)
            self.sim_after = None

        self.sim_queue = []
        self.sim_i = 0
        self.sim_status.config(text="Estado: listo")

        self.sim.delete("all")
        w = self.sim.winfo_width() or 320
        h = self.sim.winfo_height() or 360
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
        size = 16
        self.sim.create_rectangle(x - size, y - size, x + size, y + size,
                                  outline="#333", width=2, fill="#dff3ff", tags="car")
        dx = math.cos(heading) * 26
        dy = math.sin(heading) * 26
        self.sim.create_line(x, y, x + dx, y + dy, width=3, arrow="last", tags="car")

    def run_sim(self):
        if self.sim_after:
            return
        if not self.sequence:
            messagebox.showinfo("Simulación", "No hay bloques.")
            return

        try:
            program = self.get_program()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        q = []
        for s in program:
            code, val = s["code"], s["value"]
            if code == "AVANZAR":
                q.append(("MOVE", val))
            elif code == "RETROCEDER":
                q.append(("MOVE", -val))
            elif code == "GIRAR_IZQ":
                q.append(("TURN", -val))
            elif code == "GIRAR_DER":
                q.append(("TURN", val))
            elif code == "DETENER":
                q.append(("STOP", 0))

        self.sim_queue = q
        self.sim_i = 0
        self.sim_status.config(text="Estado: simulando...")
        self.step_sim()

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

            w = self.sim.winfo_width() or 320
            h = self.sim.winfo_height() or 360
            self.car["x"] = max(20, min(w - 20, self.car["x"]))
            self.car["y"] = max(20, min(h - 20, self.car["y"]))

            self.draw_car()
            self.sim_after = self.after(delay, lambda: tick(i + 1))

        tick()


        

    def open_user_menu(self):

        try:
            x = self.user_btn.winfo_rootx()
            y = self.user_btn.winfo_rooty() + self.user_btn.winfo_height()
            self.user_menu.tk_popup(x, y)
        finally:
            self.user_menu.grab_release()

