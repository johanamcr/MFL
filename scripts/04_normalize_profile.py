# -*- coding: utf-8 -*-

from pathlib import Path
import csv
import re
from collections import OrderedDict

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "data" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RAW_PROFILE_CSV = OUTPUT_DIR / "corpus_thematic_profile.csv"
NORM_PROFILE_CSV = OUTPUT_DIR / "corpus_thematic_profile_normalized.csv"
NORM_SUMMARY_TXT = OUTPUT_DIR / "corpus_thematic_normalized_summary.txt"

THEMES = OrderedDict({
    "livelihoods_equity": [
        "livelihood", "livelihoods", "equity", "equitable", "inclusive",
        "inclusion", "poverty", "income", "well-being", "wellbeing",
        "justice", "distributional equity"
    ],
    "nutrition_food_systems": [
        "nutrition", "nutritious", "food system", "food systems",
        "food security", "diet", "diets", "healthy diets", "nourishment"
    ],
    "biodiversity_ecosystems": [
        "biodiversity", "ecosystem", "ecosystems", "ecosystem services",
        "nature", "nature-positive", "forest", "forests", "restoration",
        "conservation", "habitat"
    ],
    "agroecology_farming": [
        "agroecology", "agroecological", "farming", "sustainable farming",
        "production systems", "agriculture", "agricultural practices",
        "soil", "water management", "crop", "cropping"
    ],
    "landscapes": [
        "landscape", "landscapes", "multifunctional landscape",
        "multifunctional landscapes", "source-to-sea", "territory",
        "territorial", "mosaic landscape"
    ],
    "policy_governance_institutions": [
        "policy", "policies", "governance", "institution", "institutions",
        "regulation", "regulatory", "public investment", "strategy",
        "strategies", "political economy"
    ],
    "investment_markets": [
        "investment", "investments", "market", "markets", "value chain",
        "private sector", "finance", "financial", "business model",
        "enterprise", "premium prices"
    ],
    "capacity_learning": [
        "capacity", "capacity building", "capacity sharing", "training",
        "learning", "co-creation", "knowledge sharing", "extension",
        "technical assistance", "peer learning"
    ],
    "gender_social_inclusion": [
        "gender", "women", "youth", "social inclusion", "marginalized",
        "marginalised", "empowerment", "indigenous", "indigenous peoples"
    ],
    "climate_resilience": [
        "climate", "resilience", "resilient", "adaptation", "mitigation",
        "emissions", "low-emission", "climate-smart", "carbon"
    ],
    "outcomes_impact": [
        "outcome", "outcomes", "impact", "impacts", "results",
        "theory of change", "toc", "expected outcomes", "high-level outputs"
    ],
    "evidence_data_methods": [
        "evidence", "data", "analysis", "monitoring", "evaluation",
        "metrics", "indicator", "indicators", "model", "models",
        "scenario", "forecast", "decision tools"
    ]
})


def read_text(txt_path):
    return txt_path.read_text(encoding="utf-8", errors="ignore").lower()


def count_term(text, term):
    pattern = r"\b" + re.escape(term.lower()) + r"\b"
    return len(re.findall(pattern, text))


def word_count(text):
    return len(re.findall(r"\b\w+\b", text))


def profile_document(txt_path):
    text = read_text(txt_path)
    total_words = word_count(text)

    row = {"document": txt_path.name, "total_words": total_words}
    total_theme_hits = 0

    for theme, terms in THEMES.items():
        theme_count = 0
        for term in terms:
            theme_count += count_term(text, term)
        row[theme] = theme_count
        row[f"{theme}_per_1000w"] = round((theme_count / total_words) * 1000, 3) if total_words > 0 else 0.0
        total_theme_hits += theme_count

    row["total_theme_hits"] = total_theme_hits
    return row


def write_csv(rows):
    fieldnames = ["document", "total_words"] + list(THEMES.keys()) + \
                 [f"{theme}_per_1000w" for theme in THEMES.keys()] + \
                 ["total_theme_hits"]

    with open(NORM_PROFILE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows):
    raw_totals = {theme: 0 for theme in THEMES.keys()}
    norm_averages = {}

    for theme in THEMES.keys():
        raw_totals[theme] = sum(row[theme] for row in rows)
        vals = [row[f"{theme}_per_1000w"] for row in rows]
        norm_averages[theme] = round(sum(vals) / len(vals), 3) if vals else 0.0

    ranked_raw = sorted(raw_totals.items(), key=lambda x: x[1], reverse=True)
    ranked_norm = sorted(norm_averages.items(), key=lambda x: x[1], reverse=True)

    with open(NORM_SUMMARY_TXT, "w", encoding="utf-8") as f:
        f.write("NORMALIZED CORPUS THEMATIC SUMMARY\n")
        f.write("=" * 70 + "\n\n")

        f.write("A. Top themes by raw counts across the corpus\n")
        for i, (theme, total) in enumerate(ranked_raw, start=1):
            f.write(f"{i}. {theme}: {total}\n")

        f.write("\n" + "-" * 70 + "\n\n")

        f.write("B. Top themes by average normalized intensity (mentions per 1000 words)\n")
        for i, (theme, score) in enumerate(ranked_norm, start=1):
            f.write(f"{i}. {theme}: {score}\n")

        f.write("\n" + "=" * 70 + "\n\n")
        f.write("C. Top normalized themes by document\n\n")

        for row in rows:
            f.write(f"{row['document']} | total_words={row['total_words']}\n")
            ranked_doc = sorted(
                [(theme, row[f"{theme}_per_1000w"]) for theme in THEMES.keys()],
                key=lambda x: x[1],
                reverse=True
            )
            for theme, value in ranked_doc[:5]:
                f.write(f"  - {theme}: {value}\n")
            f.write("\n")


def main():
    txt_files = sorted(PROCESSED_DIR.glob("*.txt"))

    if not txt_files:
        print("No se encontraron archivos .txt en:", PROCESSED_DIR)
        return

    rows = []
    for txt_file in txt_files:
        row = profile_document(txt_file)
        rows.append(row)
        print(f"Procesado: {txt_file.name} | total_words={row['total_words']} | total_theme_hits={row['total_theme_hits']}")

    write_csv(rows)
    write_summary(rows)

    print("\n===================================")
    print("Perfil temático normalizado generado")
    print("CSV:", NORM_PROFILE_CSV)
    print("Resumen:", NORM_SUMMARY_TXT)
    print("===================================")


if __name__ == "__main__":
    main()
