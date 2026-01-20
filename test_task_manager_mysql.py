import pytest
from task_manager_mysql import (
    pripojeni_db,
    vytvoreni_tabulky,
    pridat_ukol,
    aktualizovat_ukol,
    odstranit_ukol
)

@pytest.fixture
def db_conn():
    conn = pripojeni_db(test_db=True)
    vytvoreni_tabulky(conn)
    yield conn
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ukoly")
    conn.commit()
    conn.close()


#TESTY PŘIDÁNÍ ÚKOLU

def test_pridat_ukol_ok(db_conn):
    ukol_id = pridat_ukol(db_conn, "Test", "Popis")
    assert ukol_id is not None

def test_pridat_ukol_neplatny(db_conn):
    with pytest.raises(ValueError):
        pridat_ukol(db_conn, "", "")


#TESTY AKTUALIZACE ÚKOLU

def test_aktualizovat_ukol_ok(db_conn):
    ukol_id = pridat_ukol(db_conn, "Test", "Popis")
    aktualizovat_ukol(db_conn, ukol_id, "Hotovo")

def test_aktualizovat_ukol_neexistuje(db_conn):
    with pytest.raises(ValueError):
        aktualizovat_ukol(db_conn, 9999, "Hotovo")


#TESTY ODSTRANĚNÍ ÚKOLU

def test_odstranit_ukol_ok(db_conn):
    ukol_id = pridat_ukol(db_conn, "Test", "Popis")
    odstranit_ukol(db_conn, ukol_id)


def test_odstranit_ukol_neexistuje(db_conn):
    with pytest.raises(ValueError):
        odstranit_ukol(db_conn, 9999)