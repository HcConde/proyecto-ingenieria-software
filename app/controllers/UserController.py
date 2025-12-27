from app.config.database import get_connection
from app.model.entities.Usuario import Usuario


class UserController:
    def update_profile(self, user_id: int, nombre: str, apellido: str, fecha_nacimiento: str) -> Usuario:
        nombre = nombre.strip()
        apellido = apellido.strip()
        fecha_nacimiento = fecha_nacimiento.strip()

        if not nombre or not apellido or not fecha_nacimiento:
            raise ValueError("Completa nombre, apellido y fecha de nacimiento.")

        with get_connection() as conn:
            conn.execute(
                """
                UPDATE usuario
                SET nombre = ?, apellido = ?, fecha_nacimiento = ?
                WHERE id = ?
                """,
                (nombre, apellido, fecha_nacimiento, user_id),
            )
            row = conn.execute(
                "SELECT id, nombre, apellido, fecha_nacimiento, correo, rol FROM usuario WHERE id=?",
                (user_id,),
            ).fetchone()

        return Usuario(**dict(row))
