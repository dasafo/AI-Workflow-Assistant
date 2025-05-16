-- Migración para unificar las tablas de consultas en una sola
-- y crear tabla de estado de usuario

-- Crear tabla unificada de consultas
CREATE TABLE IF NOT EXISTS consultas_ia (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT NOT NULL,
    tipo_tarea TEXT NOT NULL,  -- 'resumir', 'clasificar', 'traducir', 'consultar', etc.
    texto_original TEXT NOT NULL,
    resultado TEXT,
    idioma TEXT DEFAULT NULL,  -- Solo para traducciones
    fecha TIMESTAMP DEFAULT NOW()
);

-- Crear índices para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_consultas_ia_chat_id ON consultas_ia(chat_id);
CREATE INDEX IF NOT EXISTS idx_consultas_ia_tipo_tarea ON consultas_ia(tipo_tarea);
CREATE INDEX IF NOT EXISTS idx_consultas_ia_fecha ON consultas_ia(fecha);

-- Crear tabla de estado de usuario
CREATE TABLE IF NOT EXISTS estado_usuario (
    chat_id BIGINT PRIMARY KEY,
    modo_actual TEXT,  -- '/resumir', '/clasificar', etc.
    fecha TIMESTAMP DEFAULT NOW()
);

-- Migrar datos existentes (si hay)
INSERT INTO consultas_ia (chat_id, tipo_tarea, texto_original, resultado, fecha)
SELECT 
    CAST(user_id AS BIGINT), 
    'resumir', 
    texto_original, 
    resumen, 
    fecha 
FROM resumenes
ON CONFLICT DO NOTHING;

INSERT INTO consultas_ia (chat_id, tipo_tarea, texto_original, resultado, idioma, fecha)
SELECT 
    CAST(user_id AS BIGINT), 
    'traducir', 
    texto_original, 
    traduccion, 
    idioma,
    fecha 
FROM traducciones
ON CONFLICT DO NOTHING;

INSERT INTO consultas_ia (chat_id, tipo_tarea, texto_original, resultado, fecha)
SELECT 
    CAST(user_id AS BIGINT), 
    'clasificar', 
    texto, 
    clasificacion, 
    created_at 
FROM clasificaciones
ON CONFLICT DO NOTHING; 