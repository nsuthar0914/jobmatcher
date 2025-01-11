from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
from typing import List, Optional
import os
import shutil
from datetime import datetime
from uuid import uuid4
import services

app = FastAPI(title="Job Matching System API")

class JobSeekerInput(BaseModel):
    email: str
    linkedin_url: Optional[str]
    github_url: Optional[str]

class JobOpeningInput(BaseModel):
    creator_email: str
    job_title: str
    company_name: str
    job_description: str
    company_values: str
    team_structure: str
    growth_opportunities: str

# File storage configuration
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize services
job_matching_service = services.JobMatchingService()

@app.post("/job-seeker/upload")
async def upload_job_seeker_documents(
    job_seeker: JobSeekerInput,
    resume: UploadFile = File(...),
    cover_letter: Optional[UploadFile] = File(None),
    certificates: List[UploadFile] = File([])
):
    try:
        # Generate unique ID for job seeker
        seeker_id = str(uuid4())
        seeker_dir = os.path.join(UPLOAD_DIR, "seekers", seeker_id)
        os.makedirs(seeker_dir, exist_ok=True)

        # Save files
        files_info = {}
        
        # Save resume
        resume_path = os.path.join(seeker_dir, "resume.pdf")
        with open(resume_path, "wb") as f:
            shutil.copyfileobj(resume.file, f)
        files_info["resume_path"] = resume_path

        # Save cover letter if provided
        if cover_letter:
            cover_letter_path = os.path.join(seeker_dir, "cover_letter.pdf")
            with open(cover_letter_path, "wb") as f:
                shutil.copyfileobj(cover_letter.file, f)
            files_info["cover_letter_path"] = cover_letter_path

        # Save certificates if provided
        cert_paths = []
        for i, cert in enumerate(certificates):
            cert_path = os.path.join(seeker_dir, f"certificate_{i}.pdf")
            with open(cert_path, "wb") as f:
                shutil.copyfileobj(cert.file, f)
            cert_paths.append(cert_path)
        files_info["certificate_paths"] = cert_paths

        # Process documents and create vectors
        profile_info = {
            "id": seeker_id,
            "email": job_seeker.email,
            "linkedin_url": job_seeker.linkedin_url,
            "github_url": job_seeker.github_url,
            **files_info
        }
        
        job_matching_service.process_job_seeker(profile_info)
        
        return {"seeker_id": seeker_id, "message": "Profile processed successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/job-opening/create")
async def create_job_opening(job_opening: JobOpeningInput):
    try:
        # Generate unique ID for job opening
        job_id = str(uuid4())
        
        # Process job opening information
        job_info = {
            "id": job_id,
            **job_opening.dict()
        }
        
        job_matching_service.process_job_opening(job_info)
        
        return {"job_id": job_id, "message": "Job opening processed successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/matches/{entity_id}")
async def get_matches(entity_id: str, entity_type: str):
    try:
        # Generate matches and visualizations
        matches = job_matching_service.get_matches(entity_id, entity_type)
        
        return {
            "matches": matches,
            "visualization_url": f"/visualization/{entity_id}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/visualization/{entity_id}")
async def get_visualization(entity_id: str):
    try:
        viz_path = job_matching_service.get_visualization(entity_id)
        return FileResponse(viz_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))