import chromadb
from google import genai
from pathlib import Path
from src.database_access import get_schema, execute_query
from src.prompt_builder import build_baseline_prompt, build_rag_prompt
from src.llm_client import generate_sql, get_api
from evaluation.evaluation_data import get_questions, save_result, save_executability_results, get_results_dir, get_question_path
from rag.rag_pipeline import save_embeddings_in_db, create_embedding, retrieve_relevant_documents, build_rag_context

CHROMADB_PATH = Path(__file__).resolve().parent / "rag" / "chromaDB"

# Configurations:
USE_RAG = False
REBUILD_RAG_COLLECTION = False
USE_EXTENDED_QUESTIONS = False

def main():
    """Run complete Text-to-SQL workflow

    Read database schema and test questions, send prompt to LLM, receive SQL-queries,
    execute queries in SQL and save results.
    """

    gemini_api_key = get_api()
    client = genai.Client(api_key=gemini_api_key)

    executability_ids = []
    executability_results = []
    error_messages = []

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

            print("\nRAG context: ")
            print(rag_context)
            print("\n\n")
        else:
            prompt = build_baseline_prompt(question, schema)

        sql_query = generate_sql(client, prompt)
        executability_ids.append(question_id)
        
        try:
            column_names, results = execute_query(sql_query)
            executability_results.append(True)
            error_messages.append(None)
        except RuntimeError as e:
            column_names = []
            results = []
            executability_results.append(False)
            error_messages.append(str(e))

        if USE_RAG:
            save_result(question_id, column_names, results, sql_query, results_dir, rag_results)
        else:
            save_result(question_id, column_names, results, sql_query, results_dir)


        print("\n")
        print("-"*60)
        print(f"Question {question_id}: {question}\n")
        print(f"Generated SQL-Query: {sql_query}")
        print("\n")
        print("Result:")
        print(" | ".join(column_names))
        print("-"*40)

        for row in results:
            print(" | ".join(map(str, row))) 
    
    save_executability_results(executability_ids, executability_results, error_messages, results_dir)
    print("\nTest run completed successfully.")
    print(f"Results have been saved in {results_dir}")

if __name__ == "__main__":
    main()