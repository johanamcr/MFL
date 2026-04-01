# -*- coding: utf-8 -*-

from pathlib import Path
import csv
import fitz  # PyMuPDF

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = BASE_DIR / "data" / "pdfs"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
LOGS_DIR = BASE_DIR / "data" / "logs"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

SUMMARY_CSV = PROCESSED_DIR / "document_summary.csv"
ERROR_LOG = LOGS_DIR / "extract_errors.log"


def clean_text(text):
    if not text:
        return ""
    text = text.replace("\x00", " ")
    text = text.replace("\r", "\n")
    text = " ".join(text.split())
    return text.strip()


def extract_pdf(pdf_path):
    doc = fitz.open(pdf_path)

    pages_data = []
    total_chars = 0
    non_empty_pages = 0

    for page_num in range(len(doc)):
        page = doc[page_num]
        raw_text = page.get_text("text")
        text = clean_text(raw_text)

        if text:
            non_empty_pages += 1
            total_chars += len(text)

        pages_data.append({
            "page": page_num + 1,
            "text": text
        })

    doc.close()

    return {
        "pages_data": pages_data,
        "total_pages": len(pages_data),
        "non_empty_pages": non_empty_pages,
        "total_chars": total_chars
    }


def save_txt_by_document(pdf_name, pages_data):
    txt_path = PROCESSED_DIR / f"{Path(pdf_name).stem}.txt"

    with open(txt_path, "w", encoding="utf-8") as f:
        for row in pages_data:
            f.write(f"\n--- PAGE {row['page']} ---\n")
            f.write(row["text"])
            f.write("\n")

    return txt_path


def clear_previous_processed_files():
    old_txt_files = list(PROCESSED_DIR.glob("*.txt"))
    removed = 0

    for txt_file in old_txt_files:
        try:
            txt_file.unlink()
            removed += 1
        except Exception as e:
            print(f"No se pudo borrar {txt_file.name}: {e}")

    if SUMMARY_CSV.exists():
        try:
            SUMMARY_CSV.unlink()
        except Exception as e:
            print(f"No se pudo borrar {SUMMARY_CSV.name}: {e}")

    return removed


def main():
    pdf_files = sorted(PDF_DIR.glob("*.pdf"))

    if not pdf_files:
        print("No se encontraron PDFs en:", PDF_DIR)
        return

    removed = clear_previous_processed_files()
    print(f"TXT previos eliminados: {removed}")

    summary_rows = []

    with open(ERROR_LOG, "w", encoding="utf-8") as elog:
        for pdf_file in pdf_files:
            print(f"\nProcesando: {pdf_file.name}")

            try:
                result = extract_pdf(pdf_file)
                txt_path = save_txt_by_document(pdf_file.name, result["pages_data"])

                avg_chars = 0
                if result["total_pages"] > 0:
                    avg_chars = round(result["total_chars"] / result["total_pages"], 2)

                summary_rows.append({
                    "pdf_name": pdf_file.name,
                    "txt_name": txt_path.name,
                    "total_pages": result["total_pages"],
                    "non_empty_pages": result["non_empty_pages"],
                    "total_chars": result["total_chars"],
                    "avg_chars_per_page": avg_chars
                })

                print(
                    f"  OK | páginas: {result['total_pages']} | "
                    f"texto total: {result['total_chars']} caracteres"
                )

            except Exception as e:
                msg = f"{pdf_file.name}\t{type(e).__name__}\t{str(e)}\n"
                elog.write(msg)
                print(f"  ERROR: {e}")

    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "pdf_name",
                "txt_name",
                "total_pages",
                "non_empty_pages",
                "total_chars",
                "avg_chars_per_page"
            ]
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    print("\n==============================")
    print("Extracción terminada")
    print("Resumen:", SUMMARY_CSV)
    print("TXT generados en:", PROCESSED_DIR)
    print("Log de errores:", ERROR_LOG)
    print("==============================")


if __name__ == "__main__":
    main()
