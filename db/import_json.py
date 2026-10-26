import json

from db.database import get_connection

RECORDS_FILE = "data/records.json"
COLLECTIONS_FILE = "data/collections.json"
USERS_FILE = "data/users.json"


def load_json(filename):
    with open(filename, encoding="utf-8") as file:
        return json.load(file)


def import_records(conn):
    records = load_json(RECORDS_FILE)
    conn.executemany(
        """
        INSERT INTO records (id, title, artist, genre, year)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                r["id"],
                r["title"],
                r.get("artist", "Неизвестен"),
                r.get("genre", "Не указан"),
                r.get("year", 0),
            )
            for r in records
        ],
    )


def import_users(conn):
    users = load_json(USERS_FILE)
    conn.executemany(
        """
        INSERT INTO users (id, name, email)
        VALUES (?, ?, ?)
        """,
        [(u["id"], u["name"], u["email"]) for u in users],
    )


def import_collections(conn):
    collections = load_json(COLLECTIONS_FILE)
    # 1) коллекции
    conn.executemany(
        """
        INSERT INTO collections (id, name)
        VALUES (?, ?)
        """,
        [(c["id"], c["name"]) for c in collections],
    )
    # 2) связи collection_records
    links = []
    for c in collections:
        for record_id in c.get("record_ids", []):
            links.append((c["id"], record_id))
    conn.executemany(
        """
        INSERT INTO collection_records (collection_id, record_id)
        VALUES (?, ?)
        """,
        links,
    )


def main():
    conn = get_connection()
    try:
        import_records(conn)
        import_users(conn)
        import_collections(conn)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
