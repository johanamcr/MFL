# -*- coding: utf-8 -*-

from pathlib import Path
import re
from collections import OrderedDict, defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "data" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PAGE_PATTERN = re.compile(r"--- PAGE (\d+) ---")

THEMES = OrderedDict({
    "livelihoods_equity": [
        "livelihood", "livelihoods", "equity", "equitable", "inclusive",
        "inclusion", "poverty", "income", "well-being", "wellbeing",
        "justice", "distributional equity", "livelihood diversification",
        "income generation", "collective action", "social inclusion",
        "food insecurity", "market access"
    ],
    "nutrition_food_systems": [
        "nutrition", "nutritious", "food system", "food systems",
        "food security", "diet", "diets", "healthy diets", "nourishment",
        "sustainable food systems", "food security nutrition",
        "community nutrition gardens"
    ],
    "biodiversity_ecosystems": [
        "biodiversity", "ecosystem", "ecosystems", "ecosystem services",
        "nature", "nature-positive", "forest", "forests", "restoration",
        "conservation", "habitat", "biodiversity ecosystem services",
        "land restoration", "nature loss", "biological control"
    ],
    "agroecology_farming": [
        "agroecology", "agroecological", "farming", "sustainable farming",
        "production systems", "agriculture", "agricultural practices",
        "soil", "water management", "crop", "cropping",
        "agroecological practices", "agroecological transitions",
        "agroecological transition", "conservation agriculture",
        "minimum tillage", "soil health", "soil organic carbon"
    ],
    "landscapes": [
        "landscape", "landscapes", "multifunctional landscape",
        "multifunctional landscapes", "source-to-sea", "territory",
        "territorial", "mosaic landscape", "lake victoria basin",
        "vision to action", "landscape transformation"
    ],
    "policy_governance_institutions": [
        "policy", "policies", "governance", "institution", "institutions",
        "regulation", "regulatory", "public investment", "strategy",
        "strategies", "political economy", "natural resource management",
        "district development", "resource management committee",
        "civil society organizations", "policy brief", "inclusive governance",
        "institutionalizing multifunctional landscapes"
    ],
    "investment_markets": [
        "investment", "investments", "market", "markets", "value chain",
        "value chains", "private sector", "finance", "financial",
        "business model", "business models", "premium prices",
        "market access", "investment opportunities"
    ],
    "capacity_learning": [
        "capacity", "capacity building", "capacity sharing", "training",
        "learning", "co-creation", "knowledge sharing", "extension",
        "technical assistance", "peer learning", "stakeholder engagement",
        "field days", "exchange visits", "training report"
    ],
    "gender_social_inclusion": [
        "gender", "women", "youth", "social inclusion", "marginalized",
        "marginalised", "empowerment", "indigenous", "indigenous peoples",
        "fairness"
    ],
    "climate_resilience": [
        "climate", "resilience", "resilient", "adaptation", "mitigation",
        "emissions", "low-emission", "climate-smart", "carbon",
        "climate change"
    ],
    "program_outcomes": [
        "program outcome", "program outcomes", "program-level outcome",
        "program-level outcomes", "intermediate program-level outcome",
        "intermediate program-level outcomes", "expected outcomes",
        "theory of change", "toc", "high-level outputs",
        "multifunctional performance", "stakeholder engagement report",
        "science program"
    ],
    "general_outcomes": [
        "outcome", "outcomes", "impact", "impacts", "result", "results"
    ],
    "evidence_data_methods": [
        "evidence", "data", "analysis", "monitoring", "evaluation",
        "metrics", "indicator", "indicators", "model", "models",
        "scenario", "forecast", "decision tools", "assessment frameworks",
        "key informant interviews", "focus group discussions",
        "digital traceability system"
    ]
})

ALIASES = {
    "livelihoods": "livelihoods_equity",
    "livelihood": "livelihoods_equity",
    "equity": "livelihoods_equity",
    "nutrition": "nutrition_food_systems",
    "food": "nutrition_food_systems",
    "biodiversity": "biodiversity_ecosystems",
    "ecosystems": "biodiversity_ecosystems",
    "agroecology": "agroecology_farming",
    "farming": "agroecology_farming",
    "landscape": "landscapes",
    "landscapes": "landscapes",
    "policy": "policy_governance_institutions",
    "governance": "policy_governance_institutions",
    "institutions": "policy_governance_institutions",
    "investment": "investment_markets",
    "markets": "investment_markets",
    "capacity": "capacity_learning",
    "learning": "capacity_learning",
    "gender": "gender_social_inclusion",
    "inclusion": "gender_social_inclusion",
    "climate": "climate_resilience",
    "resilience": "climate_resilience",
    "program outcomes": "program_outcomes",
    "program outcome": "program_outcomes",
    "outcomes": "general_outcomes",
    "outcome": "general_outcomes",
    "impact": "general_outcomes",
    "evidence": "evidence_data_methods",
    "methods": "evidence_data_methods"
}

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
    "program_outcomes": "Program outcomes and theory of change",
    "general_outcomes": "General outcomes and impacts",
    "evidence_data_methods": "Evidence, data and methods"
}


def split_pages(txt_path):
    text = txt_path.read_text(encoding="utf-8", errors="ignore")
    parts = PAGE_PATTERN.split(text)
    pages = []

    for i in range(1, len(parts), 2):
        page_num = int(parts[i])
        page_text = parts[i + 1].strip()
        pages.append((page_num, page_text))

    return pages


def count_term(text, term):
    pattern = r"\b" + re.escape(term.lower()) + r"\b"
    return len(re.findall(pattern, text.lower()))


def make_snippet(text, terms, window=1000):
    text_lower = text.lower()
    positions = []

    for term in terms:
        pos = text_lower.find(term.lower())
        if pos != -1:
            positions.append(pos)

    if not positions:
        snippet = text[:window].strip()
    else:
        start = max(0, min(positions) - 160)
        end = min(len(text), start + window)
        snippet = text[start:end].strip()

    # limpieza ligera para no arrancar cortado
    first_period = snippet.find(". ")
    if first_period != -1 and first_period < 120:
        snippet = snippet[first_period + 2:].strip()

    return snippet


def score_page(page_text, terms):
    total = 0
    matched = []

    for term in terms:
        c = count_term(page_text, term)
        if c > 0:
            total += c
            matched.append((term, c))

    return total, matched


def resolve_theme(user_input):
    raw = user_input.strip().lower()

    if raw.isdigit():
        idx = int(raw)
        if 1 <= idx <= len(THEMES):
            return list(THEMES.keys())[idx - 1]

    if raw in THEMES:
        return raw

    if raw in ALIASES:
        return ALIASES[raw]

    return None


def choose_theme():
    print("\nAvailable themes:\n")
    for i, theme in enumerate(THEMES.keys(), start=1):
        print(f"{i}. {theme}")

    raw = input("\nEnter the theme number, exact name, or alias: ").strip()
    theme = resolve_theme(raw)

    if not theme:
        print("\nInvalid theme.")
        return None

    return theme


def choose_document_focus():
    raw = input(
        "\nOptional focus: enter a word or short phrase to narrow the search to a subset of documents "
        "(for example: program, landscape, nutrition, zimbabwe). "
        "Press Enter to search the full corpus: "
    ).strip().lower()
    return raw


def filter_txt_files(txt_files, doc_focus):
    if not doc_focus:
        return txt_files
    return [p for p in txt_files if doc_focus in p.name.lower()]


def build_quick_reading(theme, ranked_docs, hits):
    label = THEME_LABELS.get(theme, theme)

    if not hits:
        return f"No clear evidence was found for '{label}' in the selected corpus."

    if len(ranked_docs) == 1:
        return f"This theme appears in a very concentrated way in one document: {ranked_docs[0][0]}."

    total_score = sum(score for _, score in ranked_docs)
    top_doc, top_score = ranked_docs[0]
    top_share = top_score / total_score if total_score > 0 else 0

    if top_share >= 0.6:
        return (
            f"This theme appears strongly in the current sample, with most of the retrieved evidence "
            f"concentrated in {top_doc}."
        )

    if len(ranked_docs) >= 3:
        top_docs = ", ".join(doc for doc, _ in ranked_docs[:3])
        return (
            f"This theme is distributed across several documents, with the strongest evidence coming from "
            f"{top_docs}."
        )

    return "This theme is present in the selected corpus, with evidence spread across a small set of documents."


def build_search_note():
    return (
        "This output is based on keyword matching and retrieved evidence. "
        "Use it as a first-pass thematic scan."
    )


def main():
    theme = choose_theme()
    if not theme:
        return

    doc_focus = choose_document_focus()
    terms = THEMES[theme]

    txt_files = sorted(PROCESSED_DIR.glob("*.txt"))
    txt_files = filter_txt_files(txt_files, doc_focus)

    if not txt_files:
        print("\nNo documents matched that focus.")
        return

    all_hits = []
    document_scores = defaultdict(int)

    for txt_file in txt_files:
        pages = split_pages(txt_file)

        for page_num, page_text in pages:
            score, matched = score_page(page_text, terms)
            if score > 0:
                snippet = make_snippet(page_text, terms, window=1000)
                all_hits.append({
                    "document": txt_file.name,
                    "page": page_num,
                    "score": score,
                    "matched": matched,
                    "snippet": snippet
                })
                document_scores[txt_file.name] += score

    all_hits = sorted(all_hits, key=lambda x: x["score"], reverse=True)
    ranked_docs = sorted(document_scores.items(), key=lambda x: x[1], reverse=True)

    suffix = f"_{doc_focus}" if doc_focus else "_all_docs"
    out_file = OUTPUT_DIR / f"theme_explorer_{theme}{suffix}.txt"

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"THEME EXPLORER: {THEME_LABELS.get(theme, theme)}\n")
        f.write("=" * 90 + "\n\n")
        f.write(f"Theme key: {theme}\n")
        f.write(f"Theme terms: {terms}\n")
        f.write(f"Document focus: {doc_focus if doc_focus else 'Full corpus'}\n\n")

        f.write("1. Quick reading\n")
        f.write("-" * 90 + "\n")
        f.write(build_quick_reading(theme, ranked_docs, all_hits) + "\n\n")

        f.write("2. Top supporting documents\n")
        f.write("-" * 90 + "\n")
        if ranked_docs:
            for i, (doc, score) in enumerate(ranked_docs[:5], start=1):
                f.write(f"{i}. {doc} | score={score}\n")
        else:
            f.write("No relevant supporting documents found.\n")
        f.write("\n")

        f.write("3. Key evidence excerpts\n")
        f.write("-" * 90 + "\n")
        if all_hits:
            for i, hit in enumerate(all_hits[:10], start=1):
                f.write(f"[{i}] {hit['document']} | page {hit['page']} | score={hit['score']}\n")
                f.write(f"Matched terms: {hit['matched']}\n")
                f.write(hit["snippet"] + "\n")
                f.write("\n" + "-" * 90 + "\n\n")
        else:
            f.write("No relevant evidence excerpts found.\n\n")

        f.write("4. Search note\n")
        f.write("-" * 90 + "\n")
        f.write(build_search_note() + "\n")

    print(f"\nTheme resolved as: {theme}")
    print(f"Document focus: {doc_focus if doc_focus else 'Full corpus'}")
    print(f"Output written to: {out_file}")

    print("\nQuick reading:\n")
    print(build_quick_reading(theme, ranked_docs, all_hits))

    print("\nTop supporting documents:\n")
    if ranked_docs:
        for i, (doc, score) in enumerate(ranked_docs[:5], start=1):
            print(f"{i}. {doc} | score={score}")
    else:
        print("No relevant supporting documents found.")

    print("\nTop evidence excerpts:\n")
    if all_hits:
        for i, hit in enumerate(all_hits[:3], start=1):
            print(f"[{i}] {hit['document']} | page {hit['page']} | score={hit['score']}")
            print(hit["snippet"][:700])
            print("\n" + "-" * 90 + "\n")
    else:
        print("No relevant evidence excerpts found.")


if __name__ == "__main__":
    main()
