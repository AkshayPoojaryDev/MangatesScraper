import asyncio
import aiohttp
import urllib.parse
import os
import re
from bs4 import BeautifulSoup
from config import settings
from models import Job
from typing import List

class AsyncScraper:
    def __init__(self):
        self.headers = {'User-Agent': settings.USER_AGENT}
        self.semaphore = asyncio.Semaphore(settings.MAX_CONCURRENCY)

    def clean_course_name(self, raw_name: str) -> str:
        clean = raw_name.lower().replace(" mangates", "").replace("mangates", "")
        clean = clean.replace("&", "").replace("(", "").replace(")", "")
        return clean.strip()

    def get_real_pdf_url(self, raw_url: str) -> str:
        # Handle Google Docs
        if "/document/d/" in raw_url:
            base = raw_url.split('/edit')[0]
            return f"{base}/export?format=pdf"
            
        # Handle Google Drive Files
        if "/file/d/" in raw_url:
            try:
                # https://drive.google.com/file/d/FILE_ID/view...
                file_id = raw_url.split('/d/')[1].split('/')[0]
                return f"https://drive.google.com/uc?export=download&id={file_id}"
            except:
                pass

        # Handle Google Viewer
        if "docs.google.com/viewer" in raw_url:
            parsed = urllib.parse.urlparse(raw_url)
            params = urllib.parse.parse_qs(parsed.query)
            if 'url' in params: return params['url'][0]
            
        return raw_url

    async def fetch(self, session: aiohttp.ClientSession, url: str):
        try:
            async with session.get(url, headers=self.headers, timeout=15) as response:
                if response.status != 200:
                    return None
                return await response.text()
        except Exception:
            return None

    async def search_on_site(self, session: aiohttp.ClientSession, course_name: str) -> str:
        try:
            query = urllib.parse.quote(course_name)
            search_url = f"https://mangates.com/?s={query}"
            html = await self.fetch(session, search_url)
            
            if not html: return None
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # New selector: div.blogpost -> h3 -> a
            for post in soup.find_all("div", class_="blogpost"):
                h3 = post.find('h3')
                if h3:
                    link = h3.find('a')
                    if link and 'href' in link.attrs:
                        return link['href']

            # Fallback: entry-title
            for title_tag in soup.find_all(class_="entry-title"):
                link = title_tag.find('a')
                if link and 'href' in link.attrs:
                    return link['href']
        except Exception as e:
            print(f"Search Error: {e}")
            return None
        return None

    async def download_pdf(self, session: aiohttp.ClientSession, url: str, basename: str, job: Job):
        try:
            html = await self.fetch(session, url)
            if not html: return False
            
            soup = BeautifulSoup(html, 'html.parser')
            target = None
            
            for link in soup.find_all('a', href=True):
                h, t = link['href'], link.text.lower()
                
                if h.lower().endswith('.pdf') or "/document/d/" in h or "/file/d/" in h: 
                    target = h
                
                if any(x in t for x in ["factsheet", "brochure", "download outline"]): 
                    target = h
                    break
            
            if target:
                if not target.startswith('http'): 
                    target = urllib.parse.urljoin(url, target)
                
                final_url = self.get_real_pdf_url(target)
                
                # Download File
                try:
                    async with session.get(final_url, headers=self.headers, timeout=30) as resp:
                        if resp.status == 200:
                            content = await resp.read()
                            safe_name = "".join([c for c in basename if c.isalnum() or c==' ']).strip() + ".pdf"
                            path = os.path.join(settings.DOWNLOAD_DIR, safe_name)
                            
                            with open(path, 'wb') as f: 
                                f.write(content)
                                
                            job.logs.append(f"SUCCESS: Found at {url}")
                            job.success.append(safe_name)
                            return True
                except Exception as e:
                    pass
                    
        except Exception as e:
            pass
        return False

    async def worker(self, session: aiohttp.ClientSession, course: str, job: Job, total: int):
        async with self.semaphore:
            clean_name = self.clean_course_name(course)
            
            # Phase 1: Manual Map
            if course in settings.MANUAL_URL_MAP:
                if await self.download_pdf(session, settings.MANUAL_URL_MAP[course], clean_name, job):
                    return

            # Phase 2: Search
            job.logs.append(f"Searching: {clean_name}")
            search_url = await self.search_on_site(session, clean_name)
            
            found = False
            if search_url:
                if await self.download_pdf(session, search_url, clean_name, job):
                    found = True
            
            if not found:
                 job.logs.append(f"FAILED: {clean_name}")
                 job.failed.append(course)

    async def process_batch(self, job: Job, course_list: List[str]):
        job.status = "running"
        total = len(course_list)
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for idx, course in enumerate(course_list):
                tasks.append(self.worker(session, course, job, total))
            
            # Progress tracker (Approximation)
            completed = 0
            for coro in asyncio.as_completed(tasks):
                await coro
                completed += 1
                job.progress = int((completed / total) * 100)
                
        job.status = "completed"
        job.logs.append("Job Finished.")
