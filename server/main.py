import uuid
import json
import os
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager

from models import Job, CourseRequest, JobStatus
from scraper import AsyncScraper
from config import settings

# === PERSISTENCE ===
JOBS_FILE = "jobs.json"
jobs_db = {}

def load_jobs():
    global jobs_db
    if os.path.exists(JOBS_FILE):
        try:
            with open(JOBS_FILE, "r") as f:
                data = json.load(f)
                # Reconstruct classes from dicts
                for k, v in data.items():
                    jobs_db[k] = Job(**v)
        except Exception:
            jobs_db = {}

def save_jobs():
    with open(JOBS_FILE, "w") as f:
        # Convert objects to dicts for JSON
        dump = {k: v.model_dump() for k, v in jobs_db.items()}
        json.dump(dump, f, indent=2)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    load_jobs()
    yield
    # Shutdown
    save_jobs()

app = FastAPI(lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

scraper = AsyncScraper()

@app.post("/start")
async def start_job(req: CourseRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    new_job = Job(id=job_id)
    jobs_db[job_id] = new_job
    
    save_jobs() # Save initial state
    
    # Run scraping in background
    background_tasks.add_task(run_scraper_task, new_job, req.courses)
    
    return {"job_id": job_id}

async def run_scraper_task(job: Job, courses: list):
    await scraper.process_batch(job, courses)
    save_jobs() # Save final state

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs_db: raise HTTPException(status_code=404)
    return jobs_db[job_id]

@app.get("/download/{filename}")
async def download_file(filename: str):
    path = os.path.join(settings.DOWNLOAD_DIR, filename)
    if os.path.exists(path): return FileResponse(path)
    raise HTTPException(status_code=404)