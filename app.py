# -*- coding: utf-8 -*-

from pathlib import Path
import re
from collections import OrderedDict, defaultdict

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "data" / "outputs"
LEADERSHIP_BRIEF = OUTPUT_DIR / "leadership_brief.txt"

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
    "methods": "evidence_data_methods",
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

SUGGESTED_QUESTIONS = {
    "What are the main thematic areas covered by this corpus?": {
        "theme": None,
        "focus": ""
    },
    "Which documents are most relevant for biodiversity and ecosystems?": {
        "theme": "biodiversity_ecosystems",
        "focus": ""
    },
    "What evidence does the corpus provide on livelihoods and inclusion?": {
        "theme": "livelihoods_equity",
        "focus": ""
    },
    "Which policy and governance issues are most visible?": {
        "theme": "policy_governance_institutions",
        "focus": ""
    },
    "What methods and evidence gaps are visible in the sample?": {
        "theme": "evidence_data_methods",
        "focus": ""
    },
    "Show me evidence on livelihoods in Zimbabwe": {
        "theme": "livelihoods_equity",
        "focus": "zimbabwe"
    },
    "Show me evidence on biodiversity in Kenya": {
        "theme": "biodiversity_ecosystems",
        "focus": "kenya"
    }
}


@st.cache_data
def read_text_file(path_str: str):
    path = Path(path_str)
    if path.exists():
        return path.read_text(encoding="utf-8", errors="ignore")
    return None


@st.cache_data
def load_processed_texts(processed_dir_str: str):
    processed_dir = Path(processed_dir_str)
    txt_files = sorted(processed_dir.glob("*.txt"))
    data = {}
    for txt_file in txt_files:
        data[txt_file.name] = txt_file.read_text(encoding="utf-8", errors="ignore")
    return data


def split_pages_from_text(text: str):
    parts = PAGE_PATTERN.split(text)
    pages = []
    for i in range(1, len(parts), 2):
        page_num = int(parts[i])
        page_text = parts[i + 1].strip()
        pages.append((page_num, page_text))
    return pages


def count_term(text: str, term: str):
    pattern = r"\b" + re.escape(term.lower()) + r"\b"
    return len(re.findall(pattern, text.lower()))


def make_snippet(text: str, terms, window=1000):
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

    first_period = snippet.find(". ")
    if first_period != -1 and first_period < 120:
        snippet = snippet[first_period + 2:].strip()

    return snippet


def score_page(page_text: str, terms):
    total = 0
    matched = []

    for term in terms:
        c = count_term(page_text, term)
        if c > 0:
            total += c
            matched.append((term, c))

    return total, matched


def filter_documents(doc_names, focus):
    if not focus:
        return doc_names
    focus = focus.lower().strip()
    return [doc for doc in doc_names if focus in doc.lower()]


def build_quick_reading(theme_key, ranked_docs, hits):
    label = THEME_LABELS.get(theme_key, theme_key)

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


def run_theme_search(theme_key, focus, processed_texts):
    terms = THEMES[theme_key]
    available_docs = list(processed_texts.keys())
    selected_docs = filter_documents(available_docs, focus)

    all_hits = []
    document_scores = defaultdict(int)

    for doc_name in selected_docs:
        pages = split_pages_from_text(processed_texts[doc_name])

        for page_num, page_text in pages:
            score, matched = score_page(page_text, terms)
            if score > 0:
                snippet = make_snippet(page_text, terms, window=1000)
                all_hits.append({
                    "document": doc_name,
                    "page": page_num,
                    "score": score,
                    "matched": matched,
                    "snippet": snippet
                })
                document_scores[doc_name] += score

    all_hits = sorted(all_hits, key=lambda x: x["score"], reverse=True)
    ranked_docs = sorted(document_scores.items(), key=lambda x: x[1], reverse=True)

    return {
        "theme_key": theme_key,
        "theme_label": THEME_LABELS.get(theme_key, theme_key),
        "focus": focus if focus else "Full corpus",
        "quick_reading": build_quick_reading(theme_key, ranked_docs, all_hits),
        "top_docs": ranked_docs[:5],
        "evidence": all_hits[:10]
    }


def show_search_results(results):
    st.markdown("### Quick reading")
    st.write(results["quick_reading"])

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### Top supporting documents")
        if results["top_docs"]:
            for i, (doc, score) in enumerate(results["top_docs"], start=1):
                st.write(f"{i}. {doc} | score={score}")
        else:
            st.write("No supporting documents found.")

    with col2:
        st.markdown("### Key evidence excerpts")
        if results["evidence"]:
            for i, ev in enumerate(results["evidence"][:5], start=1):
                title = f"Excerpt {i} | {ev['document']} | page {ev['page']} | score={ev['score']}"
                with st.expander(title, expanded=(i == 1)):
                    st.write(f"Matched terms: {ev['matched']}")
                    st.write(ev["snippet"])
        else:
            st.write("No excerpts found.")

    st.markdown("### Search note")
    st.info(
        "This output is based on keyword matching and retrieved evidence. "
        "Use it as a first-pass thematic scan."
    )


st.set_page_config(
    page_title="CGSpace Outcomes Agent",
    layout="wide"
)

st.title("CGSpace Outcomes Agent")
st.caption("Interactive prototype for leadership-oriented exploration of a CGSpace document corpus")

processed_texts = load_processed_texts(str(PROCESSED_DIR))

tab1, tab2, tab3 = st.tabs([
    "Corpus overview",
    "Explore by theme",
    "Suggested leadership questions"
])

with tab1:
    st.subheader("Corpus overview")

    brief_text = read_text_file(str(LEADERSHIP_BRIEF))

    if brief_text:
        st.text_area(
            "Leadership brief",
            brief_text,
            height=520
        )
    else:
        st.warning(
            "The leadership brief was not found. "
            "Run scripts/05_build_leadership_brief.py first and upload data/outputs/leadership_brief.txt."
        )

with tab2:
    st.subheader("Explore by theme")

    selected_theme_label = st.selectbox(
        "Select a theme",
        list(THEME_LABELS.values())
    )

    reverse_theme_labels = {v: k for k, v in THEME_LABELS.items()}
    selected_theme_key = reverse_theme_labels[selected_theme_label]

    focus_text = st.text_input(
        "Optional focus",
        placeholder="For example: zimbabwe, kenya, ucayali, wheat, cocoa"
    )

    if st.button("Run thematic search", key="run_theme_search"):
        results = run_theme_search(selected_theme_key, focus_text, processed_texts)
        show_search_results(results)

with tab3:
    st.subheader("Suggested leadership questions")

    selected_question = st.selectbox(
        "Choose a question",
        list(SUGGESTED_QUESTIONS.keys())
    )

    question_config = SUGGESTED_QUESTIONS[selected_question]

    if question_config["theme"] is None:
        st.markdown("### Guidance")
        st.write("Use the Corpus overview tab to review the overall thematic profile and the leadership brief.")
    else:
        st.markdown("### Guidance")
        st.write(
            f"This question is mapped to the theme '{THEME_LABELS[question_config['theme']]}'"
            + (f" with focus '{question_config['focus']}'." if question_config["focus"] else ".")
        )

        if st.button("Run suggested question", key="run_suggested_question"):
            results = run_theme_search(
                question_config["theme"],
                question_config["focus"],
                processed_texts
            )
            show_search_results(results)
