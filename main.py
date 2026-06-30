from src.database_access import get_schema
from src.database_access import execute_query
from src.prompt_builder import build_prompt
from src.llm_client import generate_sql
from evaluation.evaluation_data import get_questions

def main():
    question = "Show all medium sized companies"

    schema = get_schema()
    questions = get_questions()
    question = questions[1]
    prompt = build_prompt(question, schema)
    sql_query = generate_sql(prompt)
    column_names, results = execute_query(sql_query)

    print(f"\nQuestion: {question}")
    print("\n")
    print(" | ".join(column_names))

    for row in results:
        print(row)

if __name__ == "__main__":
    main()