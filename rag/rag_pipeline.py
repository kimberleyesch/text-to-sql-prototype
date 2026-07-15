import sys
import chromadb
from google.genai import types
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

RAG_DOKUS_DIR = Path(__file__).resolve().parent / "documents"
CHROMADB_PATH = Path(__file__).resolve().parent / "chromaDB"
CHROMADB_PATH.mkdir(exist_ok=True)


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

def create_embedding(client):
    """Generates vector embeddings from text files."""

    documents = load_txt_documents(RAG_DOKUS_DIR)
    embedded_documents = []

    for document in documents:
        result = client.models.embed_content(
            model="gemini-embedding-2",
            contents=document["content"],
            config=types.EmbedContentConfig(output_dimensionality=768)
        )

        embedding = result.embeddings[0].values

        embedded_documents.append({
            "source": document["source"],
            "content": document["content"],
            "embedding": embedding
        })

    return embedded_documents

def save_embeddings_in_db(embedded_documents):
    """Saves the document embeddings to ChromaDB."""

    chroma_client = chromadb.PersistentClient(path=str(CHROMADB_PATH))

    collection = chroma_client.get_or_create_collection(
        name="rag-documents",
        metadata={"hnsw:space": "cosine"}
    )

    ids = []
    embeddings = []
    metadatas = []
    documents = []

    for i, doc in enumerate(embedded_documents):
        ids.append(f"id{i}")
        embeddings.append(doc["embedding"])
        metadatas.append({"source": doc["source"]})
        documents.append(doc["content"])

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents
    )

    print(f"Saved documents: {collection.count()}")

    return collection

def retrieve_relevant_documents(user_question, collection, client):
    """Embeds the user question and retrieves the most relevant documents from ChromaDB."""
    result = client.models.embed_content(
        model="gemini-embedding-2",
        contents=user_question,
        config=types.EmbedContentConfig(output_dimensionality=768)
    )

    query_embedding = result.embeddings[0].values
    
    rag_results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )

    return rag_results

def build_rag_context(rag_results):
    """Builds a formatted context string from the retrieved documents."""
    documents = rag_results["documents"][0]
    metadatas = rag_results["metadatas"][0]

    rag_context = []

    for document, metadata in zip(documents, metadatas):
        
        rag_context.append(f"source: {metadata["source"]}")
        rag_context.append(document)

        rag_context.append("\n\n---\n\n")

    return rag_context
