# -*- coding: utf-8 -*-

from pathlib import Path
import streamlit as st

# Ruta base relativa al repo
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "data" / "outputs"

LEADERSHIP_BRIEF = OUTPUT_DIR / "leadership_brief.txt"

THEME_FILES = {
    "Livelihoods, equity and inclusion": "theme_explorer_livelihoods_equity_all_docs.txt",
    "Nutrition and food systems": "theme_explorer_nutrition_food_systems_all_docs.txt",
    "Biodiversity and ecosystems": "theme_explorer_biodiversity_ecosystems_all_docs.txt",
    "Agroecology and farming systems": "theme_explorer_agroecology_farming_all_docs.txt",
    "Landscapes and territorial approaches": "theme_explorer_landscapes_all_docs.txt",
    "Policy, governance and institutions": "theme_explorer_policy_governance_institutions_all_docs.txt",
    "Investment, markets and business models": "theme_explorer_investment_markets_all_docs.txt",
    "Capacity, learning and technical assistance": "theme_explorer_capacity_learning_all_docs.txt",
    "Gender and social inclusion": "theme_explorer_gender_social_inclusion_all_docs.txt",
    "Climate and resilience": "theme_explorer_climate_resilience_all_docs.txt",
    "Program outcomes and theory of change": "theme_explorer_program_outcomes_all_docs.txt",
    "General outcomes and impacts": "theme_explorer_general_outcomes_all_docs.txt",
    "Evidence, data and methods": "theme_explorer_evidence_data_methods_all_docs.txt",
}

SUGGESTED_QUESTIONS = {
    "What are the main thematic areas covered by this corpus?":
        "Use the Corpus overview tab and review the leadership brief.",
    "Which documents are most relevant for biodiversity and ecosystems?":
        "Open the Biodiversity and ecosystems theme in the Explore by theme tab.",
    "What evidence does the corpus provide on livelihoods and inclusion?":
        "Open the Livelihoods, equity and inclusion theme in the Explore by theme tab.",
    "Which policy and governance issues are most visible?":
        "Open the Policy, governance and institutions theme in the Explore by theme tab.",
    "Which topics appear less visible in this sample?":
        "Use the Corpus overview tab and inspect the less visible themes in the leadership brief.",
    "What methods and evidence gaps are visible in the sample?":
        "Open the Evidence, data and methods theme in the Explore by theme tab.",
}

QUESTION_TO_THEME = {
    "Which documents are most relevant for biodiversity and ecosystems?":
        "Biodiversity and ecosystems",
    "What evidence does the corpus provide on livelihoods and inclusion?":
        "Livelihoods, equity and inclusion",
    "Which policy and governance issues are most visible?":
        "Policy, governance and institutions",
    "What methods and evidence gaps are visible in the sample?":
        "Evidence, data and methods",
}


def read_text_file(path: Path):
    if path.exists():
        return path.read_text(encoding="utf-8", errors="ignore")
    return None


def parse_theme_file(text: str):
    sections = {
        "quick_reading": "",
        "top_docs": [],
        "evidence": [],
        "search_note": "",
    }

    lines = text.splitlines()
    mode = None
    current_excerpt = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("1. Quick reading"):
            mode = "quick"
            continue
        elif stripped.startswith("2. Top supporting documents"):
            mode = "docs"
            continue
        elif stripped.startswith("3. Key evidence excerpts"):
            if current_excerpt:
                sections["evidence"].append("\n".join(current_excerpt).strip())
                current_excerpt = []
            mode = "evidence"
            continue
        elif stripped.startswith("4. Search note"):
            if current_excerpt:
                sections["evidence"].append("\n".join(current_excerpt).strip())
                current_excerpt = []
            mode = "note"
            continue
        elif stripped.startswith("----") or stripped.startswith("===="):
            continue

        if mode == "quick":
            if stripped:
                sections["quick_reading"] += stripped + " "

        elif mode == "docs":
            if stripped and stripped[0].isdigit() and ". " in stripped:
                sections["top_docs"].append(stripped)

        elif mode == "evidence":
            if stripped.startswith("[") and "]" in stripped:
                if current_excerpt:
                    sections["evidence"].append("\n".join(current_excerpt).strip())
                    current_excerpt = []
                current_excerpt.append(stripped)
            else:
                if stripped:
                    current_excerpt.append(stripped)

        elif mode == "note":
            if stripped:
                sections["search_note"] += stripped + " "

    if current_excerpt:
        sections["evidence"].append("\n".join(current_excerpt).strip())

    sections["quick_reading"] = sections["quick_reading"].strip()
    sections["search_note"] = sections["search_note"].strip()

    return sections


def show_theme_content(theme_label: str):
    theme_file = OUTPUT_DIR / THEME_FILES[theme_label]
    theme_text = read_text_file(theme_file)

    if not theme_text:
        st.warning(
            f"The file {theme_file.name} was not found. "
            f"Run scripts/06_theme_explorer.py for this theme first."
        )
        return

    parsed = parse_theme_file(theme_text)

    st.markdown("### Quick reading")
    st.write(parsed["quick_reading"] if parsed["quick_reading"] else "No quick reading available.")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### Top supporting documents")
        if parsed["top_docs"]:
            for doc in parsed["top_docs"]:
                st.write(doc)
        else:
            st.write("No supporting documents found.")

    with col2:
        st.markdown("### Key evidence excerpts")
        if parsed["evidence"]:
            for i, ev in enumerate(parsed["evidence"][:5], start=1):
                with st.expander(f"Excerpt {i}", expanded=(i == 1)):
                    st.write(ev)
        else:
            st.write("No excerpts found.")

    st.markdown("### Search note")
    st.info(parsed["search_note"] if parsed["search_note"] else "No search note available.")


st.set_page_config(
    page_title="CGSpace Outcomes Agent",
    layout="wide"
)

st.title("CGSpace Outcomes Agent")
st.caption("Prototype for leadership-oriented exploration of a CGSpace document corpus")

tab1, tab2, tab3 = st.tabs([
    "Corpus overview",
    "Explore by theme",
    "Suggested leadership questions"
])

with tab1:
    st.subheader("Corpus overview")

    brief_text = read_text_file(LEADERSHIP_BRIEF)

    if brief_text:
        st.text_area(
            "Leadership brief",
            brief_text,
            height=520
        )
    else:
        st.warning(
            "The leadership brief was not found. "
            "Run scripts/05_build_leadership_brief.py first."
        )

with tab2:
    st.subheader("Explore by theme")

    selected_theme = st.selectbox(
        "Select a theme",
        list(THEME_FILES.keys())
    )

    show_theme_content(selected_theme)

with tab3:
    st.subheader("Suggested leadership questions")

    selected_question = st.selectbox(
        "Choose a question",
        list(SUGGESTED_QUESTIONS.keys())
    )

    st.markdown("### Guidance")
    st.write(SUGGESTED_QUESTIONS[selected_question])

    st.markdown("### Suggested place to look")

    if selected_question in QUESTION_TO_THEME:
        recommended_theme = QUESTION_TO_THEME[selected_question]
        st.success(f"Recommended theme: {recommended_theme}")
        show_theme_content(recommended_theme)
    else:
        st.success("Recommended tab: Corpus overview")
