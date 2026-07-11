
import chromadb

from sentence_transformers import SentenceTransformer


from pathlib import Path


embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


# -----------------------------
# ChromaDB Path
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_PATH = BASE_DIR / "chroma_db"

CHROMA_PATH.mkdir(exist_ok=True)

# -----------------------------
# Chroma Client
# -----------------------------
client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

# -----------------------------
# Collection
# -----------------------------
collection = client.get_or_create_collection(
    name="aktu_notes"
)

# -----------------------------
# Add Document
# -----------------------------
def add_document(doc_id, text, metadata):

    embedding = embedding_model.encode(text).tolist()

    collection.add(
        ids=[doc_id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata]
    )

# -----------------------------
# Search Documents
# -----------------------------
def search_document(query, subject):

    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=10,
        where={
            "subject": subject
        }
    )

    return results

# -----------------------------
# Context Only
# -----------------------------
def get_context(query, subject):

    try:

        results = search_document(query, subject)

        documents = results["documents"][0]

        if not documents:
            return "No relevant documents found."

        return "\n\n".join(documents)

    except Exception as e:

        print("GET_CONTEXT ERROR:", e)

        return "No relevant context found."

# -----------------------------
# Context + Sources
# -----------------------------
def get_context_and_sources(query, subject):

    try:

        results = search_document(query, subject)

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]

        if not documents:
            return (
                "No relevant documents found.",
                []
            )

        context = "\n\n".join(documents)

        sources = list(
            set(
                metadata["filename"]
                for metadata in metadatas
                if metadata and "filename" in metadata
            )
        )

        return context, sources

    except Exception as e:

        print("GET_CONTEXT_AND_SOURCES ERROR:", e)

        return (
            "No relevant context found.",
            []
        )

# -----------------------------
# Count Documents
# -----------------------------
def count_documents():

    return collection.count()

# -----------------------------
# Debug Helper
# -----------------------------
def peek_documents(limit=5):

    results = collection.get(
        include=[
            "documents",
            "metadatas"
        ]
    )

    return {
        "total_docs": len(results["ids"]),
        "sample_metadata": results["metadatas"][:limit]
    }