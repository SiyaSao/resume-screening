from .vector_db import search_documents
# RETRIEVE RELEVANT DOCUMENTS
def retrieve_relevant_documents(
    query,
    k=3,
    resume_id=None
):
   
    # Check query
    if not query:
        return []
    # Create metadata filter
    filter_metadata = None
    if resume_id:
        filter_metadata = {
            "resume_id": resume_id
        }

    # Search ChromaDB
    documents = search_documents(
        query=query,
        k=k,
        filter_metadata=filter_metadata
    )
    # Convert documents to text
    results = []
    for document in documents:
        if hasattr(document, "page_content"):
            results.append(
                document.page_content
            )
        else:
            results.append(
                str(document)
            )
    return results