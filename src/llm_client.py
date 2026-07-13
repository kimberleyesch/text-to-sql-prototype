import os
from google import genai
from dotenv import load_dotenv
from pathlib import Path

def get_api():
    """GET API Key from .env"""
    PROJ_ROOT = Path(__file__).resolve().parent.parent
    dotenv_path = PROJ_ROOT.resolve()
    load_dotenv(dotenv_path=dotenv_path)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

    if not GEMINI_API_KEY:
        raise ValueError("Gemini API Key was not found in the environment.")
    
    return GEMINI_API_KEY

def clean_sql_response(response_query):
    """Remove Markdown fences form LLM response."""
    sql_query = response_query.strip()

    sql_query = (
        sql_query
        .removeprefix("```sql")
        .removeprefix("```sqlite")
        .removesuffix("```")
        .strip()
    )

    return sql_query

def generate_sql(client, prompt):
    """Send prompt to LLM and return the generated SQL query"""

    interaction = client.interactions.create(
        model="gemini-3.5-flash",
        input=prompt
    )
    
    sql_response = interaction.output_text

    sql_query = clean_sql_response(sql_response)

    return sql_query
