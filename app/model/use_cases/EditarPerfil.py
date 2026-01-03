class EditarPerfil:
    def __init__(self, usuario_repo, file_service):
        self.usuario_repo = usuario_repo
        self.file_service = file_service

    def execute(self, usuario_id, nombre, apellido, fecha_nacimiento, photo_src=None):
        if not nombre.strip():
            raise ValueError("Nombre obligatorio")
        if not apellido.strip():
            raise ValueError("Apellido obligatorio")
        if not fecha_nacimiento:
            raise ValueError("Fecha de nacimiento obligatoria")

        foto_path_db = None
        if photo_src:
            foto_path_db = self.file_service.save_profile_photo(
                usuario_id, photo_src
            )

        return self.usuario_repo.update_profile(
            usuario_id,
            nombre.strip(),
            apellido.strip(),
            fecha_nacimiento,
            foto_path_db
        )
