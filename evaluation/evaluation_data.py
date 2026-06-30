import pandas as pd
from pathlib import Path

EVALUATION_DIR = Path(__file__).resolve().parent
QUESTIONS_PATH = EVALUATION_DIR / "test_questions.xlsx"
# RESULTS_PATH = EVALUATION_DIR / "test_results.xlsx"

def get_questions():
    question_data = pd.read_excel(QUESTIONS_PATH)
    questions = question_data["Test Questions"]

    return questions
