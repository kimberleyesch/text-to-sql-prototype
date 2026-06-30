import sqlite3
from pathlib import Path


PROJ_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJ_ROOT / "database_setup" / "business.db"


def get_connection():
    """Open in read only mode and return connection to SQLite database."""

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"Database file not found: {DATABASE_PATH}")

    try:
        url_path = DATABASE_PATH.resolve().as_uri() + "?mode=ro"
        return sqlite3.connect(url_path, uri=True)
    
    except sqlite3.Error as e:
        raise sqlite3.Error(f"Could not connect to the database: {e}")


def get_schema():
    """Read and return database schema"""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
                    SELECT sql
                    FROM sqlite_master
                    WHERE type = 'table'
                    AND name NOT LIKE 'sqlite_%'
                    ORDER BY name;
                    """)

    rows = cursor.fetchall()
    statements = []

    for row in rows:
        if row[0] is not None:
            statements.append(row[0])
    
    connection.close()

    schema = "\n\n".join(statements)
    return schema


def execute_query(sql_query):
    """Execute a SELECT query and return all result rows."""

    if not sql_query.strip().lower().startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")
        #TODO add question-number
    
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(sql_query.strip())

        column_names = [desc[0] for desc in cursor.description]

        results = cursor.fetchall()

        return column_names, results
    
    except sqlite3.Error as e:
        raise RuntimeError(f"SQL error occurred: {e}")
    
    finally:
        connection.close()