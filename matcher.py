from ai_analyzer import llm
def match_candidate_with_job(
    job_data,
    candidate_data,
    retrieved_context=None
):
    if retrieved_context is None:
        retrieved_context = []
    required_skills = job_data.get(
        "required_skills",
        []
    )
    candidate_skills = candidate_data.get(
        "skills",
        []
    )
    required = {
        skill.lower().strip()
        for skill in required_skills
    }
    candidate = {
        skill.lower().strip()
        for skill in candidate_skills
    }
    matched = required.intersection(
        candidate
    )
    missing = required.difference(
        candidate
    )
    if len(required) > 0:
        match_percentage = (
            len(matched) / len(required)
        ) * 100
    else:
        match_percentage = 0
    # RAG context
    context = "\n\n".join(
        retrieved_context
    )
    explanation_prompt = f"""
You are an AI recruitment assistant.
Generate a factual screening explanation.
Job required skills:
{required_skills}
Candidate skills:
{candidate_skills}
Matched skills:
{list(matched)}
Missing skills:
{list(missing)}
Candidate experience:
{candidate_data.get("experience", "")}
Candidate education:
{candidate_data.get("education", "")}
Relevant information retrieved from the resume:
{context}
Explain:
1. Which required skills are present.
2. Which required skills were not found.
3. What experience is available.
4. What education is available.
5. Mention relevant projects or certifications if present.
Use ONLY the information provided.
Do not invent information.
Do not make a final hiring or rejection decision.
Return only the explanation in plain text.
"""
    response = llm.invoke(
        explanation_prompt
    )
    explanation = response.content
    return {
        "candidate_name":
            candidate_data.get(
                "name",
                ""
            ),
        "required_skills":
            required_skills,
        "candidate_skills":
            candidate_skills,
        "matched_skills":
            list(matched),
        "missing_skills":
            list(missing),
        "match_percentage":
            round(
                match_percentage,
                2
            ),
        "experience":
            candidate_data.get(
                "experience",
                ""
            ),
        "education":
            candidate_data.get(
                "education",
                ""
            ),
        "explanation":
            explanation
    }