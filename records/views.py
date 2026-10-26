import sqlite3
from django.shortcuts import render

DB_PATH = "data/vinyl.sqlite"


def records(request):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    records_list = conn.execute(
        """
        SELECT id, title, artist, genre, year
        FROM records
        ORDER BY title;
        """
    ).fetchall()
    conn.close()
    return render(request,
                  "records/record_list.html",
                  {"records": records_list})


def record_detail(request, record_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    record = conn.execute(
        "SELECT id, title, artist, genre, year FROM records WHERE id = ?;",
        [record_id],
    ).fetchone()
    conn.close()
    return render(
        request,
        "records/record_detail.html",
        {"record": record},
        status=404 if record is None else 200,
    )


def search_records(request):
    query = request.GET.get("q", "").strip()
    results = []
    if query:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        results = conn.execute(
            """
            SELECT id, title, artist, genre, year
            FROM records
            WHERE title LIKE '%' || ? || '%'
               OR artist LIKE '%' || ? || '%'
            ORDER BY title;
            """,
            [query, query],
        ).fetchall()
        conn.close()
    return render(
        request,
        "records/search.html",
        {"results": results, "query": query},
    )
