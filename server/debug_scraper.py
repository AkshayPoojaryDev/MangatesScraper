import asyncio
import aiohttp
import urllib.parse
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

async def fetch(session, url):
    print(f"Fetching {url}...")
    try:
        async with session.get(url, headers=HEADERS, timeout=15) as response:
            print(f"Status: {response.status}")
            if response.status != 200:
                print("Failed to fetch page")
                return None
            return await response.text()
    except Exception as e:
        print(f"Exception: {e}")
        return None

async def debug_search(course_name):
    async with aiohttp.ClientSession() as session:
        query = urllib.parse.quote(course_name)
        search_url = f"https://mangates.com/?s={query}"
        
        html = await fetch(session, search_url)
        if not html: return
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Debug: Print all links found in titles
        print("\n--- Search Results ---")
        found_link = None
        
        # Updated selector
        blogposts = soup.find_all("div", class_="blogpost")
        print(f"Found {len(blogposts)} blogpost items.")
        
        for post in blogposts:
            h3 = post.find('h3')
            if h3:
                link = h3.find('a')
                if link and 'href' in link.attrs:
                    print(f"Found Course Link: {link['href']}")
                    if not found_link: found_link = link['href']
        
        if found_link:
            print(f"\nScanning content of: {found_link}")
            page_html = await fetch(session, found_link)
            if page_html:
                page_soup = BeautifulSoup(page_html, 'html.parser')
                print("\n--- PDF Links ---")
                count = 0
                for link in page_soup.find_all('a', href=True):
                    h = link['href']
                    t = link.text.lower()
                    
                    if h.lower().endswith('.pdf') or "/document/d/" in h or any(x in t for x in ["factsheet", "brochure", "download outline"]):
                         print(f"Candidate: {h} (Text: {t})")
                         count += 1
                if count == 0:
                    print("No PDF candidates found on page.")
        else:
             print("No search results found.")

if __name__ == "__main__":
    asyncio.run(debug_search("Agile"))
