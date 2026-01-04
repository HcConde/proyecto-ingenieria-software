from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class BlockDef:
    code: str
    label: str
    param_min: Optional[int] = None
    param_max: Optional[int] = None
    param_default: Optional[int] = None


class MostrarBibliotecaMovimiento:
    """
    CU8: Mostrar Biblioteca de Bloques de Movimiento
    Retorna la lista de bloques predefinidos de movimiento.
    """

    def ejecutar(self, rol_usuario: str | None = None) -> List[BlockDef]:
        # Base: para ALUMNO y DOCENTE
        base = [
            BlockDef(code="AVANZAR", label="Avanzar", param_min=10, param_max=200, param_default=50),
            BlockDef(code="RETROCEDER", label="Retroceder", param_min=10, param_max=200, param_default=50),
            BlockDef(code="GIRAR_IZQ", label="Girar Izq", param_min=0, param_max=180, param_default=90),
            BlockDef(code="GIRAR_DER", label="Girar Der", param_min=0, param_max=180, param_default=90),
            BlockDef(code="DETENER", label="Detener"),
        ]


        return base
