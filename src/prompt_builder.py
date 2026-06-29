def build_prompt(question, schema):
    """Construct a prompt for generating a SQLite query."""
    
    prompt = f"""
You are a text-to-SQL system.
Generate one valid SQLite SELECT query that answers the user's question.

Database schema:
{schema}

User question:
{question}

Instructions:
- Return only the SQL query.
- Do not include explanations.
- Generate only SELECT queries.
- Select only the columns required to answer the question.
- Prefer human-readable descriptive column for identifying entities. 
- Include ID columns only when explicitly requested or necessary.
- Use SELECT * only when  user explicitly requests all information, all details or complete records.
"""

    return prompt