import tkinter as tk
from tkinter import ttk
from Src.View.Workspace.BloqueArrastrable import BloqueArrastrable


class FrmWorkspace(ttk.Frame):
    def __init__(self, parent, on_exit=None):
        super().__init__(parent)
        

        # callback para salir
        self.on_exit = on_exit or (lambda: None)

        # ===== Estado lógico =====
        self.bloques_logicos = []
        self.cola_ejecucion = []

        # ===== Estado del carrito =====
        self.carrito_x = 130
        self.carrito_y = 130
        self.orientacion = 0   # 0=arriba, 90=derecha, 180=abajo, 270=izquierda

        self.build_ui()

    def build_ui(self):
        self.pack(fill="both", expand=True)

        # ================== BARRA SUPERIOR ==================
        top = ttk.Frame(self, padding=10)
        top.pack(fill="x")

        ttk.Label(
            top,
            text="RoboBlock - Programador de Carrito",
            font=("Segoe UI", 14, "bold")
        ).pack(side="left")

        ttk.Button(
            top,
            text="⏮ Salir",
            command=self.salir
        ).pack(side="right", padx=5)

        ttk.Button(
            top,
            text="▶ Ejecutar",
            command=self.ejecutar_bloques
        ).pack(side="right", padx=5)

        ttk.Button(top, text="⏹ Detener").pack(side="right", padx=5)
        ttk.Button(top, text="🧹 Limpiar").pack(side="right", padx=5)

        ttk.Separator(self).pack(fill="x", pady=5)

        # ================== CUERPO PRINCIPAL ==================
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)

        # ================== PANEL IZQUIERDO ==================
        left = ttk.Frame(body, width=220, padding=10)
        left.grid(row=0, column=0, sticky="ns")

        ttk.Label(
            left,
            text="Bloques Disponibles",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=10)

        # ================== ÁREA DE TRABAJO ==================
        self._crear_canvas(body)

        BloqueArrastrable(left, "⬆ Avanzar", "AVANZAR", self.work_canvas, self).pack(fill="x", pady=5)
        BloqueArrastrable(left, "⬇ Retroceder", "RETROCEDER", self.work_canvas, self).pack(fill="x", pady=5)
        BloqueArrastrable(left, "⟲ Girar Izquierda", "GIRO_IZQ", self.work_canvas, self).pack(fill="x", pady=5)
        BloqueArrastrable(left, "⟳ Girar Derecha", "GIRO_DER", self.work_canvas, self).pack(fill="x", pady=5)

        ttk.Label(
            left,
            text="Arrastra los bloques\nal área de trabajo",
            foreground="gray",
            justify="center"
        ).pack(pady=20)

        # ================== PANEL DERECHO ==================
        right = ttk.Frame(body, width=300, padding=10)
        right.grid(row=0, column=2, sticky="ns")

        ttk.Label(
            right,
            text="Simulación en Tiempo Real",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=5)

        self.sim_canvas = tk.Canvas(
            right,
            width=260,
            height=260,
            bg="#eef2f7",
            highlightthickness=1,
            highlightbackground="#d1d5db"
        )
        self.sim_canvas.pack(pady=10)

        self.carrito = self.sim_canvas.create_rectangle(
            115, 115, 145, 145,
            fill="#2563eb"
        )

    # ================== CANVAS BLOQUES ==================

    def _crear_canvas(self, body):
        center = ttk.Frame(body, padding=10)
        center.grid(row=0, column=1, sticky="nsew")

        ttk.Label(
            center,
            text="Área de Trabajo",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", pady=5)

        ttk.Label(
            center,
            text="Los bloques se ejecutarán en orden de arriba hacia abajo",
            foreground="gray"
        ).pack(anchor="w", pady=(0, 10))

        self.work_canvas = tk.Canvas(
            center,
            bg="#f9fafb",
            bd=1,
            relief="ridge",
            height=400
        )
        self.work_canvas.pack(fill="both", expand=True)

    # ================== EJECUCIÓN ==================

    def ejecutar_bloques(self):
        if not self.bloques_logicos:
            print("No hay bloques para ejecutar")
            return

        self.cola_ejecucion = self.bloques_logicos.copy()
        print("▶ Ejecutando programa")
        self._ejecutar_siguiente()

    def _ejecutar_siguiente(self):
        if not self.cola_ejecucion:
            print("✔ Programa terminado")
            return

        bloque = self.cola_ejecucion.pop(0)

        if bloque == "AVANZAR":
            self._animar_avanzar()
        elif bloque == "RETROCEDER":
            self._animar_retroceder()
        elif bloque == "GIRO_IZQ":
            self._animar_giro(-90)
        elif bloque == "GIRO_DER":
            self._animar_giro(90)

    # ================== ANIMACIONES ==================

    def _animar_avanzar(self):
        self._mover(20, 1)

    def _animar_retroceder(self):
        self._mover(20, -1)

    def _mover(self, pasos_restantes, direccion):
        if pasos_restantes == 0:
            self.after(200, self._ejecutar_siguiente)
            return

        dx, dy = 0, 0
        step = 3 * direccion

        if self.orientacion == 0:
            dy = -step
        elif self.orientacion == 90:
            dx = step
        elif self.orientacion == 180:
            dy = step
        elif self.orientacion == 270:
            dx = -step

        self.sim_canvas.move(self.carrito, dx, dy)
        self.carrito_x += dx
        self.carrito_y += dy

        self.after(30, lambda: self._mover(pasos_restantes - 1, direccion))

    def _animar_giro(self, delta):
        self.orientacion = (self.orientacion + delta) % 360
        self.after(300, self._ejecutar_siguiente)

    # ================== SALIR ==================

    def salir(self):
        self.bloques_logicos.clear()
        self.cola_ejecucion.clear()
        self.on_exit()
