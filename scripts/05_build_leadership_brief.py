# -*- coding: utf-8 -*-

from pathlib import Path
import csv

BASE_DIR = Path("/home/jcastillo/cgspace_outcomes_agent")
OUTPUT_DIR = BASE_DIR / "data" / "outputs"

INPUT_CSV = OUTPUT_DIR / "corpus_thematic_profile_normalized.csv"
BRIEF_TXT = OUTPUT_DIR / "leadership_brief.txt"

THEMES = [
    "livelihoods_equity",
    "nutrition_food_systems",
    "biodiversity_ecosystems",
    "agroecology_farming",
    "landscapes",
    "policy_governance_institutions",
    "investment_markets",
    "capacity_learning",
    "gender_social_inclusion",
    "climate_resilience",
    "outcomes_impact",
    "evidence_data_methods"
]

THEME_LABELS = {
    "livelihoods_equity": "Livelihoods, equity and inclusion",
    "nutrition_food_systems": "Nutrition and food systems",
    "biodiversity_ecosystems": "Biodiversity and ecosystems",
    "agroecology_farming": "Agroecology and farming systems",
    "landscapes": "Landscapes and territorial approaches",
    "policy_governance_institutions": "Policy, governance and institutions",
    "investment_markets": "Investment, markets and business models",
    "capacity_learning": "Capacity, learning and technical assistance",
    "gender_social_inclusion": "Gender and social inclusion",
    "climate_resilience": "Climate and resilience",
    "outcomes_impact": "Outcomes, impacts and theory of change",
    "evidence_data_methods": "Evidence, data and methods"
}


def read_rows():
    rows = []
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean = {"document": row["document"], "total_words": int(float(row["total_words"]))}
            for theme in THEMES:
                clean[theme] = int(float(row[theme]))
                clean[f"{theme}_per_1000w"] = float(row[f"{theme}_per_1000w"])
            rows.append(clean)
    return rows


def rank_corpus(rows):
    raw_totals = {}
    norm_avg = {}

    for theme in THEMES:
        raw_totals[theme] = sum(r[theme] for r in rows)
        norm_avg[theme] = sum(r[f"{theme}_per_1000w"] for r in rows) / len(rows)

    ranked_raw = sorted(raw_totals.items(), key=lambda x: x[1], reverse=True)
    ranked_norm = sorted(norm_avg.items(), key=lambda x: x[1], reverse=True)

    return ranked_raw, ranked_norm


def top_themes_for_doc(row, n=5):
    ranked = sorted(
        [(theme, row[f"{theme}_per_1000w"]) for theme in THEMES],
        key=lambda x: x[1],
        reverse=True
    )
    return ranked[:n]


def classify_document(row):
    top3 = [theme for theme, _ in top_themes_for_doc(row, n=3)]

    if "landscapes" in top3 and "policy_governance_institutions" in top3:
        return "Programmatic / strategic"
    if "evidence_data_methods" in top3 or "outcomes_impact" in top3:
        return "Technical / evidence-oriented"
    if "agroecology_farming" in top3:
        return "Technical / practice-oriented"
    return "Mixed"


def write_brief(rows, ranked_raw, ranked_norm):
    top_raw = ranked_raw[:5]
    low_raw = ranked_raw[-3:]
    top_norm = ranked_norm[:5]

    doc_profiles = []
    for row in rows:
        doc_profiles.append({
            "document": row["document"],
            "type": classify_document(row),
            "top_themes": top_themes_for_doc(row, n=5)
        })

    with open(BRIEF_TXT, "w", encoding="utf-8") as f:
        f.write("LEADERSHIP BRIEF – MULTIFUNCTIONAL LANDSCAPES DOCUMENT CORPUS\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. Executive takeaway\n")
        f.write("-" * 80 + "\n")
        f.write(
            "This document set appears to combine two main layers of reporting. "
            "First, a programmatic-strategic layer focused on landscapes, governance, biodiversity, "
            "investment, and enabling conditions. Second, a technical-evidence layer focused on "
            "agroecology, outcomes, evidence generation, and learning/capacity support.\n\n"
        )

        f.write("2. Most visible thematic areas in the corpus (raw volume)\n")
        f.write("-" * 80 + "\n")
        for i, (theme, value) in enumerate(top_raw, start=1):
            f.write(f"{i}. {THEME_LABELS[theme]}: {value}\n")
        f.write("\n")

        f.write("3. Most intense themes after normalization (mentions per 1000 words)\n")
        f.write("-" * 80 + "\n")
        for i, (theme, value) in enumerate(top_norm, start=1):
            f.write(f"{i}. {THEME_LABELS[theme]}: {round(value, 3)}\n")
        f.write("\n")

        f.write("4. Less visible themes in this sample\n")
        f.write("-" * 80 + "\n")
        for i, (theme, value) in enumerate(low_raw, start=1):
            f.write(f"{i}. {THEME_LABELS[theme]}: {value}\n")
        f.write(
            "\nThese areas are not absent, but they appear with lower relative visibility in the current sample.\n\n"
        )

        f.write("5. Document-level reading\n")
        f.write("-" * 80 + "\n")
        for dp in doc_profiles:
            f.write(f"{dp['document']}\n")
            f.write(f"  Type: {dp['type']}\n")
            f.write("  Top themes:\n")
            for theme, value in dp["top_themes"]:
                f.write(f"    - {THEME_LABELS[theme]}: {round(value, 3)}\n")
            f.write("\n")

        f.write("6. Initial interpretation for leadership use\n")
        f.write("-" * 80 + "\n")
        f.write(
            "The sample suggests that Multifunctional Landscapes is being communicated not only as an "
            "environmental or biodiversity program, but as a broader transformation agenda linking "
            "landscapes, agroecological transitions, governance, investment, and evidence generation. "
            "The strongest strategic document in the sample appears to be the program framing document, "
            "while several shorter papers contribute technical or evidence-oriented support.\n\n"
        )

        f.write("7. Caveats\n")
        f.write("-" * 80 + "\n")
        f.write(
            "- This is a term-frequency based profile, not a semantic interpretation.\n"
            "- Longer documents still matter more in raw counts, even after normalization is added as a second lens.\n"
            "- A small number of documents can distort averages.\n"
            "- Results should be interpreted as a first-pass strategic reading, not a final content evaluation.\n\n"
        )

        f.write("8. Suggested next questions for the tool\n")
        f.write("-" * 80 + "\n")
        f.write(
            "- What are the main thematic areas covered by this corpus?\n"
            "- Which documents are most relevant for biodiversity / livelihoods / policy / nutrition?\n"
            "- What outcomes are most visible in the sample?\n"
            "- Which themes appear underrepresented?\n"
            "- Which documents are programmatic versus technical?\n"
        )


def main():
    rows = read_rows()
    ranked_raw, ranked_norm = rank_corpus(rows)
    write_brief(rows, ranked_raw, ranked_norm)

    print("\n===================================")
    print("Leadership brief generated")
    print("Output:", BRIEF_TXT)
    print("===================================")


if __name__ == "__main__":
    main()