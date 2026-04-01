# -*- coding: utf-8 -*-

import csv
import re
import time
from pathlib import Path
from urllib.parse import urljoin

import requests

# =========================================================
# Configuración
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "pdfs"
META_DIR = DATA_DIR / "metadata"
LOGS_DIR = DATA_DIR / "logs"

for d in [PDF_DIR, META_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

COLLECTION_UUID = "32ac7c8f-6874-4c3a-83b0-6223934600ca"
MAX_PDFS = 20
PAGE_SIZE = 20

SITE_BASE = "https://cgspace.cgiar.org"
API_BASE = f"{SITE_BASE}/server/api/"
DISCOVER_URL = urljoin(API_BASE, "discover/search/objects")

META_FILE = META_DIR / "collection_pdfs_metadata.csv"
ERROR_LOG = LOGS_DIR / "download_errors.log"

session = requests.Session()
session.headers.update({
    "User-Agent": "cgspace-outcomes-agent/1.0",
    "Accept": "application/json"
})


# =========================================================
# Utilidades
# =========================================================
def safe_filename(name: str) -> str:
    name = (name or "").strip()
    bad_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for ch in bad_chars:
        name = name.replace(ch, "_")
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"_+", "_", name)
    return name[:180].strip("_") or "untitled"


def looks_like_pdf(path: Path) -> bool:
    try:
        with open(path, "rb") as f:
            header = f.read(5)
        return header == b"%PDF-"
    except Exception:
        return False


def get_json(url, params=None):
    r = session.get(url, params=params, timeout=180)
    r.raise_for_status()
    return r.json()


def search_collection_items(collection_uuid, page=0, size=20):
    params = {
        "scope": collection_uuid,
        "dsoType": "item",
        "size": size,
        "page": page
    }
    data = get_json(DISCOVER_URL, params=params)

    objects = []
    try:
        objects = data["_embedded"]["searchResult"]["_embedded"]["objects"]
    except Exception:
        pass

    page_info = data.get("page", {})
    total_elements = page_info.get("totalElements")
    total_pages = page_info.get("totalPages")

    return objects, total_elements, total_pages


def extract_item_uuid(discover_obj):
    try:
        return discover_obj["_embedded"]["indexableObject"]["uuid"]
    except Exception:
        pass

    try:
        return discover_obj["uuid"]
    except Exception:
        pass

    return None


def extract_item_title(discover_obj):
    try:
        return discover_obj["_embedded"]["indexableObject"]["name"]
    except Exception:
        pass
    return None


def get_item_page_html(item_uuid):
    item_url = f"{SITE_BASE}/items/{item_uuid}"
    r = session.get(item_url, timeout=180)
    r.raise_for_status()
    return item_url, r.text


def extract_pdf_links_from_html(html):
    """
    Busca links de bitstream PDF dentro del HTML.
    """
    pattern = r'https://cgspace\.cgiar\.org/server/api/core/bitstreams/[a-f0-9\-]+/content'
    links = re.findall(pattern, html, flags=re.IGNORECASE)

    # También intenta links relativos
    rel_pattern = r'/server/api/core/bitstreams/[a-f0-9\-]+/content'
    rel_links = re.findall(rel_pattern, html, flags=re.IGNORECASE)

    all_links = set(links)
    for rl in rel_links:
        all_links.add(urljoin(SITE_BASE, rl))

    return list(all_links)


def extract_title_from_html(html, fallback=None):
    """
    Intenta extraer un título más limpio desde <title> o meta tags.
    """
    patterns = [
        r'<meta[^>]+property="og:title"[^>]+content="([^"]+)"',
        r'<meta[^>]+name="citation_title"[^>]+content="([^"]+)"',
        r'<title>(.*?)</title>'
    ]

    for p in patterns:
        m = re.search(p, html, flags=re.IGNORECASE | re.DOTALL)
        if m:
            title = m.group(1).strip()
            title = re.sub(r"\s+", " ", title)
            title = title.replace(" - CGSpace", "").strip()
            if title:
                return title

    return fallback or "untitled"


def download_pdf(pdf_url, filename_hint):
    response = session.get(pdf_url, stream=True, timeout=180)
    response.raise_for_status()

    filename = safe_filename(filename_hint)
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"

    out_path = PDF_DIR / filename

    with open(out_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return out_path


# =========================================================
# Main
# =========================================================
def main():
    records = []
    downloaded = 0
    page = 0

    with open(ERROR_LOG, "w", encoding="utf-8") as elog:
        while downloaded < MAX_PDFS:
            objects, total_elements, total_pages = search_collection_items(
                COLLECTION_UUID,
                page=page,
                size=PAGE_SIZE
            )

            if not objects:
                print("No se encontraron más objetos en la colección.")
                break

            print("")
            print("=" * 70)
            print(f"Página API: {page}")
            print(f"Total elementos reportados: {total_elements}")
            print(f"Total páginas reportadas: {total_pages}")
            print("=" * 70)

            for i, obj in enumerate(objects, start=1):
                if downloaded >= MAX_PDFS:
                    break

                try:
                    item_uuid = extract_item_uuid(obj)
                    discover_title = extract_item_title(obj)

                    if not item_uuid:
                        msg = f"PAGE {page} OBJ {i}\tNo se pudo extraer item_uuid\n"
                        elog.write(msg)
                        print(f"[{page}:{i}] ERROR: no se pudo extraer item_uuid")
                        continue

                    item_url, html = get_item_page_html(item_uuid)
                    title = extract_title_from_html(html, fallback=discover_title or item_uuid)

                    pdf_links = extract_pdf_links_from_html(html)

                    print("")
                    print(f"[{downloaded+1}] Item UUID: {item_uuid}")
                    print(f"    Title: {title}")

                    if not pdf_links:
                        print("    No PDF link found in item page.")
                        continue

                    pdf_url = pdf_links[0]
                    pdf_path = download_pdf(pdf_url, title)

                    if not looks_like_pdf(pdf_path):
                        print("    El archivo descargado no parece PDF. Se elimina.")
                        try:
                            pdf_path.unlink()
                        except Exception:
                            pass
                        continue

                    print(f"    OK -> {pdf_path.name}")

                    downloaded += 1

                    records.append({
                        "collection_uuid": COLLECTION_UUID,
                        "item_uuid": item_uuid,
                        "item_url": item_url,
                        "title": title,
                        "pdf_url": pdf_url,
                        "pdf_name": pdf_path.name,
                        "pdf_path": str(pdf_path),
                        "downloaded_at": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
                    })

                    time.sleep(0.3)

                except Exception as e:
                    msg = f"PAGE {page} OBJ {i}\t{type(e).__name__}\t{str(e)}\n"
                    elog.write(msg)
                    print(f"    ERROR: {e}")
                    continue

            page += 1

            if total_pages is not None and page >= total_pages:
                break

    with open(META_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "collection_uuid",
                "item_uuid",
                "item_url",
                "title",
                "pdf_url",
                "pdf_name",
                "pdf_path",
                "downloaded_at"
            ]
        )
        writer.writeheader()
        writer.writerows(records)

    print("")
    print("=" * 70)
    print(f"PDFs descargados: {len(records)}")
    print(f"Metadata: {META_FILE}")
    print(f"Errores: {ERROR_LOG}")
    print("=" * 70)


if __name__ == "__main__":
    main()
