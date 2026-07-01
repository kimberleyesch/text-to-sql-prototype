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


def save_result(question_id, column_names, results):
    """Save the query result in new CSV file"""

    RESULTS_PATH.mkdir(exist_ok=True)

    df = pd.DataFrame(
        results,
        columns=column_names
    )

    path_name = get_next_result_path(question_id)

    df.to_csv(path_name, index=False, sep=";")


def get_next_result_path(id):
    """Return the next available file path name for the question"""
    counter = 1

    path_name = RESULTS_PATH / f"{id}_result_{counter}.csv"

    while path_name.exists():
        counter += 1
        path_name = RESULTS_PATH / f"{id}_result_{counter}.csv"
        
    return path_name


def main():
    id = 'Q01'
    col = ['company_name', 'country']
    #col.insert(0, "id")
    list = [('Kirk-Hunter', 'Japan'), ('Nguyen-Burton', 'France'), ('Bush, Brown and Lawrence', 'China'), ('Williams-Lester', 'Chile'), ('Peterson Inc', 'China'), ('Klein, Schmitt and Johnson', 'Colombia'), ('Hancock-Carson', 'India'), ('Fitzpatrick-Walker', 'Canada'), ('Lambert Inc', 'United Kingdom'), ('Martin-Warren', 'Italy'), ('Love-Harris', 'India'), ('Perry-Thompson', 'Brazil')]
    save_result(id, col, list)

if __name__ == "__main__":
    main()