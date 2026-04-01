# -*- coding: utf-8 -*-

from pathlib import Path
import csv
import re
from collections import Counter

BASE_DIR = Path("/home/jcastillo/cgspace_outcomes_agent")
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = BASE_DIR / "data" / "outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

WORDS_CSV = OUTPUT_DIR / "dictionary_candidate_words.csv"
BIGRAMS_CSV = OUTPUT_DIR / "dictionary_candidate_bigrams.csv"
TRIGRAMS_CSV = OUTPUT_DIR / "dictionary_candidate_trigrams.csv"
SUMMARY_TXT = OUTPUT_DIR / "dictionary_candidate_summary.txt"

STOPWORDS = {
    "the", "and", "for", "with", "that", "this", "from", "into", "through", "over",
    "under", "between", "among", "within", "across", "their", "there", "these",
    "those", "which", "while", "where", "when", "what", "how", "such", "also",
    "than", "then", "they", "them", "been", "being", "have", "has", "had", "will",
    "would", "could", "should", "can", "may", "might", "using", "used", "use",
    "based", "other", "more", "most", "less", "many", "some", "each", "both",
    "including", "include", "includes", "towards", "across", "into", "very",
    "about", "because", "after", "before", "during", "around", "only", "than",
    "therefore", "however", "overall", "main", "first", "second", "third",
    "program", "programs", "study", "studies", "paper", "report", "reports",
    "data", "analysis", "results", "result", "outcome", "outcomes", "impact", "impacts",
    "page", "pages", "table", "figure", "fig", "section", "sections",
    "www", "http", "https", "doi", "org", "com",
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"
}


def read_all_text():
    txt_files = sorted(PROCESSED_DIR.glob("*.txt"))
    corpus = []

    for txt_file in txt_files:
        text = txt_file.read_text(encoding="utf-8", errors="ignore")
        corpus.append((txt_file.name, text))

    return corpus


def clean_text(text):
    text = text.lower()
    text = text.replace("\n", " ")
    text = re.sub(r"--- page \d+ ---", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[^a-záéíóúñü0-9\s\-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text):
    tokens = re.findall(r"\b[a-záéíóúñü][a-záéíóúñü\-]{2,}\b", text)
    return tokens


def valid_token(token):
    if token in STOPWORDS:
        return False
    if token.isdigit():
        return False
    if len(token) < 3:
        return False
    return True


def generate_ngrams(tokens, n=2):
    grams = []
    for i in range(len(tokens) - n + 1):
        chunk = tokens[i:i+n]
        if all(valid_token(tok) for tok in chunk):
            grams.append(" ".join(chunk))
    return grams


def write_counter_csv(counter, out_file, top_n=300):
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["term", "count"])
        for term, count in counter.most_common(top_n):
            writer.writerow([term, count])


def main():
    corpus = read_all_text()

    if not corpus:
        print("No se encontraron archivos .txt en processed.")
        return

    word_counter = Counter()
    bigram_counter = Counter()
    trigram_counter = Counter()

    doc_level_top = []

    for doc_name, raw_text in corpus:
        text = clean_text(raw_text)
        tokens = [t for t in tokenize(text) if valid_token(t)]

        words_doc = Counter(tokens)
        bigrams_doc = Counter(generate_ngrams(tokens, n=2))
        trigrams_doc = Counter(generate_ngrams(tokens, n=3))

        word_counter.update(words_doc)
        bigram_counter.update(bigrams_doc)
        trigram_counter.update(trigrams_doc)

        doc_level_top.append({
            "document": doc_name,
            "top_words": words_doc.most_common(10),
            "top_bigrams": bigrams_doc.most_common(8),
            "top_trigrams": trigrams_doc.most_common(6)
        })

        print(f"Procesado: {doc_name}")

    write_counter_csv(word_counter, WORDS_CSV, top_n=300)
    write_counter_csv(bigram_counter, BIGRAMS_CSV, top_n=300)
    write_counter_csv(trigram_counter, TRIGRAMS_CSV, top_n=300)

    with open(SUMMARY_TXT, "w", encoding="utf-8") as f:
        f.write("DICTIONARY EXPANSION SUMMARY\n")
        f.write("=" * 70 + "\n\n")

        f.write("Top candidate words across the corpus\n")
        f.write("-" * 70 + "\n")
        for term, count in word_counter.most_common(50):
            f.write(f"{term}: {count}\n")

        f.write("\nTop candidate bigrams across the corpus\n")
        f.write("-" * 70 + "\n")
        for term, count in bigram_counter.most_common(50):
            f.write(f"{term}: {count}\n")

        f.write("\nTop candidate trigrams across the corpus\n")
        f.write("-" * 70 + "\n")
        for term, count in trigram_counter.most_common(50):
            f.write(f"{term}: {count}\n")

        f.write("\n" + "=" * 70 + "\n\n")
        f.write("Top terms by document\n\n")

        for row in doc_level_top:
            f.write(f"{row['document']}\n")
            f.write("  Top words:\n")
            for term, count in row["top_words"]:
                f.write(f"    - {term}: {count}\n")

            f.write("  Top bigrams:\n")
            for term, count in row["top_bigrams"]:
                f.write(f"    - {term}: {count}\n")

            f.write("  Top trigrams:\n")
            for term, count in row["top_trigrams"]:
                f.write(f"    - {term}: {count}\n")

            f.write("\n")

    print("\n===================================")
    print("Dictionary candidate files generated")
    print("Words:", WORDS_CSV)
    print("Bigrams:", BIGRAMS_CSV)
    print("Trigrams:", TRIGRAMS_CSV)
    print("Summary:", SUMMARY_TXT)
    print("===================================")


if __name__ == "__main__":
    main()