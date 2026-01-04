from app.model.use_cases.MostrarBibliotecaMovimiento import MostrarBibliotecaMovimiento, BlockDef


class BlockController:
    def __init__(self, mostrar_biblioteca_movimiento: MostrarBibliotecaMovimiento):
        self.uc = mostrar_biblioteca_movimiento

    def listar_bloques_movimiento(self, rol_usuario: str | None) -> list[BlockDef]:
        return self.uc.ejecutar(rol_usuario=rol_usuario)
    
