from database.database import Database


def add_tables():
    query = (
        "CREATE TABLE IF NOT EXISTS users ("
        "user_id BIGINT PRIMARY KEY,"
        "handle TEXT NOT NULL UNIQUE"
        ")"
    )
    Database.execute_query(query)
