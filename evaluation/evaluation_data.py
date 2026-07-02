import pandas as pd
from pathlib import Path

EVALUATION_DIR = Path(__file__).resolve().parent
QUESTIONS_PATH = EVALUATION_DIR / "test_questions.xlsx"
RESULTS_PATH = EVALUATION_DIR / "results"


def get_questions():
    """Read test question and ID from Excel file."""
    question_data = pd.read_excel(QUESTIONS_PATH, dtype={"ID": str})

    required_columns = {"ID", "Test Questions"}

    if not required_columns.issubset(question_data.columns):
        raise ValueError(f"Excel file doesn't contain required columns: {required_columns}")

    questions = question_data["Test Questions"]
    question_ids = question_data["ID"].str.strip().to_list()

    return questions, question_ids

def save_result(question_id, column_names, results, sql_query):
    """Save the query result in new CSV file"""

    RESULTS_PATH.mkdir(exist_ok=True)

    df = pd.DataFrame(
        results,
        columns=column_names
    )
    df.insert(0, "Generated SQL-Query", "")
    df.loc[0, "Generated SQL-Query"] = sql_query.replace("\n", " ")

    path_name = get_next_result_path(question_id)

    df.to_csv(path_name,
              index=False,
              sep=";",
              encoding="utf-8")

def get_next_result_path(id):
    """Return the next available file path name for the question"""
    counter = 1

    path_name = RESULTS_PATH / f"{id}_result_{counter}.csv"

    while path_name.exists():
        counter += 1
        path_name = RESULTS_PATH / f"{id}_result_{counter}.csv"
        
    return path_name
