from Src.Model.DataBaseContext import Database


class UsuarioModel:

    @staticmethod
    def registrar(nombre, correo, password):
        conn = Database.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO usuarios (nombre, correo, password, rol) VALUES (?, ?, ?, ?)",
                (nombre, correo, password, "ALUMNO")
            )
            conn.commit()
            return True

        except Exception:
            return False

        finally:
            cursor.close()

    @staticmethod
    def login(correo, password):
        conn = Database.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id_usuario, nombre, correo, rol FROM usuarios WHERE correo=? AND password=?",
            (correo, password)
        )

        user = cursor.fetchone()
        cursor.close()

        if user is None:
            return None

        return {
            "id": user[0],
            "nombre": user[1],
            "correo": user[2],
            "rol": user[3]
        }
