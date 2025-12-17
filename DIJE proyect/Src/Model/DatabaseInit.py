from Src.Model.DataBaseContext import Database


class DatabaseInit:

    @staticmethod
    def initialize():
        conn = Database.get_connection()
        cursor = conn.cursor()

        # TABLA USUARIOS
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL
        )
        """)

        conn.commit()
        cursor.close()
