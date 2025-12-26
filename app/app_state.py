from dataclasses import dataclass
from typing import Optional
from app.model.entities.Usuario import Usuario

@dataclass
class AppState:
    current_user: Optional[Usuario] = None
