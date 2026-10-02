from typing import TypedDict, List, Dict, Any

class RecruitmentState(TypedDict, total=False):  
    # JOB INFORMATION
    job_description: str
    job_data: Dict[str, Any]
    # RESUME INFORMATION
    resume_text: str
    resume_id: str
    candidate_data: Dict[str, Any]
    # RAG INFORMATION
    retrieved_context: List[str]
    # SCREENING INFORMATION
    screening_result: Dict[str, Any]
    explanation: str