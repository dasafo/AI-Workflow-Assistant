# db.py - VERSIÓN PARA DOCKER
import psycopg2
import os


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "workflowdb"),
        user=os.getenv("POSTGRES_USER", "david"),
        password=os.getenv("POSTGRES_PASSWORD", "superclave"),
    )


def guardar_resumen(user_id, texto_original, resumen):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO resumenes (user_id, texto_original, resumen)
        VALUES (%s, %s, %s)
        """,
        (user_id, texto_original, resumen),
    )
    conn.commit()
    cur.close()
    conn.close()
