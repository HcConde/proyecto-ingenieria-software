from dataclasses import dataclass

@dataclass
class Usuario:
    id: int
    nombre: str
    apellido: str
    fecha_nacimiento: str
    correo: str
    rol: str  
