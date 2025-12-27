import tkinter as tk
from tkinter import ttk, messagebox
import json
import math


class BlockWorkspaceView(ttk.Frame):
    """
    Vista Scratch-like (MVP):
    - Panel izquierdo: biblioteca de bloques
    - Centro: workspace con bloques arrastrables
    - Derecha: simulación del carrito en Canvas
    """

    def __init__(self, parent, router, state):
        super().__init__(parent)
        self.router = router
        self.state = state

        # Toolbar superior
        top = ttk.Frame(self)
        top.pack(fill="x", padx=12, pady=10)

        user_txt = "Usuario: (sin sesión)"
        if self.state.current_user:
            u = self.state.current_user
            user_txt = f"Usuario: {u.nombre} {u.apellido} ({u.rol})"

        ttk.Label(top, text="Editor de Bloques", font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Label(top, text=user_txt).pack(side="left", padx=15)

        ttk.Button(top, text="Exportar (JSON)", command=self.export_program).pack(side="right", padx=5)
        ttk.Button(top, text="Limpiar", command=self.clear_workspace).pack(side="right", padx=5)
        ttk.Button(top, text="Cerrar sesión", command=self.logout).pack(side="right", padx=5)


        # Layout 3 columnas
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        left = ttk.Frame(paned, width=250)
        center = ttk.Frame(paned)
        right = ttk.Frame(paned, width=340)

        paned.add(left, weight=0)
        paned.add(center, weight=1)
        paned.add(right, weight=0)


        # Izquierda: Biblioteca
        ttk.Label(left, text="Biblioteca de Bloques", font=("Segoe UI", 11, "bold")).pack(
            anchor="w", pady=(10, 8), padx=10
        )

        self.block_defs = [
            ("AVANZAR", "Avanzar"),
            ("GIRAR_IZQ", "Girar Izq"),
            ("GIRAR_DER", "Girar Der"),
            ("DETENER", "Detener"),
        ]

        for code, label in self.block_defs:
            ttk.Button(left, text=label, command=lambda c=code, l=label: self.create_block(c, l)).pack(
                fill="x", padx=10, pady=5
            )

        ttk.Separator(left).pack(fill="x", padx=10, pady=10)
        ttk.Label(left, text="Tip: arrastra los bloques al workspace.", wraplength=220).pack(
            padx=10, pady=(0, 10)
        )


        # Centro: Workspace
        ttk.Label(center, text="Workspace", font=("Segoe UI", 11, "bold")).pack(
            anchor="w", pady=(10, 8), padx=10
        )

        self.canvas = tk.Canvas(center, bg="#f7f7f7", highlightthickness=1, highlightbackground="#cccccc")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Datos de bloques
        self._block_id_seq = 1
        self.blocks = {}  # tag -> {"code":..., "label":..., "x":..., "y":...}

        # Drag & drop
        self._drag_data = {"x": 0, "y": 0, "tag": None}
        self.canvas.tag_bind("draggable", "<ButtonPress-1>", self.on_drag_start)
        self.canvas.tag_bind("draggable", "<B1-Motion>", self.on_drag_move)
        self.canvas.tag_bind("draggable", "<ButtonRelease-1>", self.on_drag_end)


        # Derecha: Simulador
        ttk.Label(right, text="Simulación", font=("Segoe UI", 11, "bold")).pack(
            anchor="w", pady=(10, 8), padx=10
        )

        sim_controls = ttk.Frame(right)
        sim_controls.pack(fill="x", padx=10)

        ttk.Button(sim_controls, text="▶ Simular", command=self.run_simulation).pack(side="left")
        ttk.Button(sim_controls, text="⟲ Reset", command=self.reset_simulation).pack(side="left", padx=8)

        self.sim_status = ttk.Label(right, text="Estado: listo")
        self.sim_status.pack(anchor="w", padx=10, pady=(8, 0))

        self.sim_canvas = tk.Canvas(right, bg="white", highlightthickness=1, highlightbackground="#cccccc")
        self.sim_canvas.pack(fill="both", expand=True, padx=10, pady=10)


        self.sim_after_id = None
        self.sim_queue = []
        self.sim_idx = 0
        self.car = {"x": 160, "y": 200, "heading": -90}  
        self.car_item_ids = {"body": None, "dir": None}

        self.draw_sim_grid()
        self.draw_car()

    # Sesión / navegación
    def logout(self):
        self.state.current_user = None
        self.router.show("home")


    # Workspace: creación y drag
    def create_block(self, code: str, label: str):
        tag = f"block_{self._block_id_seq}"
        self._block_id_seq += 1

        x, y = 60, 40 + (len(self.blocks) * 55)

        rect = self.canvas.create_rectangle(
            x, y, x + 180, y + 40,
            outline="#333333", width=2,
            tags=(tag, "draggable")
        )
        text = self.canvas.create_text(
            x + 90, y + 20,
            text=label, font=("Segoe UI", 10, "bold"),
            tags=(tag, "draggable")
        )

        self.blocks[tag] = {"code": code, "label": label, "x": x, "y": y}
        self.canvas.tag_raise(text, rect)

    def on_drag_start(self, event):
        item = self.canvas.find_withtag("current")
        if not item:
            return
        tags = self.canvas.gettags(item[0])
        block_tag = next((t for t in tags if t.startswith("block_")), None)
        if not block_tag:
            return
        self._drag_data["tag"] = block_tag
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_drag_move(self, event):
        tag = self._drag_data["tag"]
        if not tag:
            return
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        self.canvas.move(tag, dx, dy)
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_drag_end(self, event):
        tag = self._drag_data["tag"]
        if not tag:
            return

        bbox = self.canvas.bbox(tag)
        if bbox:
            x1, y1, x2, y2 = bbox
            self.blocks[tag]["x"] = x1
            self.blocks[tag]["y"] = y1

        self._drag_data["tag"] = None

    def clear_workspace(self):
        self.canvas.delete("all")
        self.blocks.clear()


        self.canvas.tag_bind("draggable", "<ButtonPress-1>", self.on_drag_start)
        self.canvas.tag_bind("draggable", "<B1-Motion>", self.on_drag_move)
        self.canvas.tag_bind("draggable", "<ButtonRelease-1>", self.on_drag_end)


        self.reset_simulation()


    def get_ordered_program(self):
        """Devuelve lista de bloques ordenados de arriba hacia abajo por posición Y."""
        ordered = sorted(self.blocks.items(), key=lambda kv: kv[1]["y"])
        return [{"code": data["code"], "label": data["label"]} for _, data in ordered]

    def export_program(self):
        if not self.blocks:
            messagebox.showinfo("Exportar", "No hay bloques en el workspace.")
            return

        program = self.get_ordered_program()
        messagebox.showinfo("Programa (JSON)", json.dumps(program, indent=2, ensure_ascii=False))


    # Simulación (derecha)
    def draw_sim_grid(self):
        self.sim_canvas.delete("grid")
        w = self.sim_canvas.winfo_width() or 320
        h = self.sim_canvas.winfo_height() or 360

        step = 40
        for x in range(0, w, step):
            self.sim_canvas.create_line(x, 0, x, h, fill="#eeeeee", tags="grid")
        for y in range(0, h, step):
            self.sim_canvas.create_line(0, y, w, y, fill="#eeeeee", tags="grid")

    def draw_car(self):
        # borra si existe
        if self.car_item_ids["body"]:
            self.sim_canvas.delete(self.car_item_ids["body"])
        if self.car_item_ids["dir"]:
            self.sim_canvas.delete(self.car_item_ids["dir"])

        x = self.car["x"]
        y = self.car["y"]
        heading = math.radians(self.car["heading"])

        # cuerpo del carrito 
        size = 16
        body = self.sim_canvas.create_rectangle(
            x - size, y - size, x + size, y + size,
            outline="#333333", width=2, fill="#dff3ff"
        )


        dx = math.cos(heading) * 26
        dy = math.sin(heading) * 26
        direction = self.sim_canvas.create_line(
            x, y, x + dx, y + dy,
            fill="#333333", width=3, arrow="last"
        )

        self.car_item_ids["body"] = body
        self.car_item_ids["dir"] = direction

    def reset_simulation(self):
        if self.sim_after_id:
            self.after_cancel(self.sim_after_id)
            self.sim_after_id = None

        self.car = {"x": 160, "y": 200, "heading": -90}
        self.sim_queue = []
        self.sim_idx = 0
        self.sim_status.config(text="Estado: listo")

        self.sim_canvas.delete("all")
        self.draw_sim_grid()
        self.draw_car()

    def run_simulation(self):
        if self.sim_after_id:
            
            return

        if not self.blocks:
            messagebox.showinfo("Simulación", "No hay bloques para simular.")
            return

        # Crea cola de ejecución
        program = self.get_ordered_program()

       
        queue = []
        for b in program:
            code = b["code"]
            if code == "AVANZAR":
                queue.append(("MOVE", 40))
            elif code == "GIRAR_IZQ":
                queue.append(("TURN", -90))
            elif code == "GIRAR_DER":
                queue.append(("TURN", 90))
            elif code == "DETENER":
                queue.append(("STOP", 0))
            else:
                queue.append(("UNKNOWN", code))

        self.sim_queue = queue
        self.sim_idx = 0
        self.sim_status.config(text="Estado: simulando...")

        
        self.step_simulation()


    def step_simulation(self):
        if self.sim_idx >= len(self.sim_queue):
            self.sim_after_id = None
            self.sim_status.config(text="Estado: terminado ✅")
            return

        action, value = self.sim_queue[self.sim_idx]
        self.sim_idx += 1

        if action == "MOVE":
            self._anim_move(distance=value, steps=10, delay_ms=30)
            return

        if action == "TURN":
            self.car["heading"] = (self.car["heading"] + value) % 360
            self.draw_car()
            self.sim_after_id = self.after(250, self.step_simulation)
            return

        if action == "STOP":
            self.sim_after_id = self.after(250, self.step_simulation)
            return

        
        self.sim_status.config(text="Estado: bloque desconocido ⚠️")
        self.sim_after_id = self.after(400, self.step_simulation)

    def _anim_move(self, distance: int, steps: int, delay_ms: int):
        
        # movimiento suave de animacion
        per = distance / steps
        heading = math.radians(self.car["heading"])

        def tick(i=0):
            if i >= steps:
                self.draw_car()
                self.sim_after_id = self.after(200, self.step_simulation)
                return

            self.car["x"] += math.cos(heading) * per
            self.car["y"] += math.sin(heading) * per

            # límites simples (rebote suave)
            w = self.sim_canvas.winfo_width() or 320
            h = self.sim_canvas.winfo_height() or 360
            self.car["x"] = max(20, min(w - 20, self.car["x"]))
            self.car["y"] = max(20, min(h - 20, self.car["y"]))

            self.draw_car()
            self.sim_after_id = self.after(delay_ms, lambda: tick(i + 1))

        tick()
