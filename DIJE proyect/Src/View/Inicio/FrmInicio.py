import tkinter as tk
from tkinter import ttk


# ---------- utilidades UI (canvas) ----------
def _rounded_rect(canvas, x1, y1, x2, y2, r=16, **kwargs):
    points = [
        x1+r, y1,
        x2-r, y1,
        x2, y1,
        x2, y1+r,
        x2, y2-r,
        x2, y2,
        x2-r, y2,
        x1+r, y2,
        x1, y2,
        x1, y2-r,
        x1, y1+r,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


def _vertical_gradient(canvas, x1, y1, x2, y2, top="#f5f3ff", bottom="#ffffff"):
    def hex_to_rgb(h):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def rgb_to_hex(rgb):
        return "#%02x%02x%02x" % rgb

    tr, tg, tb = hex_to_rgb(top)
    br, bg, bb = hex_to_rgb(bottom)
    steps = max(1, int(y2 - y1))

    for i in range(steps):
        t = i / steps
        r = int(tr + (br - tr) * t)
        g = int(tg + (bg - tg) * t)
        b = int(tb + (bb - tb) * t)
        canvas.create_line(x1, y1 + i, x2, y1 + i, fill=rgb_to_hex((r, g, b)))


class _Scrollable(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.inner = ttk.Frame(self.canvas)
        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.canvas.pack(side="left", fill="both", expand=True)
        self.vsb.pack(side="right", fill="y")

        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(self.inner_id, width=e.width)
        )

        # ✅ bind LOCAL (no global)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def destroy(self):
        try:
            self.canvas.unbind("<MouseWheel>")
        except Exception:
            pass
        super().destroy()



# ---------- FrmInicio ----------
class FrmInicio(ttk.Frame):
    def __init__(self, parent, on_login=None, on_register=None):
        super().__init__(parent)
        self.on_login = on_login or (lambda: None)
        self.on_register = on_register or (lambda: None)

        self._build_styles()

        sc = _Scrollable(self)
        sc.pack(fill="both", expand=True)

        # HEADER
        header = ttk.Frame(sc.inner, style="Card.TFrame")
        header.pack(fill="x", padx=24, pady=(16, 10))

        left = ttk.Frame(header, style="Card.TFrame")
        left.pack(side="left", padx=14)

        logo = tk.Canvas(left, width=44, height=44, highlightthickness=0, bg="white")
        logo.pack(side="left")
        _rounded_rect(logo, 2, 2, 42, 42, r=12, fill="#7c3aed", outline="")
        logo.create_text(22, 22, text="</>", fill="white", font=("Segoe UI", 12, "bold"))

        ttk.Frame(left, width=10).pack(side="left")

        brand = ttk.Frame(left, style="Card.TFrame")
        brand.pack(side="left")
        ttk.Label(brand, text="RoboBlock", style="H2.TLabel").pack(anchor="w")
        ttk.Label(brand, text="Programación Visual para Robótica", style="Muted.TLabel").pack(anchor="w")

        right = ttk.Frame(header, style="Card.TFrame")
        right.pack(side="right", padx=14)

        ttk.Button(right, text="Iniciar Sesión", style="Ghost.TButton",
                   command=self.on_login).pack(side="left", padx=(0, 10))
        ttk.Button(right, text="Registrarse Gratis", style="Primary.TButton",
                   command=self.on_register).pack(side="left")

        # HERO
        hero = tk.Canvas(sc.inner, height=420, highlightthickness=0)
        hero.pack(fill="x", padx=24, pady=(0, 18))
        hero.bind("<Configure>", lambda e: self._draw_hero(hero, e.width, e.height))

        # SECCIÓN 2
        sec2 = ttk.Frame(sc.inner)
        sec2.pack(fill="x", padx=24, pady=(10, 8))

        ttk.Label(sec2, text="¿Por qué RoboBlock?", style="H1.TLabel").pack(pady=(10, 6))
        ttk.Label(
            sec2,
            text="Una herramienta diseñada específicamente para el aprendizaje efectivo de\n"
                 "programación y robótica en estudiantes de secundaria",
            style="Muted2.TLabel",
            justify="center"
        ).pack(pady=(0, 18))

        cards = ttk.Frame(sec2)
        cards.pack(fill="x")

        self._feature_card(cards, "Aprendizaje Visual",
                           "Programa con bloques visuales que se conectan\ncomo piezas de LEGO.",
                           "💡").grid(row=0, column=0, padx=10)

        self._feature_card(cards, "Educación STEM",
                           "Desarrolla habilidades científicas y tecnológicas.",
                           "🎓").grid(row=0, column=1, padx=10)

        self._feature_card(cards, "Simulación en Tiempo Real",
                           "Prueba tu programa antes de usar el robot físico.",
                           "⚡").grid(row=0, column=2, padx=10)

        for i in range(3):
            cards.columnconfigure(i, weight=1)

    # ---------- estilos ----------
    def _build_styles(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure(".", font=("Segoe UI", 10))
        s.configure("Card.TFrame", background="#ffffff")
        s.configure("H1.TLabel", font=("Segoe UI", 24, "bold"), foreground="#111827")
        s.configure("H2.TLabel", font=("Segoe UI", 14, "bold"))
        s.configure("Muted.TLabel", foreground="#6b7280")
        s.configure("Muted2.TLabel", font=("Segoe UI", 12), foreground="#6b7280")

        s.configure("Primary.TButton", background="#7c3aed", foreground="white",
                    padding=(14, 10), borderwidth=0)
        s.map("Primary.TButton", background=[("active", "#6d28d9")])

        s.configure("Ghost.TButton", background="white", padding=(14, 10))
        s.map("Ghost.TButton", background=[("active", "#f3f4f6")])

    # ---------- componentes ----------
    def _feature_card(self, parent, title, body, icon):
        outer = tk.Frame(parent, bg="#e5e7eb")
        inner = tk.Frame(outer, bg="white", padx=16, pady=16)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        tk.Label(inner, text=icon, font=("Segoe UI", 18)).pack(anchor="w")
        tk.Label(inner, text=title, font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(8, 4))
        tk.Label(inner, text=body, fg="#6b7280").pack(anchor="w")

        return outer

    # ---------- dibujo hero ----------
    def _draw_hero(self, canvas, w, h):
        canvas.delete("all")
        _vertical_gradient(canvas, 0, 0, w, h)

        pad = 22
        canvas.create_text(
            pad, 140, anchor="nw",
            text="Aprende Robótica\nProgramando por Bloques",
            fill="#6d28d9", font=("Segoe UI", 34, "bold")
        )

        canvas.create_text(
            pad, 260, anchor="nw",
            text="Plataforma visual e intuitiva para iniciar en robótica educativa.",
            fill="#374151", font=("Segoe UI", 12)
        )

        btns = ttk.Frame(canvas)
        canvas.create_window(pad, 320, window=btns, anchor="nw")

        ttk.Button(btns, text="Comenzar Ahora ➜",
                   style="Primary.TButton",
                   command=self.on_login).pack(side="left", padx=(0, 10))

        ttk.Button(btns, text="Ver Más",
                   style="Ghost.TButton").pack(side="left")
