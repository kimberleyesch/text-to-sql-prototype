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

def save_result(question_id, column_names, results, sql_query, target_dir, rag_results=None):
    """Save the query result in a new CSV file"""

    target_dir.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(
        results,
        columns=column_names
    )
    df.insert(0, "Generated SQL-Query", "")
    df.loc[0, "Generated SQL-Query"] = sql_query.replace("\n", " ")

    if rag_results is not None:
        df.insert(1, "RAG Document Sources", "")

        for i, source in enumerate(rag_results["metadatas"][0]):
            df.loc[i, "RAG Document Sources"] = source["source"]

    result_path = get_next_result_path(question_id, target_dir)

    df.to_csv(result_path,
              index=False,
              sep=";",
              encoding="utf-8")
    
def save_executability_results(executability_ids, executability_results, error_messages, target_dir):
    """Save the executability results in a new CSV file"""

    target_dir.mkdir(parents=True, exist_ok=True)

    number_results = len(executability_results)

    n=0
    for i in range(number_results):
        if executability_results[i] == False:
            n+1

    executability_rate = (number_results - n) / number_results * 100

    df = pd.DataFrame({
        "Question ID": executability_ids,
        "Executable": executability_results,
        "Error Message": error_messages,
        "Executability rate": [executability_rate] + [""] * (number_results - 1)
    })

    target_path = target_dir / "Executability_Evaluation.csv"

    df.to_csv(target_path,
              index=False,
              sep=";",
              encoding="utf-8")

    return executability_rate

def save_thinking_summary(question_id, thinking_summary, dir_name):
    """Saves thinking summary of the LLM into text file."""

    file_path = Path(dir_name) / "thinking_summary.txt"

    with open(file_path, "a") as f:
        f.write(f"{question_id}:\n")
        f.write(f"{thinking_summary}\n\n")

def save_rag_distances(question_id, rag_distances, dir_name):
    """Saves document distances of all documents into text file."""

    file_path = Path(dir_name) / "rag_distances.txt"
    
    with open(file_path, "a") as f:
        f.write(f"{question_id}:\n")
        f.write(f"{rag_distances}\n\n")

def get_next_result_path(question_id, dir_name):
    """Return the next available file path name for the question."""

    counter = 1
    results_path = (dir_name /  f"{question_id}_result_{counter}.csv")
    
    while results_path.exists():
        counter += 1
        results_path = dir_name / f"{question_id}_result_{counter}.csv"
        
    return results_path

def get_next_dir_path(dir_name):
    """Return the next available directory path."""

    results_dir = dir_name
    counter = 1

    while results_dir.exists():
        results_dir = Path(f"{dir_name}_{counter}")
        counter += 1

    return Path(results_dir)

def get_results_dir(use_rag, use_extended_questions):
    """Return the directory name in which results should be saved."""

    if use_rag and use_extended_questions:
        results_dir = get_next_dir_path(EXTENDED_RAG_DIR)
    elif use_rag and not use_extended_questions:
        results_dir = get_next_dir_path(STANDARD_RAG_DIR)
    elif not use_rag and use_extended_questions:
        results_dir = get_next_dir_path(EXTENDED_BASELINE_DIR)
    elif not use_rag and not use_extended_questions:
        results_dir = get_next_dir_path(STANDARD_BASELINE_DIR)

    return results_dir

def get_question_path(use_extended_questions):
    """Returns question path."""

    if use_extended_questions:
        question_path = EXTENDED_QUESTIONS_PATH
    else:
        question_path = STANDARD_QUESTIONS_PATH

    return question_path
