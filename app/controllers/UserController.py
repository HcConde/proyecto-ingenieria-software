import os
import shutil

from app.config.database import get_connection
from app.config.paths import BASE_DIR, PROFILES_DIR
from app.model.entities.Usuario import Usuario


class UserController:
    
    def __init__(self, editar_perfil_uc):
        self.editar_perfil_uc = editar_perfil_uc

    def update_profile(self, user_id, nombre, apellido, fecha_nacimiento, photo_src=None):
        return self.editar_perfil_uc.execute(
            user_id,
            nombre,
            apellido,
            fecha_nacimiento,
            photo_src
        )

