# CGSpace Outcomes Agent

A lightweight prototype to explore CGSpace documents from the CGIAR Multifunctional Landscapes collection and support leadership-oriented document review.

## What this project does

This project helps transform a set of downloaded CGSpace PDFs into a searchable thematic evidence base.

It supports four main steps:

1. Download PDFs from a CGSpace collection
2. Extract text from PDFs
3. Build thematic summaries of the corpus
4. Explore evidence by theme through a Streamlit app

## Current workflow

### 1. Download documents
Run:

```bash
python -u scripts/00_download_collection_pdfs.py