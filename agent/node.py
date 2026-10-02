from ai_analyzer import (
    analyze_job_description,
    analyze_resume
)
from matcher import match_candidate_with_job
from rag_system.document_processor import split_document
from rag_system.vector_db import add_documents
from rag_system.retriever import retrieve_relevant_documents
import uuid

# 1. ANALYZE JOB DESCRIPTION
def analyze_job_node(state):
    job_description = state["job_description"]
    job_data = analyze_job_description(
        job_description
    )
    return {
        "job_data": job_data
    }

# 2. ANALYZE RESUME
def analyze_resume_node(state):
    resume_text = state["resume_text"]
    candidate_data = analyze_resume(
        resume_text
    )
    return {
        "candidate_data": candidate_data
    }

# 3. STORE RESUME + RETRIEVE RELEVANT INFORMATION
def retrieve_context_node(state):
    resume_text = state["resume_text"]
    # Get resume ID
    resume_id = state.get(
        "resume_id"
    )
    if not resume_id:
        resume_id = str(
            uuid.uuid4()
        )
   
    # Split resume into chunks
    chunks = split_document(
        resume_text
    )
 
    # Create unique IDs for chunks
    document_ids = []
    for index in range(len(chunks)):
        document_ids.append(
            f"{resume_id}_chunk_{index}"
        )
   
    # Create metadata
    metadatas = []
    for index in range(len(chunks)):
        metadatas.append(
            {
                "resume_id": str(resume_id)
            }
        )
    # Store chunks in ChromaDB
    if chunks:
        add_documents(
            texts=chunks,
            document_ids=document_ids,
            metadatas=metadatas
        )
    # Create retrieval query
    job_description = state.get(
        "job_description",
        ""
    )

    query = f"""
    Find information from this candidate resume
    that is relevant to the following job requirements:

    {job_description}

    Focus on:
    skills,
    experience,
    education,
    projects,
    certifications,
    technologies
    """


    # Retrieve relevant resume chunks
    retrieved_context = retrieve_relevant_documents(
        query=query,
        k=5,
        resume_id=str(resume_id)
    )
    # Return retrieved context
    return {
        "retrieved_context": retrieved_context,
        "resume_id": str(resume_id)
    }

# 4. MATCH CANDIDATE WITH JOB
def match_candidate_node(state):
    job_data = state["job_data"]
    candidate_data = state["candidate_data"]
    retrieved_context = state.get(
        "retrieved_context",
        []
    )

    # Send retrieved RAG information to matcher
    screening_result = match_candidate_with_job(
        job_data,
        candidate_data,
        retrieved_context
    )
    return {
        "screening_result": screening_result,

        "explanation": screening_result.get(
            "explanation",
            ""
        )
    }