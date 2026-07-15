import sqlite3
import pandas as pd
from pathlib import Path
from test_data_generator import create_test_data

DATABASE_PATH = Path(__file__).resolve().parent / "business.db"

INSERT_ORDER = [
    "customers",
    "categories",
    "products",
    "orders",
    "order_items",
]

CREATE_TABLES_SQL = """
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        company_name TEXT NOT NULL,
        industry TEXT,
        company_size TEXT
            CHECK (company_size IN ('small', 'medium', 'large')),
        country TEXT,
        city TEXT,
        acquisition_date TEXT NOT NULL DEFAULT CURRENT_DATE
            CHECK (acquisition_date = date(acquisition_date)
                    AND date(acquisition_date) IS NOT NULL),
        is_active INTEGER NOT NULL DEFAULT 1
            CHECK (is_active IN (1, 0))
    );

    CREATE TABLE categories (
        category_id INTEGER PRIMARY KEY,
        category_name TEXT NOT NULL UNIQUE
    );

    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL UNIQUE,
        category_id INTEGER NOT NULL,
        current_unit_price_cents INTEGER NOT NULL
            CHECK (current_unit_price_cents >= 0),
        current_unit_cost_cents INTEGER NOT NULL
            CHECK (current_unit_cost_cents >= 0),
            
        FOREIGN KEY (category_id)
            REFERENCES categories(category_id)
    );

    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        order_date TEXT NOT NULL DEFAULT CURRENT_DATE
            CHECK (order_date = date(order_date)
                    AND date(order_date) IS NOT NULL),
        order_status TEXT NOT NULL
            CHECK (order_status IN ('pending', 'completed', 'cancelled')),
            
        FOREIGN KEY (customer_id)
            REFERENCES customers(customer_id)
    );

    CREATE TABLE order_items (
        order_item_id INTEGER PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        
        order_unit_price_cents INTEGER NOT NULL
            CHECK (order_unit_price_cents >= 0),
        order_unit_cost_cents INTEGER NOT NULL
            CHECK (order_unit_cost_cents >= 0),

        quantity INTEGER NOT NULL
            CHECK (quantity > 0),
        
        discount_percent INTEGER NOT NULL
            CHECK (discount_percent >= 0 AND discount_percent <= 100),
            
        FOREIGN KEY (order_id)
            REFERENCES orders(order_id),
        FOREIGN KEY (product_id)
            REFERENCES products(product_id)
    );
"""


def get_available_database_path(base_path):
    """Returns an available file path by adding a number if the path already exists."""
    if not base_path.exists():
        return base_path
    
    number = 1

    while True:
        new_path = base_path.with_name(f"{base_path.stem}_{number}{base_path.suffix}")

        if not new_path.exists():
            return new_path
        
        number += 1

def create_database_tables(connection):
    """Creates the database tables using predefined schema."""
    connection.executescript(CREATE_TABLES_SQL)

def formate_date_columns(dataframe):
    """Returns a copy of the dataframe with date columns formated as YYYY-MM-DD-"""
    dataframe = dataframe.copy()

    date_columns = ["acquisition_date", "order_date"]
    
    for column in date_columns:
        if column in dataframe.columns:
            dataframe[column] = (pd.to_datetime(dataframe[column]).dt.strftime("%Y-%m-%d"))

    return dataframe

def insert_test_data(connection):
    """Generates and inserts test data into all database tables."""
    test_data = create_test_data()

    for table_name in INSERT_ORDER:
        dataframe = formate_date_columns(test_data[table_name])

        dataframe.to_sql(
            name=table_name,
            con=connection,
            if_exists="append",
            index=False
        )

        print(f"{len(dataframe)} data rows were successfully transfered to {table_name}.")

def main():
    """Creates the SQLite test database."""

    database_path = get_available_database_path(DATABASE_PATH)

    try:
        with sqlite3.connect(database_path) as connection:
            connection.execute("PRAGMA foreign_keys = ON")

            create_database_tables(connection)
            insert_test_data(connection)

            connection.commit()
    
    except Exception:
        if database_path.exists():
            database_path.unlink()

        raise

    print(f"\nDatabase was successfully created: {database_path.resolve()}")


if __name__ == "__main__":
    main()
