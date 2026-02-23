import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

def pripojeni_db(test_db=False):
    """Připojení k hlavní nebo testovací databázi."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME_TEST") if test_db else os.getenv("DB_NAME"),
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except Error as e:
        print(f"Chyba připojení k databázi: {e}")
        return None


def vytvoreni_tabulky(conn):
    """Vytvoří tabulku ukoly, pokud neexistuje."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ukoly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nazev VARCHAR(255) NOT NULL,
            popis TEXT NOT NULL,
            stav ENUM('Nezahájeno', 'Probíhá', 'Hotovo') DEFAULT 'Nezahájeno',
            datum_vytvoreni TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    """)
    conn.commit()
    cursor.close()


def pridat_ukol(conn, nazev: str, popis: str) -> int:
    """Přidá nový úkol do databáze a vrátí jeho ID."""
    if not nazev or not popis:
        raise ValueError("Název a popis jsou povinné")

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)",
        (nazev, popis)
    )
    conn.commit()
    ukol_id = cursor.lastrowid
    cursor.close()
    return ukol_id


def zobrazit_ukoly(conn) -> List[Dict]:
    """Vrátí seznam aktivních úkolů (Nezahájeno + Probíhá)."""
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, nazev, popis, stav
        FROM ukoly
        WHERE stav IN ('Nezahájeno', 'Probíhá')
        ORDER BY datum_vytvoreni ASC
    """)
    vysledek = cursor.fetchall()
    cursor.close()
    return vysledek


def aktualizovat_ukol(conn, ukol_id: int, novy_stav: str):
    """Aktualizuje stav úkolu podle ID."""
    if novy_stav not in ("Probíhá", "Hotovo"):
        raise ValueError("Neplatný stav")

    cursor = conn.cursor()
    cursor.execute("SELECT id FROM ukoly WHERE id = %s", (ukol_id,))
    if not cursor.fetchone():
        cursor.close()
        raise ValueError("Úkol neexistuje")

    cursor.execute(
        "UPDATE ukoly SET stav = %s WHERE id = %s",
        (novy_stav, ukol_id)
    )
    conn.commit()
    cursor.close()


def odstranit_ukol(conn, ukol_id: int):
    """Odstraní úkol z databáze podle ID."""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM ukoly WHERE id = %s", (ukol_id,))
    if not cursor.fetchone():
        cursor.close()
        raise ValueError("Úkol neexistuje")

    cursor.execute("DELETE FROM ukoly WHERE id = %s", (ukol_id,))
    conn.commit()
    cursor.close()
