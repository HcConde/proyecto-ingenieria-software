import tkinter as tk


class BloqueArrastrable(tk.Label):
    """
    Bloque plantilla (lado izquierdo).
    Al hacer click, crea un CLON arrastrable.
    """

    def __init__(self, master, texto, tipo, canvas_trabajo, workspace):
        super().__init__(
            master,
            text=texto,
            bg="#e5e7eb",
            relief="raised",
            bd=2,
            padx=8,
            pady=6
        )

        self.texto = texto
        self.tipo = tipo
        self.canvas_trabajo = canvas_trabajo
        self.workspace = workspace   # 👈 REFERENCIA DIRECTA

        self.bind("<ButtonPress-1>", self._crear_clon)

    def _crear_clon(self, event):
        clon = BloqueClon(
            self.master.winfo_toplevel(),
            self.texto,
            self.tipo,
            self.canvas_trabajo,
            self.workspace,
            event.x_root,
            event.y_root
        )
        clon.start_drag(event)


class BloqueClon(tk.Label):
    """
    Bloque real que se arrastra y se suelta en el canvas
    """

    def __init__(self, root, texto, tipo, canvas_trabajo, workspace, x, y):
        super().__init__(
            root,
            text=texto,
            bg="#dbeafe",
            relief="raised",
            bd=2,
            padx=8,
            pady=6
        )

        self.texto = texto
        self.tipo = tipo
        self.canvas_trabajo = canvas_trabajo
        self.workspace = workspace   # 👈 REFERENCIA DIRECTA

        self.place(x=x, y=y)

        self.bind("<B1-Motion>", self._en_drag)
        self.bind("<ButtonRelease-1>", self._fin_drag)

    def start_drag(self, event):
        self._dx = event.x
        self._dy = event.y

    def _en_drag(self, event):
        x = self.winfo_x() + event.x - self._dx
        y = self.winfo_y() + event.y - self._dy
        self.place(x=x, y=y)

    def _fin_drag(self, event):
        cx = self.canvas_trabajo.winfo_rootx()
        cy = self.canvas_trabajo.winfo_rooty()
        cw = self.canvas_trabajo.winfo_width()
        ch = self.canvas_trabajo.winfo_height()

        x_root = self.winfo_rootx()
        y_root = self.winfo_rooty()

        if cx < x_root < cx + cw and cy < y_root < cy + ch:
            self._agregar_a_canvas()

        self.destroy()

    def _agregar_a_canvas(self):
        bloques = self.canvas_trabajo.find_withtag("bloque")
        y = len(bloques) * 45 + 10

        self.canvas_trabajo.create_rectangle(
            10, y, 260, y + 35,
            fill="#dbeafe",
            outline="#2563eb",
            tags=("bloque", self.tipo)
        )

        self.canvas_trabajo.create_text(
            20, y + 18,
            anchor="w",
            text=self.texto,
            font=("Segoe UI", 10),
            tags=("bloque", self.tipo)
        )

        # ✅ GUARDA DIRECTAMENTE EN FrmWorkspace
        self.workspace.bloques_logicos.append(self.tipo)
