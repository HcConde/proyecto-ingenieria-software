import tkinter as tk
class BloqueClon(tk.Label):
    """
    Bloque real que se arrastra y se suelta en el canvas
    """

    def __init__(self, root, texto, tipo, canvas_trabajo, start_x, start_y):
        super().__init__(
            root,
            text=texto,
            bg="#e0e7ff",
            relief="raised",
            bd=2,
            padx=8,
            pady=6
        )

        self.texto = texto
        self.tipo = tipo
        self.canvas_trabajo = canvas_trabajo

        # posición inicial
        self.place(x=start_x, y=start_y)

        self.bind("<B1-Motion>", self._en_drag)
        self.bind("<ButtonRelease-1>", self._fin_drag)

    def start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _en_drag(self, event):
        x = self.winfo_x() + event.x - self._drag_x
        y = self.winfo_y() + event.y - self._drag_y
        self.place(x=x, y=y)

    def _fin_drag(self, event):
        # límites del canvas
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
