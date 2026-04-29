import pymysql
import time

db_config = {
    'host': 'localhost',
    'user': 'admin',
    'password': 'admin',
    'database': 'pz11',
    'port': 3306
}

queries = [
    "SELECT * FROM dataset WHERE track_genre = 'Pop' LIMIT 1000",
    "SELECT artists, AVG(popularity) as avg_popularity, COUNT(*) as cnt FROM dataset GROUP BY artists ORDER BY cnt DESC",
    "SELECT * FROM dataset WHERE popularity >= 70 AND energy BETWEEN 0.5 AND 0.8 ORDER BY popularity DESC LIMIT 500",
    "SELECT track_genre, COUNT(*) as total_tracks, AVG(duration_ms) as avg_duration FROM dataset GROUP BY track_genre",
    "SELECT * FROM dataset WHERE track_id = '12345'",
    "SELECT artists, AVG(danceability) as avg_danceability, "
    "COUNT(*) as tracks FROM dataset GROUP BY artists HAVING COUNT(*) > 10",
    "SELECT COUNT(*) FROM dataset WHERE album_name LIKE '%Greatest%' OR album_name LIKE '%Best%'",
    "SELECT artists, COUNT(*) as track_count FROM dataset "
    "WHERE explicit = 'True' GROUP BY artists ORDER BY track_count DESC LIMIT 10",
    "SELECT track_genre, explicit, COUNT(*) as cnt FROM dataset GROUP BY track_genre, explicit",
    "SELECT track_genre, AVG(energy) as avg_energy, AVG(danceability) "
    "as avg_danceability FROM dataset WHERE popularity > 50 GROUP BY track_genre HAVING AVG(energy) > 0.6"
]


def run_query(conn, query):
    with conn.cursor() as cursor:
        start = time.perf_counter()
        cursor.execute(query)
        _ = cursor.fetchall()
        return round(time.perf_counter() - start, 4)


def main():
    print("Phase 1: Benchmark without indexes")
    conn = pymysql.connect(**db_config)
    t1 = [run_query(conn, q) for q in queries]
    for i, v in enumerate(t1, 1):
        print(f"Query {i:2d}: {v:.4f} sec")
    conn.close()

    print("\nCreating indexes...")
    conn = pymysql.connect(**db_config)
    indexes = [
        "CREATE INDEX idx_track_genre ON dataset(track_genre(100))",
        "CREATE INDEX idx_artists ON dataset(artists(100))",
        "CREATE INDEX idx_popularity ON dataset(popularity)",
        "CREATE INDEX idx_energy ON dataset(energy)",
        "CREATE INDEX idx_track_id ON dataset(track_id(100))",
        "CREATE INDEX idx_album_name ON dataset(album_name(100))",
        "CREATE INDEX idx_explicit ON dataset(explicit(10))",
        "CREATE INDEX idx_danceability ON dataset(danceability)",
        "CREATE INDEX idx_genre_explicit ON dataset(track_genre(50), explicit(10))",
        "CREATE INDEX idx_duration ON dataset(duration_ms)"
    ]
    with conn.cursor() as cursor:
        for sql in indexes:
            try:
                cursor.execute(sql)
                print(f"  Created: {sql.split('ON')[0].split()[1]}")
            except Exception as e:
                print(f"  Skipped: {e}")
    conn.commit()
    print("Indexes created.")
    conn.close()

    print("\nPhase 2: Benchmark with indexes")
    conn = pymysql.connect(**db_config)
    t2 = [run_query(conn, q) for q in queries]
    for i, v in enumerate(t2, 1):
        print(f"Query {i:2d}: {v:.4f} sec")
    conn.close()


if __name__ == "__main__":
    main()
