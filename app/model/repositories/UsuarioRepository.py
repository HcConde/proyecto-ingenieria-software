from app.config.database import get_connection
from app.model.entities.Usuario import Usuario


class UsuarioRepository:
    def find_by_correo(self, correo: str) -> Usuario | None:
        correo = correo.strip().lower()
        with get_connection() as conn:
            row = conn.execute(
                "SELECT id, nombre, apellido, fecha_nacimiento, correo, rol, foto_path FROM usuario WHERE correo = ?",
                (correo,),
            ).fetchone()
            if not row:
                return None
            return Usuario(**dict(row))

    def find_auth_row(self, correo: str):
        """Devuelve fila con password_hash para login."""
        correo = correo.strip().lower()
        with get_connection() as conn:
            return conn.execute(
                "SELECT * FROM usuario WHERE correo = ?",
                (correo,),
            ).fetchone()

    def create_user(self, nombre, apellido, fecha_nacimiento, correo, password_hash, rol) -> int:
        correo = correo.strip().lower()
        with get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO usuario (nombre, apellido, fecha_nacimiento, correo, password_hash, rol)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (nombre.strip(), apellido.strip(), fecha_nacimiento.strip(), correo, password_hash, rol),
            )
            return int(cur.lastrowid)
    

    def update_profile(self, usuario_id, nombre, apellido, fecha_nacimiento, foto_path=None):
        with get_connection() as conn:
            if foto_path:
                conn.execute(
                    """
                    UPDATE usuario
                    SET nombre=?, apellido=?, fecha_nacimiento=?, foto_path=?
                    WHERE id=?
                    """,
                    (nombre, apellido, fecha_nacimiento, foto_path, usuario_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE usuario
                    SET nombre=?, apellido=?, fecha_nacimiento=?
                    WHERE id=?
                    """,
                    (nombre, apellido, fecha_nacimiento, usuario_id),
                )

            row = conn.execute(
                """
                SELECT id, nombre, apellido, fecha_nacimiento, correo, rol, foto_path
                FROM usuario
                WHERE id=?
                """,
                (usuario_id,),
            ).fetchone()

        if not row:
            raise ValueError("Usuario no encontrado")

        return Usuario(**dict(row))
