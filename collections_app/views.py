import sqlite3
from django.shortcuts import render, get_object_or_404

DB_PATH = "data/vinyl.sqlite"


def collections(request):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    collections_list = conn.execute(
        """
        SELECT collections.id,
               collections.name,
               COUNT(collection_records.record_id) AS records_count
        FROM collections
        LEFT JOIN collection_records
               ON collections.id = collection_records.collection_id
        GROUP BY collections.id, collections.name
        ORDER BY collections.name;
        """
    ).fetchall()
    conn.close()
    return render(
        request, "collections/collection_list.html",
        {"collections": collections_list},
    )


def collection_detail(request, collection_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    collection = conn.execute(
        "SELECT id, name FROM collections WHERE id = ?;",
        [collection_id],
    ).fetchone()
    records = []
    if collection:
        records = conn.execute(
            """
            SELECT records.id, records.title, records.artist, records.year
            FROM records
            JOIN collection_records
              ON records.id = collection_records.record_id
            WHERE collection_records.collection_id = ?
            ORDER BY records.title;
            """,
            [collection_id],
        ).fetchall()
    conn.close()
    if collection is None:
        return render(request, "collections/collection_detail.html",
                      {"collection": None}, status=404)
    return render(
        request, "collections/collection_detail.html",
        {"collection": collection, "records": records},
    )


def statistics(request):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    stats = conn.execute(
        """
        SELECT
            (SELECT COUNT(*) FROM records)     AS total_records,
            (SELECT COUNT(*) FROM collections) AS total_collections,
            (SELECT COUNT(*) FROM users)       AS total_users;
        """
    ).fetchone()
    by_collection = conn.execute(
        """
        SELECT collections.name,
               COUNT(collection_records.record_id) AS records_count
        FROM collections
        LEFT JOIN collection_records
               ON collections.id = collection_records.collection_id
        GROUP BY collections.id, collections.name
        ORDER BY records_count DESC;
        """
    ).fetchall()
    conn.close()
    return render(
        request, "collections/statistics.html",
        {"stats": stats, "by_collection": by_collection},
    )
