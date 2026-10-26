

CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    genre TEXT,
    year INTEGER
);

CREATE TABLE IF NOT EXISTS collections (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS collection_records (
    collection_id INTEGER NOT NULL,
    record_id INTEGER NOT NULL,
    PRIMARY KEY (collection_id, record_id),
    FOREIGN KEY (collection_id) REFERENCES collections(id),
    FOREIGN KEY (record_id) REFERENCES records(id)
);