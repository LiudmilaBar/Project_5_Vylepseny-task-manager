import pytest
from task_manager_mysql import (
    pripojeni_db,
    vytvoreni_tabulky,
    pridat_ukol,
    aktualizovat_ukol,
    odstranit_ukol
)

# ---------------------------------------------------------------------------
# FIXTURE – testovací DB, data se po každém testu automaticky smažou
# ---------------------------------------------------------------------------

@pytest.fixture
def db_conn():
    """Připojení k testovací databázi. Testovací data se po testu automaticky smažou."""
    conn = pripojeni_db(test_db=True)
    if conn is None:
        pytest.skip("Nelze se připojit k testovací databázi – přeskakuji testy.")
    vytvoreni_tabulky(conn)
    yield conn
    # Cleanup – smazání všech testovacích dat po každém testu
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ukoly")
    conn.commit()
    cursor.close()
    conn.close()


# ---------------------------------------------------------------------------
# TESTY PŘIDÁNÍ ÚKOLU – pridat_ukol()
# ---------------------------------------------------------------------------

def test_pridat_ukol_pozitivni(db_conn):
    """Pozitivní test: úkol se přidá, vrátí ID a data jsou skutečně v DB."""
    ukol_id = pridat_ukol(db_conn, "Test úkol", "Popis testu")

    # Ověření vráceného ID
    assert ukol_id is not None
    assert isinstance(ukol_id, int)
    assert ukol_id > 0

    # Ověření vlastním SQL dotazem – řádek opravdu existuje v DB
    cursor = db_conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ukoly WHERE id = %s", (ukol_id,))
    ukol = cursor.fetchone()
    cursor.close()

    assert ukol is not None
    assert ukol["nazev"] == "Test úkol"
    assert ukol["popis"] == "Popis testu"
    assert ukol["stav"] == "Nezahájeno"  # výchozí stav po přidání

def test_pridat_ukol_negativni(db_conn):
    """Negativní test: prázdný název a popis způsobí ValueError."""
    with pytest.raises(ValueError):
        pridat_ukol(db_conn, "", "")


# ---------------------------------------------------------------------------
# TESTY AKTUALIZACE ÚKOLU – aktualizovat_ukol()
# ---------------------------------------------------------------------------

def test_aktualizovat_ukol_pozitivni(db_conn):
    """Pozitivní test: stav se změní na 'Hotovo' a DB to potvrdí."""
    ukol_id = pridat_ukol(db_conn, "Aktualizace test", "Popis")

    aktualizovat_ukol(db_conn, ukol_id, "Hotovo")

    # Ověření vlastním SQL dotazem – stav se opravdu změnil
    cursor = db_conn.cursor(dictionary=True)
    cursor.execute("SELECT stav FROM ukoly WHERE id = %s", (ukol_id,))
    ukol = cursor.fetchone()
    cursor.close()

    assert ukol is not None
    assert ukol["stav"] == "Hotovo"

def test_aktualizovat_ukol_negativni(db_conn):
    """Negativní test: neexistující ID způsobí ValueError."""
    with pytest.raises(ValueError):
        aktualizovat_ukol(db_conn, 999999, "Hotovo")


# ---------------------------------------------------------------------------
# TESTY ODSTRANĚNÍ ÚKOLU – odstranit_ukol()
# ---------------------------------------------------------------------------

def test_odstranit_ukol_pozitivni(db_conn):
    """Pozitivní test: úkol se odstraní a v DB již neexistuje."""
    ukol_id = pridat_ukol(db_conn, "Smazání test", "Popis")

    odstranit_ukol(db_conn, ukol_id)

    # Ověření vlastním SQL dotazem – řádek v DB již neexistuje
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ukoly WHERE id = %s", (ukol_id,))
    pocet = cursor.fetchone()[0]
    cursor.close()

    assert pocet == 0

def test_odstranit_ukol_negativni(db_conn):
    """Negativní test: neexistující ID způsobí ValueError."""
    with pytest.raises(ValueError):
        odstranit_ukol(db_conn, 999999)