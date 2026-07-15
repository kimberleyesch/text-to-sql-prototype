import sqlite3
import sys
from pathlib import Path
import pandas as pd

PROJ_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJ_ROOT))
from src.database_access import get_connection

RESULTS_DIR = Path(__file__).resolve().parent / "results"
RESULTS_WITHOUT_RAG_DIR = RESULTS_DIR / "without_rag"
RESULTS_WITH_RAG_DIR = RESULTS_DIR / "with_rag"


def read_result_data(file_name):
    """Reads generated SQL from test results."""

    required_column = {"Generated SQL-Query"}

    try:
        file_data = pd.read_csv(file_name, sep=";", encoding="utf-8")
    except Exception as error:
        raise RuntimeError("File could not be read.") from error

    if not required_column.issubset(file_data.columns):
        raise ValueError(f"File {file_name} data differs from the expected.")

    if file_data.empty:
        raise ValueError(f"File {file_name} is empty.")

    return file_data

def check_executability():
    """Checks if the generated SQL-queries are executable"""

    executability_results = {}
    executability_failed = []
    result_directories = [RESULTS_WITHOUT_RAG_DIR, RESULTS_WITH_RAG_DIR]

    database_connection = get_connection()

    cursor = database_connection.cursor()
    
    try:
        for result_directory in result_directories:

            for file_path in result_directory.glob("*.csv"):

                file_data = read_result_data(file_path)
                sql_query = file_data["Generated SQL-Query"][0]

                if not sql_query.strip().lower().startswith("select"):
                    raise ValueError(f"Error with file {file_path.name}: Only SELECT queries are allowed.")

                try:
                    cursor.execute(sql_query.strip())

                    column_names = [desc[0] for desc in cursor.description]
                    results = cursor.fetchall()
                    executability = True
                    error_message = None
                
                except sqlite3.Error as e:
                    column_names, results = None, None
                    executability = False
                    error_message = str(e)
                    executability_failed.append(file_path.name)

                executability_results[file_path.name] = {
                    "Executability": executability,
                    "Error Message": error_message,
                    "Column Names": column_names,
                    "Results": results
                }

    finally:
        database_connection.close()
    
    return executability_results, executability_failed

def main():
    executability_results, ex_fail = check_executability()

    print(f"Amount of tests executed: {len(executability_results)}")
    if ex_fail:
       print(ex_fail)
    else:
        print("All generated SQL queries were executed successfully.")


if __name__ == "__main__":
    main()