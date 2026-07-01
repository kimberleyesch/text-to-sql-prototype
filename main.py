from src.database_access import get_schema
from src.database_access import execute_query
from src.prompt_builder import build_prompt
from src.llm_client import generate_sql
from evaluation.evaluation_data import get_questions
from evaluation.evaluation_data import save_result

def main():
    """Run complete Text-to-SQL workflow

    Read database schema and test questions, send prompt to LLM, receive SQL-queries,
    execute queries in SQL and save results.
    """

    schema = get_schema()
    questions, question_ids = get_questions()

    for i in range(3):
        question_id = question_ids[i]
        question = questions[i]
    # for question_id, question in zip(question_ids, questions):

        prompt = build_prompt(question, schema)
        sql_query = generate_sql(prompt)
        column_names, results = execute_query(sql_query)
        save_result(question_id, column_names, results)

        print(f"\nQuestion: {question}")
        print("\n")
        print(" | ".join(column_names))

        for row in results:
            print(row)

if __name__ == "__main__":
    main()