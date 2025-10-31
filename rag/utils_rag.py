import os
import json
from llama_index.core import (
    VectorStoreIndex,
    Settings,
    StorageContext,
    load_index_from_storage,
    Document,
)

def create_index(persist_dir, jsonl_path):
    print(f"Creating a new index from file: {jsonl_path}")

    if os.path.exists(persist_dir):
        delete_index(persist_dir)

    if not os.path.exists(jsonl_path):
        raise FileNotFoundError(f"File not found: {jsonl_path}")

    documents = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            item = json.loads(line)
            # Build a Document with text content and metadata
            doc = Document(
                text=f"Title: {item.get('title', '')}\n"
                    f"URL: {item.get('url', '')}\n"
                    f"Timestamp: {item.get('timestamp', '')}\n\n"
                    f"{item.get('content', '')}",
                metadata={
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "timestamp": item.get("timestamp"),
                    "description": item.get("description"),
                },
            )
            documents.append(doc)

    # Create the index from documents
    index = VectorStoreIndex.from_documents(
        documents,
        embed_model=Settings.embed_model,
    )

    # Persist the index to disk
    index.storage_context.persist(persist_dir=persist_dir)

    print("Index created and saved to:", persist_dir)
    print(f"Total documents indexed: {len(documents)}")
    return index


def get_index(output_dir: str, jsonl_path: str = "../items.jsonl") -> VectorStoreIndex:
    """Loads an existing index from disk or creates a new one from items.jsonl."""
    persist_dir = os.path.join(output_dir, "rag_index")

    # Load existing index if available
    if os.path.exists(persist_dir):
        print("Loading existing index from:", persist_dir)
        storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
        index = load_index_from_storage(
            storage_context,
            embed_model=Settings.embed_model,  # important for consistency
        )
        return index    
    else:
        return create_index(persist_dir, jsonl_path)


def delete_index(output_dir: str):
    persist_dir = os.path.join(output_dir, "rag_index")
    if os.path.exists(persist_dir):
        import shutil
        shutil.rmtree(persist_dir)
        print("Deleted index directory:", persist_dir)
    else:
        print("Index directory does not exist:", persist_dir)