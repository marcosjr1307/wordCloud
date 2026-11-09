from collections import Counter
import csv
from pathlib import Path
import re
import sys

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from extract_abstract import ensure_nltk_resources, extract_terms_from_text
from extract_keywords import read_xlsx_sheet
import settings as cfg


def strip_search_phrases(text: str) -> str:
    working = text
    for pat in cfg.SEARCH_PHRASES_REGEX:
        working = re.sub(r"(?<!\w)" + pat + r"(?!\w)", " ", working, flags=re.IGNORECASE)
    return working


def filter_search_terms(terms: list[str]) -> list[str]:
    remove_lower = {t.lower() for t in cfg.TEXT_SEARCH_TERMS_REMOVE}
    return [t for t in terms if t.lower() not in remove_lower]


def main() -> int:
    ensure_nltk_resources()
    nltk_stops = set(stopwords.words("english"))
    all_stops = nltk_stops | {w.lower() for w in cfg.CUSTOM_STOPWORDS}
    lemmatizer = WordNetLemmatizer()

    rows = read_xlsx_sheet(cfg.XLSX_PATH, cfg.SHEET_NAME_ABSTRACT)
    if not rows:
        print(f"Nenhum dado encontrado em {cfg.XLSX_PATH} (aba '{cfg.SHEET_NAME_ABSTRACT}').")
        return 1

    total_counts = Counter()
    doc_freq = Counter()
    article_records = []

    for idx, r in enumerate(rows, 1):
        abstract_text = strip_search_phrases(r.get("abstract", ""))
        raw_terms = extract_terms_from_text(abstract_text, all_stops, lemmatizer)
        terms = filter_search_terms(raw_terms)

        total_counts.update(terms)
        doc_freq.update(set(terms))

        top_art = ", ".join(f"{w} ({c})" for w, c in Counter(terms).most_common(8))
        article_records.append({
            "ID": r.get("ID", idx),
            "author": r.get("author", ""),
            "year": int(float(r["year"])) if r.get("year") else "",
            "title": r.get("title", ""),
            "total_terms": len(terms),
            "unique_terms": len(set(terms)),
            "top_terms": top_art,
        })

    out_dir = Path(cfg.ABSTRACT_NO_SEARCH_COUNTS_CSV).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(cfg.ABSTRACT_NO_SEARCH_COUNTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["keyword", "count", "articles_count"])
        for kw, cnt in total_counts.most_common():
            writer.writerow([kw, cnt, doc_freq[kw]])

    with open(cfg.ABSTRACT_NO_SEARCH_BY_ARTICLE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["ID", "author", "year", "title", "total_terms", "unique_terms", "top_terms"],
        )
        writer.writeheader()
        writer.writerows(article_records)

    print(f"Total de ocorrências nos Abstracts (sem termos de busca): {sum(total_counts.values())}")
    print(f"Total de termos distintos:                                {len(total_counts)}")
    print("\nTop 30 termos nos Abstracts (sem termos de busca):")
    for kw, cnt in total_counts.most_common(30):
        print(f"  {cnt:3d}x (em {doc_freq[kw]:2d} artigos) | {kw}")

    print("\nArquivos gerados:")
    print(f"  - {cfg.ABSTRACT_NO_SEARCH_COUNTS_CSV}")
    print(f"  - {cfg.ABSTRACT_NO_SEARCH_BY_ARTICLE_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
