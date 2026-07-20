import pandas as pd
from pathlib import Path

EVALUATION_DIR = Path(__file__).resolve().parent

# Question path
STANDARD_QUESTIONS_PATH = EVALUATION_DIR / "test_questions.xlsx"
EXTENDED_QUESTIONS_PATH = EVALUATION_DIR / "test_questions_extended.xlsx"
# Results path
RESULTS_DIR = EVALUATION_DIR / "results"
STANDARD_BASELINE_DIR = RESULTS_DIR / "baseline"
STANDARD_RAG_DIR = RESULTS_DIR / "rag"
EXTENDED_BASELINE_DIR = RESULTS_DIR / "extended_baseline"
EXTENDED_RAG_DIR = RESULTS_DIR / "extended_rag"


def get_questions(question_path):
    """Read test question and ID from Excel file."""
    question_data = pd.read_excel(question_path, dtype={"ID": str})

    required_columns = {"ID", "Test Questions"}

    if not required_columns.issubset(question_data.columns):
        raise ValueError(f"Excel file doesn't contain required columns: {required_columns}")

    questions = question_data["Test Questions"]
    question_ids = question_data["ID"].str.strip().to_list()

    return questions, question_ids

def save_result(question_id, column_names, results, sql_query, target_dir):
    """Save the query result in a new CSV file"""

    target_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(
        results,
        columns=column_names
    )
    df.insert(0, "Generated SQL-Query", "")
    df.loc[0, "Generated SQL-Query"] = sql_query.replace("\n", " ")

    result_path = get_next_result_path(question_id, target_dir)

    df.to_csv(result_path,
              index=False,
              sep=";",
              encoding="utf-8")
    
def save_executability_results(executability_ids, executability_results, error_messages, target_dir):
    """Save the executability results in a new CSV file"""

    target_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame({
        "Question ID": executability_ids,
        "Executable": executability_results,
        "Error Message": error_messages
    })

    target_path = target_dir / "Executability_Evaluation.csv"

    df.to_csv(target_path,
              index=False,
              sep=";",
              encoding="utf-8")

def get_next_result_path(question_id, dir_name):
    """Return the next available file path name for the question."""

    counter = 1
    results_path = (dir_name /  f"{question_id}_result_{counter}.csv")
    
    while results_path.exists():
        counter += 1
        results_path = dir_name / f"{question_id}_result_{counter}.csv"
        
    return results_path

def get_results_dir(use_rag, use_extended_questions):
    if use_rag and use_extended_questions:
        results_dir = EXTENDED_RAG_DIR
    elif use_rag and not use_extended_questions:
        results_dir = STANDARD_RAG_DIR
    elif not use_rag and use_extended_questions:
        results_dir = EXTENDED_BASELINE_DIR
    elif not use_rag and not use_extended_questions:
        results_dir = STANDARD_BASELINE_DIR

    return results_dir

def get_question_path(use_extended_questions):
    if use_extended_questions:
        question_path = EXTENDED_QUESTIONS_PATH
    else:
        question_path = STANDARD_QUESTIONS_PATH

    return question_path
