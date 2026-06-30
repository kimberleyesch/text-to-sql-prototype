from src.database_access import get_schema
from src.database_access import execute_query
from src.prompt_builder import build_prompt
from src.llm_client import generate_sql

question = "Show all medium sized companies"

schema = get_schema()
prompt = build_prompt(question, schema)
sql_query = generate_sql(prompt)
column_names, results = execute_query(sql_query)

print(" | ".join(column_names))

for row in results:
    print(row)