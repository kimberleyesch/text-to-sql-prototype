import os
from google import genai
from dotenv import load_dotenv
from pathlib import Path

"""GET API Key from .env"""
PROJ_ROOT = Path(__file__).resolve().parent.parent
dotenv_path = PROJ_ROOT.resolve()
load_dotenv(dotenv_path=dotenv_path)
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

client = genai.Client(api_key=GEMINI_API_KEY)

interaction = client.interactions.create(
    model="gemini-3.5-flash",
    input="How does one select all columns in a SQLite database from a customers table? Reply only with the SQL query"
)
print(interaction.output_text)

# def generate_sql(prompt):T
#     """Send prompt to LLM and return the generated SQL query"""
    
#     sql_query = "SELECT company_name, company_size FROM customers WHERE company_size = 'medium'"
    
#     return sql_query