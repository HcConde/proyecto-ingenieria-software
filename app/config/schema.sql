
PRAGMA foreign_keys = ON;


CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    fecha_nacimiento TEXT NOT NULL, -- 'YYYY-MM-DD'
    correo TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    rol TEXT NOT NULL CHECK (rol IN ('ALUMNO', 'DOCENTE')),
    createdAt TEXT DEFAULT CURRENT_TIMESTAMP,
    updatedAt TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER IF NOT EXISTS trg_usuario_updated
AFTER UPDATE ON usuario
FOR EACH ROW
BEGIN
  UPDATE usuario SET updatedAt = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;


CREATE TABLE IF NOT EXISTS block_definition (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    categoria TEXT NOT NULL,
    parametros_schema TEXT NOT NULL,   -- JSON (texto)
    es_sistema INTEGER NOT NULL DEFAULT 1 CHECK (es_sistema IN (0,1))
);


CREATE TABLE IF NOT EXISTS custom_block (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    definicion_json TEXT NOT NULL,
    createdAt TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS programa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    programa_json TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'CREADO' CHECK (estado IN ('CREADO','ENVIADO','REVISADO')),
    createdAt TEXT DEFAULT CURRENT_TIMESTAMP,
    updatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
);

CREATE TRIGGER IF NOT EXISTS trg_programa_updated
AFTER UPDATE ON programa
FOR EACH ROW
BEGIN
  UPDATE programa SET updatedAt = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;


CREATE TABLE IF NOT EXISTS docente_proyecto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    docente_id INTEGER NOT NULL,
    programa_id INTEGER NOT NULL,
    FOREIGN KEY (docente_id) REFERENCES usuario(id) ON DELETE CASCADE,
    FOREIGN KEY (programa_id) REFERENCES programa(id) ON DELETE CASCADE,
    UNIQUE(docente_id, programa_id)
);


CREATE TABLE IF NOT EXISTS evaluacion (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    programa_id INTEGER NOT NULL,
    docente_id INTEGER NOT NULL,
    observaciones TEXT,
    puntaje INTEGER CHECK (puntaje BETWEEN 0 AND 20),
    createdAt TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (programa_id) REFERENCES programa(id) ON DELETE CASCADE,
    FOREIGN KEY (docente_id) REFERENCES usuario(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS dispositivo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    nombre TEXT,
    mac_address TEXT,
    ultimo_estado TEXT,
    last_seen TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
);
