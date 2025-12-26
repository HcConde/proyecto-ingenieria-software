import tkinter as tk
from tkinter import ttk, messagebox
import json


class BlockWorkspaceView(ttk.Frame):
    """
    Vista Scratch-like (mínimo funcional):
    - Panel izquierdo: biblioteca de bloques (botones)
    - Centro: canvas workspace con bloques arrastrables
    - Toolbar superior: exportar / limpiar / simular (placeholder)
    """

    def __init__(self, parent, router, state):
        super().__init__(parent)
        self.router = router
        self.state = state

        # --- Toolbar superior
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
        ttk.Button(top, text="Simular", command=self.simulate_placeholder).pack(side="right", padx=5)
        ttk.Button(top, text="Cerrar sesión", command=self.logout).pack(side="right", padx=5)

        # --- Paneles (izq biblioteca / centro workspace)
        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        left = ttk.Frame(paned, width=250)
        center = ttk.Frame(paned)
        paned.add(left, weight=0)
        paned.add(center, weight=1)

        # Biblioteca
        ttk.Label(left, text="Biblioteca de Bloques", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(10, 8), padx=10)

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
        ttk.Label(left, text="Tip: arrastra los bloques en el workspace.", wraplength=220).pack(padx=10, pady=(0, 10))

        # Workspace Canvas
        ttk.Label(center, text="Workspace", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(10, 8), padx=10)

        self.canvas = tk.Canvas(center, bg="#f7f7f7", highlightthickness=1, highlightbackground="#cccccc")
        self.canvas.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Datos de bloques en workspace
        self._block_id_seq = 1
        self.blocks = {}  # tag -> {"code":..., "label":..., "x":..., "y":...}

        # Drag & drop
        self._drag_data = {"x": 0, "y": 0, "tag": None}

        # Bindings para items con tag "draggable"
        self.canvas.tag_bind("draggable", "<ButtonPress-1>", self.on_drag_start)
        self.canvas.tag_bind("draggable", "<B1-Motion>", self.on_drag_move)
        self.canvas.tag_bind("draggable", "<ButtonRelease-1>", self.on_drag_end)

        # Scroll (opcional, por si crece)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)

    # ---------------------------
    # Navegación / sesión
    # ---------------------------
    def logout(self):
        self.state.current_user = None
        self.router.show("home")

    # ---------------------------
    # Bloques / Canvas
    # ---------------------------
    def create_block(self, code: str, label: str):
        tag = f"block_{self._block_id_seq}"
        self._block_id_seq += 1

        # posición inicial
        x, y = 60, 40 + (len(self.blocks) * 55)

        # “bloque” simple: rect + texto
        rect = self.canvas.create_rectangle(x, y, x + 180, y + 40, outline="#333333", width=2, tags=(tag, "draggable"))
        text = self.canvas.create_text(x + 90, y + 20, text=label, font=("Segoe UI", 10, "bold"), tags=(tag, "draggable"))

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

        # Actualiza coords aproximadas (tomamos el bbox del rect)
        bbox = self.canvas.bbox(tag)
        if bbox:
            x1, y1, x2, y2 = bbox
            self.blocks[tag]["x"] = x1
            self.blocks[tag]["y"] = y1

        self._drag_data["tag"] = None

    def clear_workspace(self):
        self.canvas.delete("all")
        self.blocks.clear()

        # Re-bind porque delete borra items, pero tags siguen funcionales para nuevos items
        self.canvas.tag_bind("draggable", "<ButtonPress-1>", self.on_drag_start)
        self.canvas.tag_bind("draggable", "<B1-Motion>", self.on_drag_move)
        self.canvas.tag_bind("draggable", "<ButtonRelease-1>", self.on_drag_end)

    def export_program(self):
        """
        Exporta una secuencia simple ordenando por posición Y (de arriba hacia abajo).
        Esto es un primer paso antes de CU17/CU18.
        """
        if not self.blocks:
            messagebox.showinfo("Exportar", "No hay bloques en el workspace.")
            return

        ordered = sorted(self.blocks.items(), key=lambda kv: kv[1]["y"])
        program = [{"code": data["code"], "label": data["label"]} for _, data in ordered]

        messagebox.showinfo("Programa (JSON)", json.dumps(program, indent=2, ensure_ascii=False))

    def simulate_placeholder(self):
        messagebox.showinfo("Simulación", "Simulación: próximamente.\n(Luego conectamos CU16 + motor de simulación)")

    def on_mousewheel(self, event):
        # Scroll vertical del canvas (opcional)
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
