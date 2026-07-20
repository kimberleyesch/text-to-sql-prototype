import chromadb
from google import genai
from pathlib import Path
from src.database_access import get_schema, execute_query
from src.prompt_builder import build_baseline_prompt, build_rag_prompt
from src.llm_client import generate_sql, get_api
from evaluation.evaluation_data import get_questions, save_result, get_results_dir, get_question_path
from evaluation.evaluation_data import RESULTS_DIR
from rag.rag_pipeline import save_embeddings_in_db, create_embedding, retrieve_relevant_documents, build_rag_context

CHROMADB_PATH = Path(__file__).resolve().parent / "rag" / "chromaDB"

USE_RAG = True
REBUILD_RAG_COLLECTION = False

USE_EXTENDED_QUESTIONS = True

def main():
    """Run complete Text-to-SQL workflow

    Read database schema and test questions, send prompt to LLM, receive SQL-queries,
    execute queries in SQL and save results.
    """

    gemini_api_key = get_api()
    client = genai.Client(api_key=gemini_api_key)

    schema = get_schema()
    results_dir = get_results_dir(USE_RAG, USE_EXTENDED_QUESTIONS)
    question_path = get_question_path(USE_EXTENDED_QUESTIONS)
    questions, question_ids = get_questions(question_path)

    if USE_RAG:
        if REBUILD_RAG_COLLECTION:
            embedded_documents = create_embedding(client)
            collection = save_embeddings_in_db(embedded_documents)

        else:
            chroma_client = chromadb.PersistentClient(path=str(CHROMADB_PATH))
            collection = chroma_client.get_collection(name="rag-documents")

    for question_id, question in zip(question_ids, questions):

        if USE_RAG:
            rag_results  = retrieve_relevant_documents(question, collection, client)
            rag_context = build_rag_context(rag_results)
            prompt = build_rag_prompt(question, schema, rag_context)
            question_id += "_RAG"
        else:
            prompt = build_baseline_prompt(question, schema)

        sql_query = generate_sql(client, prompt)
        column_names, results = execute_query(sql_query)
        save_result(question_id, column_names, results, sql_query, results_dir)
    
    print("\nTest run completed successfully.")
    print(f"Results have been saved in {RESULTS_DIR}")

if __name__ == "__main__":
    main()