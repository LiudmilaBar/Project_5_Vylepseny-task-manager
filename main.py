import task_manager_mysql as db

def pridat_ukol(conn) -> None:
    """Umožní uživateli přidat úkol do DATABÁZE."""
    print("\n--- Přidat nový úkol ---")

    while True:
        nazev = input("Zadejte název úkolu: ").strip()
        if not nazev:
            print("Název úkolu je povinný a nesmí být prázdný.")
            continue

        popis = input("Zadejte popis úkolu: ").strip()
        if not popis:
            print("Popis úkolu je povinný a nesmí být prázdný.")
            continue

        #Funkce z DB
        try:
            ukol_id = db.pridat_ukol(conn, nazev, popis)
            print(f"Úkol '{nazev}' byl úspěšně přidán s ID {ukol_id}.\n")
            break 
        except Exception as e:
            print(f"Chyba při ukládání: {e}\n")
            break

def zobrazit_ukoly(conn) -> None:
    """Zobrazí všechny úkoly přímo z DATABÁZE."""
    print("\n--- Seznam aktivních úkolů ---")
    ukoly = db.zobrazit_ukoly(conn) # Data z SQL
    
    if not ukoly:
        print("Seznam úkolů v databázi je prázdný.\n")
        return

    print("Seznam úkolů (z databáze):")
    for u in ukoly:
        print(f"ID: {u['id']} | Úkol: {u['nazev']} | Stav: {u['stav']}")
    print()

def aktualizovat_ukol(conn) -> None:
    """Umožní uživateli aktualizovat stav existujícího úkolu."""
    print("\n--- Aktualizovat úkol ---")
    
    zobrazit_ukoly(conn)
    
    try:
        id_ukolu = int(input("Zadejte ID úkolu, který chcete aktualizovat: "))
        
        print("\nVyberte nový stav:")
        print("1. Probíhá")
        print("2. Hotovo")
        volba = input("Zadejte číslo (1-2): ").strip()
        
        stavy = {"1": "Probíhá", "2": "Hotovo"}
        
        if volba not in stavy:
            print("Neplatná volba.\n")
            return
        
        novy_stav = stavy[volba]
        db.aktualizovat_ukol(conn, id_ukolu, novy_stav)
        print(f"Úkol s ID {id_ukolu} byl aktualizován na stav '{novy_stav}'.\n")
        
    except ValueError as e:
        if "invalid literal" in str(e):
            print("Zadejte platné číslo ID.\n")
        else:
            print(f"Chyba: {e}\n")
    except Exception as e:
        print(f"Chyba: {e}\n")

def odstranit_ukol(conn) -> None:
    """Odstraní úkol z databáze podle ID."""
    print("\n--- Odstranit úkol ---")
    
    zobrazit_ukoly(conn)
    
    try:
        id_ukolu = int(input("Zadejte ID úkolu, který chcete odstranit: "))
        
        potvrzeni = input(f"Opravdu chcete odstranit úkol s ID {id_ukolu}? (ano/ne): ").strip().lower()
        
        if potvrzeni == "ano":
            db.odstranit_ukol(conn, id_ukolu)
            print(f"Úkol s ID {id_ukolu} byl odstraněn.\n")
        else:
            print("Odstranění zrušeno.\n")
            
    except ValueError as e:
        if "invalid literal" in str(e):
            print("Zadejte platné číslo ID.\n")
        else:
            print(f"Chyba: {e}\n")
    except Exception as e:
        print(f"Chyba: {e}\n")


def hlavni_menu() -> None:
    """Hlavní menu aplikace pro správu úkolů."""
    # Připojení k databázi při startu
    conn = db.pripojeni_db()
    if not conn:
        print("Chyba: Nepodařilo se připojit k databázi.")
        print("Zkontrolujte prosím:")
        print("  - Soubor .env s přihlašovacími údaji")
        print("  - Běžící MySQL server")
        print("  - Existující databázi")
        return

    # Vytvoření tabulky, pokud neexistuje
    try:
        db.vytvoreni_tabulky(conn)
    except Exception as e:
        print(f"Chyba při vytváření tabulky: {e}")
        conn.close()
        return

    print("=" * 50)
    print("   SPRÁVCE ÚKOLŮ (MySQL)")
    print("=" * 50)

    while True:
        print("\n--- Hlavní menu ---")
        print("1. Přidat nový úkol")
        print("2. Zobrazit úkoly")
        print("3. Aktualizovat stav úkolu")
        print("4. Odstranit úkol")
        print("5. Ukončit program")

        volba = input("\nVyberte možnost (1-5): ").strip()

        if volba == "1":
            pridat_ukol(conn)
        elif volba == "2":
            zobrazit_ukoly(conn)
        elif volba == "3":
            aktualizovat_ukol(conn)
        elif volba == "4":
            odstranit_ukol(conn)
        elif volba == "5":
            conn.close()
            print("\n Databázové připojení ukončeno.")
            print("Děkujeme za použití správce úkolů. Na shledanou!")
            break
        else:
            print("Neplatná volba. Zvolte číslo 1-5.\n")


if __name__ == "__main__":
    hlavni_menu()