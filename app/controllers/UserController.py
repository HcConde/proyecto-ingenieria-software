import os
import shutil

from app.config.database import get_connection
from app.config.paths import BASE_DIR, PROFILES_DIR
from app.model.entities.Usuario import Usuario


class UserController:
    def update_profile(self, user_id, nombre, apellido, fecha_nacimiento, photo_src=None):
        os.makedirs(PROFILES_DIR, exist_ok=True)

        foto_path_db = None

        if photo_src:
            ext = os.path.splitext(photo_src)[1].lower()
            if ext not in (".png", ".jpg", ".jpeg", ".webp"):
                ext = ".png"

            dest_abs = os.path.join(PROFILES_DIR, f"user_{user_id}{ext}")
            shutil.copy2(photo_src, dest_abs)

            foto_path_db = os.path.relpath(dest_abs, BASE_DIR).replace("\\", "/")

        with get_connection() as conn:
            if foto_path_db:
                conn.execute(
                    """
                    UPDATE usuario
                    SET nombre=?, apellido=?, fecha_nacimiento=?, foto_path=?
                    WHERE id=?
                    """,
                    (nombre, apellido, fecha_nacimiento, foto_path_db, user_id),
                )
            else:
                conn.execute(
                    """
                    UPDATE usuario
                    SET nombre=?, apellido=?, fecha_nacimiento=?
                    WHERE id=?
                    """,
                    (nombre, apellido, fecha_nacimiento, user_id),
                )

            row = conn.execute(
                """
                SELECT id, nombre, apellido, fecha_nacimiento, correo, rol, foto_path
                FROM usuario WHERE id=?
                """,
                (user_id,),
            ).fetchone()

        return Usuario(**dict(row))
