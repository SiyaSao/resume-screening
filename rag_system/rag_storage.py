from .document_processor import split_document
from .vector_db import add_documents
import uuid
# STORE RESUME IN VECTOR DATABASE
def store_resume_in_rag(
    resume_text,
    resume_id,
    filename=None
):
    # Check resume text
    if not resume_text:
        return {
            "success": False,
            "message": "Resume text is empty"
        }
    # Split resume into chunks
    chunks = split_document(
        resume_text
    )
    if not chunks:
        return {
            "success": False,
            "message": "No chunks created"
        }
    # Create unique IDs
    document_ids = []
    for _ in chunks:
        document_ids.append(
            str(uuid.uuid4())
        )
    # Create metadata
    metadatas = []
    for _ in chunks:
        metadata = {
            "resume_id": str(resume_id)
        }
        if filename:
            metadata["filename"] = filename
        metadatas.append(
            metadata
        )
    # Store in ChromaDB
    result = add_documents(
        documents=chunks,
        document_ids=document_ids,
        metadatas=metadatas
    )
    return {
        "success": True,
        "message": result,
        "resume_id": str(resume_id),
        "chunks_stored": len(chunks)
    }