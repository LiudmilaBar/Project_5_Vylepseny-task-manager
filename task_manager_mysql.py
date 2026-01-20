import mysql.connector

from mysql.connector import Error


def pripojeni_db(test_db=False):
    try:
        return mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="aSd123#",
            database="task_manager_test" if test_db else "task_manager"
        )
    except Error as e:
        print(f"Chyba připojení k DB: {e}")
        return None


def vytvoreni_tabulky(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ukoly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nazev VARCHAR(255) NOT NULL,
            popis TEXT NOT NULL,
            stav ENUM('Nezahájeno', 'Probíhá', 'Hotovo') DEFAULT 'Nezahájeno',
            datum_vytvoreni TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
def pridat_ukol(conn, nazev: str, popis: str):
    if not nazev or not popis:
        raise ValueError("Název a popis jsou povinné")

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)",
        (nazev, popis)
    )
    conn.commit()
    return cursor.lastrowid


def zobrazit_ukoly(conn):
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, nazev, popis, stav
        FROM ukoly
        WHERE stav IN ('Nezahájeno', 'Probíhá')
    """)
    return cursor.fetchall()


def aktualizovat_ukol(conn, ukol_id: int, novy_stav: str):
    if novy_stav not in ("Probíhá", "Hotovo"):
        raise ValueError("Neplatný stav")

    cursor = conn.cursor()
    cursor.execute("SELECT id FROM ukoly WHERE id = %s", (ukol_id,))
    if not cursor.fetchone():
        raise ValueError("Úkol neexistuje")

    cursor.execute(
        "UPDATE ukoly SET stav = %s WHERE id = %s",
        (novy_stav, ukol_id)
    )
    conn.commit()


def odstranit_ukol(conn, ukol_id: int):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM ukoly WHERE id = %s", (ukol_id,))
    if not cursor.fetchone():
        raise ValueError("Úkol neexistuje")

    cursor.execute("DELETE FROM ukoly WHERE id = %s", (ukol_id,))
    conn.commit()

#if __name__ == "__main__":
#    conn = pripojeni_db()  # подключение к task_manager
#    if conn:
#        vytvoreni_tabulky(conn)
#        conn.close()
#        print("Tabulka vytvořena v task_manager")