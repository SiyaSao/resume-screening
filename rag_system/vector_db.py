from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import uuid
# 1. EMBEDDING MODEL

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
# 2. CHROMA VECTOR DATABASE
vector_store = Chroma(
    collection_name="recruitment_documents",
    persist_directory="./chroma_db",
    embedding_function=embeddings
)
# 3. ADD DOCUMENTS
def add_documents(
    documents=None,
    texts=None,
    document_ids=None,
    ids=None,
    metadatas=None
):
    # Accept texts also

    if texts is not None:
        documents = texts
    # Check documents
    
    if not documents:
        return "No documents found"

    # Clean documents
    clean_texts = []
    for document in documents:
        if hasattr(document, "page_content"):
            text = document.page_content
        elif isinstance(document, str):
            text = document
        else:
            text = str(document)
        if text.strip():
            clean_texts.append(
                text.strip()
            )
    # Check cleaned text
    
    if not clean_texts:
        return "No text found"
    # Create IDs if not provided

    final_ids = None
    if document_ids:
        final_ids = document_ids
    elif ids:
        final_ids = ids
    else:
        final_ids = [
            str(uuid.uuid4())
            for _ in clean_texts
        ]
    # Check metadata
    
    final_metadatas = metadatas
    if final_metadatas:
        if len(final_metadatas) != len(clean_texts):
            raise ValueError(
                "Number of metadatas must match number of documents"
            )
    # Add documents to ChromaDB
    
    vector_store.add_texts(
        texts=clean_texts,
        ids=final_ids,
        metadatas=final_metadatas
    )
    return (
       f"{len(clean_texts)} documents added successfully"
    )
# 4. SEARCH DOCUMENTS

def search_documents(
    query,
    k=3,
    filter_metadata=None
):
    if not query:
        return []
    # Normal search
    
    if filter_metadata:
        results = vector_store.similarity_search(
            query,
            k=k,
            filter=filter_metadata
        )
    else:
        results = vector_store.similarity_search(
            query,
            k=k
        )
    return results
# 5. DELETE DOCUMENTS

def delete_documents(document_ids):
    if not document_ids:
        return "No document IDs provided"
    vector_store.delete(
        ids=document_ids
    )
    return (
        f"{len(document_ids)} documents deleted successfully"
    )