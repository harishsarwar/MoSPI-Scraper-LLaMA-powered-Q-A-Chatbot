
import argparse, time, os, json, hashlib
import httpx
from bs4 import BeautifulSoup
from scraper.utils import sha256_bytes, write_json, structured_log, read_json
from urllib.parse import urljoin
from datetime import datetime

USER_AGENT = os.getenv("USER_AGENT","MoSPI-Scraper/1.0 (+https://example)")
RATE_LIMIT_SECONDS = float(os.getenv("RATE_LIMIT_SECONDS", "1"))
DB_DIR = os.getenv("PROCESSED_DIR","./data/processed")
FINGERPRINT_FILE = os.path.join(DB_DIR, "fingerprints.json")
os.makedirs(DB_DIR, exist_ok=True)

def load_fingerprints():
    return read_json(FINGERPRINT_FILE) or {}

def save_fingerprints(fp):
    write_json(FINGERPRINT_FILE, fp)

def fetch(url):
    headers = {"User-Agent": USER_AGENT}
    r = httpx.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    return r

def parse_listing(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    items = []
    for li in soup.select("article, .views-row, .node, .listing, li"):
        a = li.find("a", href=True)
        if not a:
            continue
        title = a.get_text(strip=True)
        href = urljoin(base_url, a['href'])
        date_el = li.find("time") or li.find(class_="date")
        date_text = date_el.get_text(strip=True) if date_el else None
        items.append({"title": title, "url": href, "date": date_text})
    return items

def crawl(seed_urls, max_pages=5):
    fp = load_fingerprints()
    discovered = []
    for seed in seed_urls:
        url = seed
        pages = 0
        while url and pages < max_pages:
            structured_log("fetching_listing", url=url, page=pages)
            try:
                r = fetch(url)
            except Exception as e:
                structured_log("fetch_failed", url=url, error=str(e))
                break
            items = parse_listing(r.text, base_url=url)
            for it in items:
                h = hashlib.sha256((it["url"]+it["title"]).encode('utf-8')).hexdigest()
                if h in fp:
                    continue
                discovered.append(it)
                fp[h] = {"url": it["url"], "title": it["title"], "fetched_at": datetime.utcnow().isoformat()}
            soup = BeautifulSoup(r.text, "html.parser")
            next_el = soup.find("a", string=lambda s: s and 'next' in s.lower())
            url = urljoin(seed, next_el['href']) if next_el and next_el.get('href') else None
            pages += 1
            time.sleep(RATE_LIMIT_SECONDS)
    save_fingerprints(fp)
    write_json(os.path.join(DB_DIR,"discovered.json"), discovered)
    structured_log("crawl_complete", count=len(discovered))
    return discovered

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed-url", required=True)
    parser.add_argument("--max-pages", type=int, default=5)
    args = parser.parse_args()
    seed_list = [u.strip() for u in args.seed_url.split(",")]
    crawl(seed_list, max_pages=args.max_pages)
