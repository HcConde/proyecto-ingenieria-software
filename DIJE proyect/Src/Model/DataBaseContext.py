import sqlite3
import os
import sys


class Database:
    _connection = None

    @staticmethod
    def _get_db_path():
        """
        Devuelve la ruta correcta tanto en modo script
        como en modo .exe (PyInstaller)
        """
        if hasattr(sys, "_MEIPASS"):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        return os.path.join(base_path, "roboblock.db")

    @staticmethod
    def get_connection():
        if Database._connection is None:
            db_path = Database._get_db_path()
            Database._connection = sqlite3.connect(db_path)
        return Database._connection
