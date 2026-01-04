from app.model.entities.SecuenciaBloques import SecuenciaBloques
from app.model.entities.Bloque import Bloque


class CrearBloquePersonalizado:

    def ejecutar(self, bloques_ui: list) -> SecuenciaBloques:

        if not bloques_ui:
            raise ValueError("No hay bloques ensamblados")

        bloques = []

        for b in bloques_ui:
            code = b.get("code")
            value = b.get("value")

            if code == "AVANZAR":
                bloques.append(Bloque("AVANZAR", valor=value))

            elif code == "RETROCEDER":
                bloques.append(Bloque("RETROCEDER", valor=value))

            elif code == "GIRAR_IZQ":
                bloques.append(Bloque("GIRAR_IZQ", valor=value))

            elif code == "GIRAR_DER":
                bloques.append(Bloque("GIRAR_DER", valor=value))

            elif code == "DETENER":
                bloques.append(Bloque("DETENER"))

            else:
                raise ValueError(f"Bloque desconocido: {code}")

        return SecuenciaBloques(bloques)
