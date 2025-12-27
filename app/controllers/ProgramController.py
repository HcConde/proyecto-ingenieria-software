import json
from app.config.database import get_connection


class ProgramController:
    def save_program(self, alumno_id: int, nombre: str, program_list: list[dict]) -> int:
        program_json = json.dumps(program_list, ensure_ascii=False)
        with get_connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO programa (usuario_id, nombre, programa_json, estado)
                VALUES (?, ?, ?, 'CREADO')
                """,
                (alumno_id, nombre.strip(), program_json),
            )
            return int(cur.lastrowid)

    def send_to_teacher(self, programa_id: int, docente_correo: str) -> None:
        docente_correo = docente_correo.strip().lower()
        with get_connection() as conn:
            docente = conn.execute(
                "SELECT id FROM usuario WHERE lower(correo)=? AND rol='DOCENTE'",
                (docente_correo,),
            ).fetchone()
            if not docente:
                raise ValueError("No existe un DOCENTE con ese correo.")

            docente_id = int(docente["id"])

            # vincular
            conn.execute(
                """
                INSERT OR IGNORE INTO docente_proyecto (docente_id, programa_id)
                VALUES (?, ?)
                """,
                (docente_id, programa_id),
            )

            # marcar como enviado
            conn.execute(
                "UPDATE programa SET estado='ENVIADO' WHERE id=?",
                (programa_id,),
            )

    def list_for_teacher(self, docente_id: int) -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute(
                """
                SELECT p.id as programa_id, p.nombre as programa_nombre, p.estado, p.createdAt,
                       u.nombre as alumno_nombre, u.apellido as alumno_apellido, u.correo as alumno_correo
                FROM docente_proyecto dp
                JOIN programa p ON p.id = dp.programa_id
                JOIN usuario u ON u.id = p.usuario_id
                WHERE dp.docente_id = ?
                ORDER BY p.createdAt DESC
                """,
                (docente_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_program_json(self, programa_id: int) -> str:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT programa_json FROM programa WHERE id=?",
                (programa_id,),
            ).fetchone()
            if not row:
                raise ValueError("Programa no encontrado.")
            return row["programa_json"]