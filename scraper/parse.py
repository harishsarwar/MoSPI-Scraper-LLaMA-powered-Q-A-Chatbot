
import os, json, argparse, httpx, hashlib
from bs4 import BeautifulSoup
from scraper.utils import sha256_bytes, write_json, structured_log, read_json
import pdfplumber
import camelot
from urllib.parse import urljoin
from datetime import datetime

RAW_PDF_DIR = os.getenv("RAW_PDF_DIR","./data/raw/pdf")
DB_DIR = os.getenv("PROCESSED_DIR","./data/processed")
os.makedirs(RAW_PDF_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

def fetch_url(url):
    headers = {"User-Agent": os.getenv("USER_AGENT","MoSPI-Scraper/1.0")}
    r = httpx.get(url, headers=headers, timeout=60)
    r.raise_for_status()
    return r

def parse_detail(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    title_el = soup.find("h1") or soup.find("title")
    title = title_el.get_text(strip=True) if title_el else ""
    date_el = soup.find("time") or soup.find(class_="date")
    date = date_el.get_text(strip=True) if date_el else None
    summary_el = soup.select_one(".summary, .lead, .field--name-body, .content")
    summary = summary_el.get_text(strip=True) if summary_el else None
    file_links = []
    for a in soup.find_all("a", href=True):
        href = a['href']
        if href.lower().endswith(".pdf"):
            file_links.append(urljoin(base_url, href))
    return {"title": title, "date": date, "summary": summary, "file_links": file_links}

def download_pdf(url):
    r = fetch_url(url)
    content = r.content
    h = sha256_bytes(content)
    fname = f"{h}.pdf"
    out_path = os.path.join(RAW_PDF_DIR, fname)
    if not os.path.exists(out_path):
        with open(out_path, "wb") as f:
            f.write(content)
    return out_path, h

def extract_pdf_text_and_table(pdf_path):
    text = ""
    tables = []
    with pdfplumber.open(pdf_path) as pdf:
        for p in pdf.pages:
            text += (p.extract_text() or "") + "\n"
    try:
        tables_found = camelot.read_pdf(pdf_path, pages='1-end')
        for t in tables_found:
            tables.append({"n_rows": t.shape[0], "n_cols": t.shape[1], "csv": t.df.to_csv(index=False)})
    except Exception as e:
        structured_log("camelot_failed", error=str(e), path=pdf_path)
    return text, tables

def parse_run():
    discovered_file = os.path.join(DB_DIR,"discovered.json")
    if not os.path.exists(discovered_file):
        structured_log("discovered_missing", path=discovered_file)
        return
    discovered = read_json(discovered_file) or []
    docs = []
    for it in discovered:
        try:
            r = fetch_url(it['url'])
            meta = parse_detail(r.text, it['url'])
            doc_id = hashlib.sha256(it['url'].encode('utf-8')).hexdigest()
            files = []
            for f in meta['file_links']:
                path, file_hash = download_pdf(f)
                text, tables = extract_pdf_text_and_table(path)
                files.append({"file_url": f, "file_path": path, "file_hash": file_hash, "text": text, "text_len": len(text), "tables": tables})
            doc_record = {
                "id": doc_id,
                "title": meta['title'],
                "date_published": meta['date'],
                "url": it['url'],
                "category": None,
                "summary": meta['summary'],
                "file_links": meta['file_links'],
                "files": files,
                "created_at": datetime.utcnow().isoformat()
            }
            docs.append(doc_record)
        except Exception as e:
            structured_log("parse_failed", url=it.get('url'), error=str(e))
    write_json(os.path.join(DB_DIR,"documents.json"), docs)
    structured_log("parse_complete", count=len(docs))

if __name__ == "__main__":
    parse_run()
