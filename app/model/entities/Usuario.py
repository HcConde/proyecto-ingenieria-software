from dataclasses import dataclass
from typing import Optional

@dataclass
class Usuario:
    id: int
    nombre: str
    apellido: str
    fecha_nacimiento: str
    correo: str
    rol: str
    foto_path: str | None = None
