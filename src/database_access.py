import sqlite3
from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJ_ROOT / "database_setup" / "business.db"

def get_connection():
    """Open and return connection to SQLite database."""

    if not DATABASE_PATH.exists():
        raise FileNotFoundError(f"Database file not found: {DATABASE_PATH}")

    try:
        return sqlite3.connect(DATABASE_PATH)
    
    except sqlite3.Error as e:
        raise sqlite3.Error(f"Could not connect to the database: {e}")

def get_schema():
    """Read and return database schema"""

    connetion = get_connection()
    cursor = connetion.cursor()

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
    
    connetion.close()

    schema = "\n\n".join(statements)
    return schema