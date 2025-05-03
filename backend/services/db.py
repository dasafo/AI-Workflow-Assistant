import os
import psycopg2
from datetime import datetime


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=os.getenv("POSTGRES_PORT", 5432),
    )


def guardar_resumen(user_id, texto_original, resumen):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO resumenes (user_id, texto_original, resumen, fecha)
        VALUES (%s, %s, %s, %s)
        """,
        (user_id, texto_original, resumen, datetime.utcnow()),
    )
    conn.commit()
    cur.close()
    conn.close()


def guardar_traduccion(user_id, texto_original, traduccion):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO traducciones (user_id, texto_original, traduccion, fecha)
        VALUES (%s, %s, %s, %s)
        """,
        (user_id, texto_original, traduccion, datetime.utcnow()),
    )
    conn.commit()
    cur.close()
    conn.close()


def guardar_clasificacion(user_id, texto_original, etiqueta):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO clasificaciones (user_id, texto_original, etiqueta, fecha)
        VALUES (%s, %s, %s, %s)
        """,
        (user_id, texto_original, etiqueta, datetime.utcnow()),
    )
    conn.commit()
    cur.close()
    conn.close()
