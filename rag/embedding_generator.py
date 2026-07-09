import sys
from google import genai
from google.genai import types
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from llm_client import get_api

RAG_DOKUS_DIR = Path(__file__).resolve().parent / "documents"

def load_txt_documents(folder_path):
    """Load all text files from the documents path."""

    documents = []

    for file in sorted(folder_path.glob("*.txt")):
        with open(file, "r", encoding="utf-8") as f:
            content = f.read().strip()

            documents.append({
                "source": file.name,
                "content": content
            })

    return documents

def create_embedding():
    GEMINI_API_KEY = get_api()
    client = genai.Client(api_key=GEMINI_API_KEY)

    documents = load_txt_documents(RAG_DOKUS_DIR)
    embedded_documents = []

    for document in documents:
        result = client.models.embed_content(
            model="gemini-embedding-2",
            contents=document["content"],
            config=types.EmbedContentConfig(output_dimensionality=768)
        )

        embedding = result.embeddings[0].values

        embedded_documents.append([{
            "source": document["source"],
            "content": document["content"],
            "embedding": embedding
        }])
