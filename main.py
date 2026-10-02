from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from rag_system.rag_storage import store_resume_in_rag
from rag_system.retriever import retrieve_relevant_documents

from typing import List
import os
import shutil
import html
import uuid

from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, Job, Candidate, Screening

from resume_parser import extract_text_from_pdf
from agent.graph import recruitment_graph
# DATABASE
Base.metadata.create_all(bind=engine)

# FASTAPI APP
app = FastAPI(
    title="AI Recruitment System"
)

# FRONTEND
app.mount(
    "/static",
    StaticFiles(directory="../frontend"),
    name="static"
)
# UPLOAD FOLDER
UPLOAD_FOLDER = "uploads"
os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)
# HOME PAGE
@app.get(
    "/",
    response_class=HTMLResponse
)
def home():

    db: Session = SessionLocal()

    try:
        # GET PREVIOUS CANDIDATES
        candidates = (
            db.query(Candidate)
            .order_by(
                Candidate.id.desc()
            )
            .all()
        )
        # READ EXISTING DASHBOARD
        with open(
            "../frontend/index.html",
            "r",
            encoding="utf-8"
        ) as file:

            html_page = file.read()
        # PREVIOUS CANDIDATES SECTION

        previous_candidates_html = """

        <div style="
            max-width: 900px;
            margin: 40px auto;
            padding: 20px;
            font-family: Arial, sans-serif;
        ">

            <h2 style="
                color: #6657c8;
                text-align: center;
                margin-bottom: 25px;
            ">

                Previous Candidates

            </h2>

        """
        # IF NO CANDIDATES
        if not candidates:
            previous_candidates_html += """
                <div style="
                    background: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 10px;
                    box-shadow: 0 2px 7px #ddd;
                ">
                    No previously screened candidates yet.
                </div>

            """
        # SHOW CANDIDATES
        else:
            for candidate in candidates:
                candidate_name = html.escape(
                    str(
                        candidate.name
                        or "Unknown"
                    )
                )
                resume_name = html.escape(
                    str(
                        candidate.resume_filename
                        or "No resume"
                    )
                )
                previous_candidates_html += f"""
                    <div style="
                        background: white;
                        padding: 20px;
                        margin-bottom: 15px;
                        border-radius: 10px;
                        border-left: 5px solid #6657c8;
                        box-shadow: 0 2px 7px #ddd;
                    ">

                        <div style="
                            font-size: 20px;
                            font-weight: bold;
                            color: #333;
                            margin-bottom: 8px;
                        ">
                            {candidate_name}
                        </div>
                        <div style="
                            color: #666;
                            margin-bottom: 15px;
                        ">
                            Resume: {resume_name}
                        </div>
                        <a
                            href="/candidate/{candidate.id}"
                            style="
                                display: inline-block;
                                padding: 9px 15px;
                                background: #6657c8;
                                color: white;
                                text-decoration: none;
                                border-radius: 5px;
                                margin-right: 8px;
                            "
                        >
                            View Analysis
                        </a>
                        <a
                            href="/resume/{candidate.id}"
                            target="_blank"
                            style="
                                display: inline-block;
                                padding: 9px 15px;
                                background: #555;
                                color: white;
                                text-decoration: none;
                                border-radius: 5px;
                            "
                        >
                            Open Resume PDF
                        </a>
                    </div>
                """
        previous_candidates_html += """
        </div>
        """
 
        # ADD SECTION BEFORE </body>
        html_page = html_page.replace(
            "</body>",
            previous_candidates_html + "</body>"
        )
        return HTMLResponse(
            content=html_page
        )
    finally:
        db.close()

# PREVIOUS CANDIDATES PAGE

@app.get(
    "/candidates",
    response_class=HTMLResponse
)
def previous_candidates():
    db: Session = SessionLocal()
    try:
        candidates = (
            db.query(Candidate)
            .order_by(Candidate.id.desc())
            .all()
        )
        html_page = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Previous Candidates</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #f2f5ff;
                    margin: 0;
                    padding: 30px;
                }
                .container {
                    max-width: 900px;
                    margin: auto;
                }
                h1 {
                    text-align: center;
                    color: #6657c8;
                    margin-bottom: 30px;
                }
                .candidate-card {
                    background: white;
                    padding: 20px;
                    margin-bottom: 18px;
                    border-radius: 10px;
                    border-left: 5px solid #6657c8;
                    box-shadow: 0 2px 7px #ddd;
                }
                .candidate-name {
                    font-size: 21px;
                    font-weight: bold;
                    color: #333;
                }
                .resume-name {
                    color: #666;
                    margin-top: 8px;
                }

                .button {
                    display: inline-block;
                    margin-top: 15px;
                    margin-right: 8px;
                    padding: 9px 15px;
                    background: #6657c8;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }
                .button:hover {
                    background: #5143ad;
                }
                .home-button {
                    display: block;
                    width: 180px;
                    text-align: center;
                    margin: 30px auto;
                    padding: 10px;
                    background: #555;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }
                .empty {
                    background: white;
                    padding: 25px;
                    text-align: center;
                    border-radius: 10px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>
                    Previous Candidates
                </h1>
        """
        if not candidates:
            html_page += """
                <div class="empty">
                    No analyzed candidates found yet.
                </div>
            """
        else:
            for candidate in candidates:
                candidate_name = html.escape(
                    str(candidate.name or "Unknown")
                )
                resume_name = html.escape(
                    str(
                        candidate.resume_filename
                        or "No resume"
                    )
                )
                html_page += f"""
                <div class="candidate-card">
                    <div class="candidate-name">
                        {candidate_name}
                    </div>
                    <div class="resume-name">
                        Resume: {resume_name}
                    </div>
                    <a
                        class="button"
                        href="/candidate/{candidate.id}"
                    >
                        View Analysis
                    </a>
                    <a
                        class="button"
                        href="/resume/{candidate.id}"
                        target="_blank"
                    >
                        Open PDF
                    </a>
                </div>
                """
        html_page += """
                <a
                    class="home-button"
                    href="/"
                >
                    ← Back to Home
                </a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(
            content=html_page
        )
    finally:
        db.close()


# VIEW ONE CANDIDATE'S ANALYSIS
@app.get(
    "/candidate/{candidate_id}",
    response_class=HTMLResponse
)
def view_candidate(candidate_id: int):
    db: Session = SessionLocal()
    try:
        candidate = (
            db.query(Candidate)
            .filter(
                Candidate.id == candidate_id
            )
            .first()
        )
        if not candidate:
            return HTMLResponse(
                content="<h2>Candidate not found.</h2>",
                status_code=404
            )
        screening = (
            db.query(Screening)
            .filter(
                Screening.candidate_id == candidate_id
            )
            .order_by(
                Screening.id.desc()
            )
            .first()
        )
       
        # Candidate information
        name = html.escape(
            str(candidate.name or "Unknown")
        )
        email = html.escape(
            str(candidate.email or "")
        )
        phone = html.escape(
            str(candidate.phone or "")
        )
        experience = html.escape(
            str(candidate.experience or "")
        )
        education = html.escape(
            str(candidate.education or "")
        )
        resume_filename = html.escape(
            str(
                candidate.resume_filename
                or ""
            )
        )
        # Lists
        skills = candidate.skills or []
        projects = candidate.projects or []
        certifications = (
            candidate.certifications or []
        )
        skills_text = html.escape(
            ", ".join(
                str(x) for x in skills
            )
        )
        projects_text = html.escape(
            ", ".join(
                str(x) for x in projects
            )
        )
        certifications_text = html.escape(
            ", ".join(
                str(x) for x in certifications
            )
        )
        
        # Screening information
        match_percentage = 0
        matched_skills_text = ""
        missing_skills_text = ""
        explanation = ""
        if screening:
            match_percentage = (
                screening.match_percentage
                or 0
            )
            matched_skills = (
                screening.matched_skills or []
            )
            missing_skills = (
                screening.missing_skills or []
            )
            matched_skills_text = html.escape(
                ", ".join(
                    str(x)
                    for x in matched_skills
                )
            )
            missing_skills_text = html.escape(
                ", ".join(
                    str(x)
                    for x in missing_skills
                )
            )
            explanation = html.escape(
                str(
                    screening.explanation
                    or ""
                )
            )
       
        # HTML
        html_page = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>
                Candidate Analysis
            </title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #f2f5ff;
                    margin: 0;
                    padding: 30px;
                }}
                .container {{
                    max-width: 850px;
                    margin: auto;
                }}
                h1 {{
                    color: #6657c8;
                    text-align: center;
                    margin-bottom: 25px;
                }}
                .card {{
                    background: white;
                    padding: 22px;
                    margin-bottom: 18px;
                    border-radius: 10px;
                    box-shadow: 0 2px 7px #ddd;
                }}
                .card h2 {{
                    color: #6657c8;
                    margin-top: 0;
                }}
                .name {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #333;
                }}
                .score {{
                    font-size: 28px;
                    font-weight: bold;
                    color: green;
                }}

                .missing {{
                    color: #c0392b;
                }}
                .explanation {{
                    line-height: 1.6;
                    background: #f7f7f7;
                    padding: 15px;
                    border-radius: 6px;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 15px;
                    margin-right: 8px;
                    margin-top: 8px;
                    background: #6657c8;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }}
                .button:hover {{
                    background: #5143ad;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>
                    Candidate Analysis
                </h1>
                <div class="card">
                    <div class="name">
                        {name}
                    </div>
                    <p>
                        <b>Email:</b>
                        {email}
                    </p>
                    <p>
                        <b>Phone:</b>
                        {phone}
                    </p>
                    <p>
                        <b>Resume:</b>
                        {resume_filename}
                    </p>
                </div>
                <div class="card">
                    <h2>
                        Candidate Details
                    </h2>
                    <p>
                        <b>Skills:</b>
                        {skills_text}
                    </p>
                    <p>
                        <b>Experience:</b>
                        {experience}
                    </p>
                    <p>
                        <b>Education:</b>
                        {education}
                    </p>
                    <p>
                        <b>Projects:</b>
                        {projects_text}
                    </p>
                    <p>
                        <b>Certifications:</b>
                        {certifications_text}
                    </p>
                </div>
                <div class="card">
                    <h2>
                        Screening Result
                    </h2>
                    <p class="score">
                        Match:
                        {match_percentage}%
                    </p>
                    <p>
                        <b>Matched Skills:</b>
                        {matched_skills_text}
                    </p>
                    <p class="missing">
                        <b>Missing Skills:</b>
                        {missing_skills_text}
                    </p>
                </div>
                <div class="card">
                    <h2>
                        AI Explanation
                    </h2>
                    <div class="explanation">
                        {explanation}
                    </div>
                </div>
                <a
                    class="button"
                    href="/resume/{candidate.id}"
                    target="_blank"
                >
                    📄 Open Resume PDF
                </a>
                <a
                    class="button"
                    href="/candidates"
                >
                    ← Previous Candidates
                </a>
                <a
                    class="button"
                    href="/"
                >
                    Home
                </a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(
            content=html_page
        )
    finally:
        db.close()
# OPEN SAVED PDF
@app.get(
    "/resume/{candidate_id}"
)
def open_resume(candidate_id: int):
    db: Session = SessionLocal()
    try:
        candidate = (
            db.query(Candidate)
            .filter(
                Candidate.id == candidate_id
            )
            .first()
        )
        if not candidate:
            return HTMLResponse(
                content="<h2>Candidate not found.</h2>",
                status_code=404
            )


        filename = candidate.resume_filename
        if not filename:
            return HTMLResponse(
                content="<h2>Resume file not found.</h2>",
                status_code=404
            )
        file_path = os.path.join(
            UPLOAD_FOLDER,
            filename
        )
        if not os.path.exists(file_path):
            return HTMLResponse(
                content="""
                <h2>
                    Resume PDF is not available
                    in the uploads folder.
                </h2>
                """,
                status_code=404
            )
        return FileResponse(
            path=file_path,
            media_type="application/pdf",
            filename=filename
        )
    finally:
        db.close()

# MULTIPLE RESUME SCREENING WITH RAG
@app.post("/screen-from-dashboard")
async def screen_from_dashboard(
    job_description: str = Form(...),
    files: List[UploadFile] = File(...)
):
    print("\n====================================")
    print("===== SCREENING STARTED =====")
    print("====================================")
    db: Session = SessionLocal()
    results = []
    try:
        # CHECK FILES
        print("Number of files received:", len(files))
        if not files:
            print("No files received.")
            return HTMLResponse(
                content="<h2>Please upload at least one PDF.</h2>",
                status_code=400
            )
        
        # PROCESS EVERY PDF
        for file in files:
            print("\n------------------------------------")
            print("Processing file:", file.filename)
            print("------------------------------------")
            # CHECK PDf
            if not file.filename.lower().endswith(".pdf"):
                print("Skipped - not a PDF")
                continue
            
            # CREATE UNIQUE RAG ID
            resume_id = str(uuid.uuid4())
            print("Generated Resume ID:", resume_id)
            
            # SAVE PDF
            file_path = os.path.join(
                UPLOAD_FOLDER,
                file.filename
            )
            print("Saving PDF to:", file_path)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(
                    file.file,
                    buffer
                )
            print("PDF saved successfully.")
            # EXTRACT RESUME TEXT
            print("Extracting resume text...")
            resume_text = extract_text_from_pdf(
                file_path
            )
            if not resume_text:
                print("No text found in PDF.")
                continue
            print(
                "Resume text extracted successfully."
            )
            print(
                "Text length:",
                len(resume_text)
            )
            # STORE RESUME IN RAG
            print("\n===== RAG STORAGE STARTED =====")
            rag_result = store_resume_in_rag(
                resume_text=resume_text,
                resume_id=resume_id,
                filename=file.filename
            )
            print(
                "RAG storage completed."
            )
            print(
                "RAG result:",
                rag_result
            )
           
            # RETRIEVE RELEVANT INFORMATION
            print("\n===== RAG RETRIEVAL STARTED =====")
            query = """
            candidate skills
            experience
            education
            projects
            certifications
            """
            retrieved_context = (
                retrieve_relevant_documents(
                    query=query,
                    k=3
                )
            )
            print(
                "Retrieved context:"
            )
            print(
                retrieved_context
            )
          
            # RUN AI AGENT WORKFLOW
            print("\n===== AI WORKFLOW STARTED =====")
            workflow_result = (
                recruitment_graph.invoke(
                    {
                        "job_description":
                            job_description,
                        "resume_text":
                            resume_text,
                        "resume_id":
                            resume_id,
                        "retrieved_context":
                            retrieved_context
                    }
                )
            )
            print(
                "AI workflow completed."
            )
          
            # GET RESULTS
            job_data = workflow_result.get(
                "job_data",
                {}
            )
            candidate_data = workflow_result.get(
                "candidate_data",
                {}
            )
            screening_result = workflow_result.get(
                "screening_result",
                {}
            )
            
            # SAVE JOB
            job = Job(
                job_title=job_data.get(
                    "job_title",
                    "Unknown"
                ),
                description=job_description,
                required_skills=job_data.get(
                    "required_skills",
                    []
                ),
                preferred_skills=job_data.get(
                    "preferred_skills",
                    []
                ),
                experience=job_data.get(
                    "experience",
                    ""
                ),
                education=job_data.get(
                    "education",
                    ""
                )
            )
            db.add(job)
            db.commit()
            db.refresh(job)
         
            # SAVE CANDIDATE

            candidate = Candidate(
                name=candidate_data.get(
                    "name",
                    "Unknown"
                ),
                email=candidate_data.get(
                    "email",
                    ""
                ),
                phone=candidate_data.get(
                    "phone",
                    ""
                ),
                skills=candidate_data.get(
                    "skills",
                    []
                ),
                experience=candidate_data.get(
                    "experience",
                    ""
                ),
                education=candidate_data.get(
                    "education",
                    ""
                ),
                projects=candidate_data.get(
                    "projects",
                    []
                ),
                certifications=candidate_data.get(
                    "certifications",
                    []
                ),
                resume_filename=file.filename
            )
            db.add(candidate)
            db.commit()
            db.refresh(candidate)
           
            # SAVE SCREENING
        
            screening = Screening(
                job_id=job.id,
                candidate_id=candidate.id,
                match_percentage=screening_result.get(
                    "match_percentage",
                    0
                ),
                matched_skills=screening_result.get(
                    "matched_skills",
                    []
                ),
                missing_skills=screening_result.get(
                    "missing_skills",
                    []
                ),
                explanation=screening_result.get(
                    "explanation",
                    ""
                )
            )
            db.add(screening)
            db.commit()
            db.refresh(screening)
            
            # ADD RESULT
            results.append({
                "candidate_name":
                    candidate.name,
                "resume_filename":
                    candidate.resume_filename,
                "match_percentage":
                    screening.match_percentage,
                "matched_skills":
                    screening.matched_skills or [],
                "missing_skills":
                    screening.missing_skills or [],
                "explanation":
                    screening.explanation or "",
                "candidate_id":
                    candidate.id
            })
            print(
                "\nCandidate processed successfully:"
            )
            print(
                "Name:",
                candidate.name
            )
            print(
                "Match:",
                screening.match_percentage
            )
     
        # RANK CANDIDATES
        
        results.sort(
            key=lambda x:
                x["match_percentage"],
            reverse=True
        )
     
        # ADD RANK
        for index, candidate in enumerate(
            results,
            start=1
        ):
            candidate["rank"] = index
        print("\n====================================")
        print("===== SCREENING COMPLETED =====")
        print("Candidates processed:", len(results))
      
        # RESULT PAGE
        html_page = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Candidate Ranking</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #f2f5ff;
                    padding: 30px;
                }
                .box {
                    max-width: 900px;
                    margin: auto;
                }
                h1 {
                    text-align: center;
                    color: #6657c8;
                }
                .candidate {
                    background: white;
                    margin: 15px 0;
                    padding: 20px;
                    border-radius: 10px;
                    border-left: 5px solid #6657c8;
                    box-shadow: 0 2px 6px #ddd;
                }
                .rank {
                    font-size: 18px;
                    font-weight: bold;
                    color: #6657c8;
                }
                .name {
                    font-size: 22px;
                    font-weight: bold;
                    margin-top: 8px;
                }
                .score {
                    font-size: 18px;
                    font-weight: bold;
                    color: green;
                    margin-top: 10px;
                }
                .missing {
                    color: #d9534f;
                }
                .explanation {
                    background: #f7f7f7;
                    padding: 12px;
                    margin-top: 12px;
                    border-radius: 6px;
                    line-height: 1.5;
                }
                .button {
                    display: inline-block;
                    margin-top: 15px;
                    margin-right: 8px;
                    padding: 10px 15px;
                    background: #6657c8;
                    color: white;
                    text-decoration: none;
                       border-radius: 5px;
                }
                .button:hover {
                    background: #5143ad;
                }
            </style>
        </head>
        <body>
            <div class="box">
                <h1>
                    Candidate Ranking
                </h1>
        """
        # NO RESULTS
        
        if len(results) == 0:
            html_page += """
                <div class="candidate">
                    No PDF resumes were processed.
                </div>
            """
       
        # SHOW RESULTS
        for candidate in results:
            candidate_name = html.escape(
                str(
                    candidate["candidate_name"]
                    or "Unknown"
                )
            )
            resume_filename = html.escape(
                str(
                    candidate["resume_filename"]
                    or ""
                )
            )
            explanation = html.escape(
                str(
                    candidate["explanation"]
                    or ""
                )
            )
            matched_skills = html.escape(
                ", ".join(
                    str(x)
                    for x in candidate["matched_skills"]
                )
            )
            missing_skills = html.escape(
                ", ".join(
                    str(x)
                    for x in candidate["missing_skills"]
                )
            )
            html_page += f"""
                <div class="candidate">
                    <div class="rank">
                        Rank #{candidate["rank"]}
                    </div>
                    <div class="name">
                        {candidate_name}
                    </div>
                    <p>
                        Resume:
                        {resume_filename}
                    </p>
                    <div class="score">
                        Match:
                        {candidate["match_percentage"]}%
                    </div>
                    <p>
                        <b>Matched Skills:</b>
                        {matched_skills}
                    </p>
                    <p class="missing">
                        <b>Missing Skills:</b>
                        {missing_skills}
                    </p>
                    <div class="explanation">
                        <b>AI Explanation:</b>
                        {explanation}
                    </div>
                    <a
                        class="button"
                        href="/candidate/{candidate["candidate_id"]}"
                    >
                        View Full Analysis
                    </a>
                    <a
                        class="button"
                        href="/resume/{candidate["candidate_id"]}"
                        target="_blank"
                    >
                        Open Resume
                    </a>
                </div>
            """
        html_page += """
                <a
                    class="button"
                    href="/candidates"
                >
                    Previous Candidates
                </a>
                <a
                    class="button"
                    href="/"
                >
                    ← Back to Home
                </a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(
            content=html_page
        )
    except Exception as e:
        db.rollback()
        print("\n===== ERROR =====")
        print(
            "Error:",
            str(e)
        )
        return HTMLResponse(
            content=f"""
            <h2>Error occurred:</h2>
            <p>{html.escape(str(e))}</p>
            """,
            status_code=500
        )
    finally:
        db.close()