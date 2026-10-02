import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()


llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)


def analyze_job_description(job_description):

    prompt = f"""
You are an AI recruitment assistant.

Analyze the following job description.

Extract:
1. Job title
2. Required skills
3. Preferred skills
4. Required experience
5. Education requirement

Return ONLY valid JSON.

Job Description:
{job_description}

Return exactly this format:

{{
    "job_title": "",
    "required_skills": [],
    "preferred_skills": [],
    "experience": "",
    "education": ""
}}
"""

    response = llm.invoke(prompt)

    result = response.content

    try:
        return json.loads(result)

    except json.JSONDecodeError:

        return {
            "raw_response": result
        }


def analyze_resume(resume_text):

    prompt = f"""
You are an AI recruitment assistant.

Analyze the following candidate resume.

Extract:
1. Candidate name
2. Email
3. Phone
4. Skills
5. Experience
6. Education
7. Projects
8. Certifications

Return ONLY valid JSON.

Resume:
{resume_text}

Return exactly this format:

{{
    "name": "",
    "email": "",
    "phone": "",
    "skills": [],
    "experience": "",
    "education": "",
    "projects": [],
    "certifications": []
}}
"""

    response = llm.invoke(prompt)

    result = response.content

    try:
        return json.loads(result)

    except json.JSONDecodeError:

        return {
            "raw_response": result
        }