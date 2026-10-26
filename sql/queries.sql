
SELECT id, title, artist, year
FROM records
ORDER BY artist, year;

SELECT id, title, artist, genre
FROM records
WHERE genre LIKE '%Rock%'
ORDER BY title;

SELECT id, title, artist, year
FROM records
WHERE year BETWEEN 1970 AND 1990
ORDER BY year;

SELECT collections.name AS collection_name,
       records.title   AS record_title,
       records.artist  AS artist
FROM collections
JOIN collection_records ON collections.id = collection_records.collection_id
JOIN records            ON records.id     = collection_records.record_id
ORDER BY collections.name, records.title;


SELECT id, name, email FROM users ORDER BY name;

SELECT records.id,
       records.title,
       records.artist,
       COUNT(collection_records.collection_id) AS collections_count
FROM records
LEFT JOIN collection_records ON records.id = collection_records.record_id
GROUP BY records.id, records.title, records.artist
ORDER BY collections_count DESC, records.title;

SELECT collections.id,
       collections.name,
       COUNT(collection_records.record_id) AS records_count
FROM collections
LEFT JOIN collection_records ON collections.id = collection_records.collection_id
GROUP BY collections.id, collections.name
ORDER BY records_count DESC;

SELECT collections.name,
       COUNT(collection_records.record_id) AS records_count
FROM collections
JOIN collection_records ON collections.id = collection_records.collection_id
GROUP BY collections.id, collections.name
HAVING COUNT(collection_records.record_id) > 1
ORDER BY records_count DESC;

SELECT id, title, artist, genre, year
FROM records
WHERE title LIKE '%' || ? || '%'
   OR artist LIKE '%' || ? || '%'
ORDER BY title;

SELECT
    (SELECT COUNT(*) FROM records)     AS total_records,
    (SELECT COUNT(*) FROM collections) AS total_collections,
    (SELECT COUNT(*) FROM users)       AS total_users;

SELECT records.id, records.title, records.artist
FROM records
LEFT JOIN collection_records ON records.id = collection_records.record_id
WHERE collection_records.record_id IS NULL
ORDER BY records.title;

SELECT id, title, artist, year
FROM records
WHERE genre = 'Jazz'
ORDER BY year DESC
LIMIT 10;