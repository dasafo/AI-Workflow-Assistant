import os
import psycopg2


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

    # Verifica si ya existe un registro idéntico
    cur.execute(
        """
        SELECT COUNT(*) FROM resumenes
        WHERE user_id = %s AND texto_original = %s AND resumen = %s
        """,
        (user_id, texto_original, resumen),
    )
    count = cur.fetchone()[0]

    # Solo inserta si no existe
    if count == 0:
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
