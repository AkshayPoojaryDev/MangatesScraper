import os
import uuid
import time
import urllib.parse
import re
import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Enable CORS for React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === STORAGE & CONFIG ===
DOWNLOAD_DIR = "downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# In-memory storage for job status
jobs = {}

# === DATA MODELS ===
class CourseRequest(BaseModel):
    courses: List[str]

# === SCRAPER LOGIC ===
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Manual Map acts as a "Cache" for known tricky ones
MANUAL_URL_MAP = {
    "Financial Modelling In Excel mangates": "https://mangates.com/financial-modeling-using-excel/",
}

def clean_course_name(raw_name):
    # Removes 'mangates' and special characters to make a clean search query
    clean = raw_name.lower().replace(" mangates", "").replace("mangates", "")
    clean = clean.replace("&", "").replace("(", "").replace(")", "")
    return clean.strip()

def get_real_pdf_url(raw_url):
    """Extracts direct PDF link from Google Viewers/Drive links."""
    if "/document/d/" in raw_url:
        base = raw_url.split('/edit')[0]
        return f"{base}/export?format=pdf"
    if "docs.google.com/viewer" in raw_url:
        parsed = urllib.parse.urlparse(raw_url)
        params = urllib.parse.parse_qs(parsed.query)
        if 'url' in params: return params['url'][0]
    return raw_url

def search_on_site(course_name):
    """
    1. Searches mangates.com/?s=name
    2. Returns the URL of the first search result
    """
    try:
        query = urllib.parse.quote(course_name)
        search_url = f"https://mangates.com/?s={query}"
        
        res = requests.get(search_url, headers=HEADERS, timeout=10)
        if res.status_code != 200: return None
        
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Mangates search results are usually in <h3 class="entry-title"><a href="...">
        # We look for the first link inside an entry-title
        for title_tag in soup.find_all(class_="entry-title"):
            link = title_tag.find('a')
            if link and 'href' in link.attrs:
                return link['href']
                
    except Exception as e:
        print(f"Search Error: {e}")
        return None
    
    return None

def download_pdf(url, basename, job_id):
    """Visits a page, finds the PDF/Brochure link, and downloads it."""
    try:
        # print(f"Checking URL: {url}") # Debugging
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code != 200: return False
        
        soup = BeautifulSoup(res.text, 'html.parser')
        target = None
        
        # Look for PDF links or "Factsheet" buttons
        for link in soup.find_all('a', href=True):
            h, t = link['href'], link.text.lower()
            
            # Priority 1: Direct PDF file
            if h.lower().endswith('.pdf') or "/document/d/" in h: 
                target = h
            
            # Priority 2: Text Match
            if any(x in t for x in ["factsheet", "brochure", "download outline"]): 
                target = h
                break # Stop if we find a text match
        
        if target:
            if not target.startswith('http'): 
                target = urllib.parse.urljoin(url, target)
            
            final_url = get_real_pdf_url(target)
            
            # Download Logic
            pdf_data = requests.get(final_url, headers=HEADERS)
            
            # Create a safe filename
            safe_name = "".join([c for c in basename if c.isalnum() or c==' ']).strip() + ".pdf"
            path = os.path.join(DOWNLOAD_DIR, safe_name)
            
            with open(path, 'wb') as f: 
                f.write(pdf_data.content)
            
            # Log Success
            jobs[job_id]['logs'].append(f"SUCCESS: Found at {url}")
            jobs[job_id]['success'].append(safe_name)
            return True
            
    except Exception as e:
        # jobs[job_id]['logs'].append(f"Error on {url}: {e}")
        pass
        
    return False

def process_batch(job_id: str, course_list: List[str]):
    jobs[job_id]['status'] = 'running'
    total = len(course_list)
    
    for idx, course in enumerate(course_list):
        clean_name = clean_course_name(course)
        jobs[job_id]['logs'].append(f"Processing ({idx+1}/{total}): {clean_name}")
        
        found = False
        
        # PHASE 1: Check Manual Map (Fastest)
        if course in MANUAL_URL_MAP:
            if download_pdf(MANUAL_URL_MAP[course], clean_name, job_id): 
                found = True

        # PHASE 2: Dynamic Search (Smartest)
        if not found:
            jobs[job_id]['logs'].append(f"  -> Searching website for '{clean_name}'...")
            search_result_url = search_on_site(clean_name)
            
            if search_result_url:
                jobs[job_id]['logs'].append(f"  -> Found page: {search_result_url}")
                if download_pdf(search_result_url, clean_name, job_id):
                    found = True
            else:
                jobs[job_id]['logs'].append(f"  -> No search results found.")

        # PHASE 3: Log Failure
        if not found:
            jobs[job_id]['logs'].append(f"FAILED: Could not find PDF.")
            jobs[job_id]['failed'].append(course)
            
        jobs[job_id]['progress'] = int(((idx + 1) / total) * 100)
        time.sleep(1) # Be polite to the server
        
    jobs[job_id]['status'] = 'completed'
    jobs[job_id]['logs'].append("Job Finished.")

# === API ENDPOINTS ===

@app.post("/start")
async def start_job(req: CourseRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "pending",
        "progress": 0,
        "logs": [],
        "failed": [],
        "success": []
    }
    background_tasks.add_task(process_batch, job_id, req.courses)
    return {"job_id": job_id}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs: raise HTTPException(status_code=404)
    return jobs[job_id]

@app.get("/download/{filename}")
async def download_file(filename: str):
    path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(path): return FileResponse(path)
    raise HTTPException(status_code=404)