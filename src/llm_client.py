import os
from google import genai
from dotenv import load_dotenv
from pathlib import Path

PROJ_ROOT = Path(__file__).resolve().parent.parent
DOTENV_FILE = PROJ_ROOT / ".env"


def get_api():
    """GET API Key from .env"""

    load_dotenv(dotenv_path=DOTENV_FILE)
    gemini_api_key = os.getenv('GEMINI_API_KEY')

    if not gemini_api_key:
        raise ValueError("Gemini API Key was not found in the environment.")
    
    return gemini_api_key

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
    """Send prompt to LLM and return the generated SQL query and thinking summary"""

    interaction = client.interactions.create(
        model="gemini-3.5-flash",
        input=prompt,
        generation_config={
            "thinking_summaries": "auto"
        }
    )
    
    sql_response = interaction.output_text
    sql_query = clean_sql_response(sql_response)

    for step in interaction.steps:
        if step.type == "thought":
            print("Thought summary:")
            if step.summary:
                for content_block in step.summary:
                    if content_block.type == "text":
                        print(content_block.text)
            print()
        elif step.type == "model_output":
            for content_block in step.content:
                if content_block.type == "text":
                    print("Answer:")
                    print(content_block.text)
                    print()

    return sql_query
