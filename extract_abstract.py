from collections import Counter
import csv
from pathlib import Path
import re
import sys

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from extract_keywords import read_xlsx_sheet
import settings as cfg


def ensure_nltk_resources() -> None:
    for resource in ("stopwords", "wordnet", "omw-1.4"):
        try:
            nltk.data.find(f"corpora/{resource}")
        except LookupError:
            nltk.download(resource, quiet=True)


def extract_terms_from_text(
    text: str,
    stop_words: set[str],
    lemmatizer: WordNetLemmatizer,
) -> list[str]:
    if not text:
        return []

    working = text
    extracted = []

    pattern_map = []
    for canonical, variants in cfg.COMPOUND_TERMS.items():
        for v in variants:
            pattern_map.append((v, canonical))
    pattern_map.sort(key=lambda x: len(x[0]), reverse=True)

    for variant, canonical in pattern_map:
        regex = re.compile(r"(?<!\w)" + re.escape(variant) + r"(?!\w)", re.IGNORECASE)
        matches = regex.findall(working)
        if matches:
            extracted.extend([canonical] * len(matches))
            working = regex.sub(" ", working)

    raw_tokens = re.findall(r"[A-Za-z][A-Za-z0-9\-]*", working)

    for tok in raw_tokens:
        clean_tok = tok.strip("-")
        if len(clean_tok) < 3:
            continue
        low = clean_tok.lower()
        if low in stop_words:
            continue

        lemma = lemmatizer.lemmatize(low, pos="n")
        if lemma in stop_words or len(lemma) < 3:
            continue

        formatted = lemma.title()
        formatted = cfg.ACRONYM_FIXES.get(formatted, formatted)
        if clean_tok.isupper() and len(clean_tok) <= 6:
            formatted = clean_tok
        extracted.append(formatted)

    return extracted


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
        abstract_text = r.get("abstract", "")
        terms = extract_terms_from_text(abstract_text, all_stops, lemmatizer)
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

    out_dir = Path(cfg.ABSTRACT_COUNTS_CSV).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(cfg.ABSTRACT_COUNTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["keyword", "count", "articles_count"])
        for kw, cnt in total_counts.most_common():
            writer.writerow([kw, cnt, doc_freq[kw]])

    with open(cfg.ABSTRACT_BY_ARTICLE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["ID", "author", "year", "title", "total_terms", "unique_terms", "top_terms"],
        )
        writer.writeheader()
        writer.writerows(article_records)

    print(f"Conferência da aba '{cfg.SHEET_NAME_ABSTRACT}' ({len(article_records)} artigos):")
    for rec in article_records:
        print(
            f"  [ID {str(rec['ID']):>2s}] {rec['author']:20s} ({rec['year']}) -> "
            f"{rec['total_terms']:3d} termos úteis ({rec['unique_terms']:2d} únicos)"
        )

    print(f"\nTotal de ocorrências extraídas (sem stopwords): {sum(total_counts.values())}")
    print(f"Total de termos distintos:                       {len(total_counts)}")
    print("\nTop 35 termos mais frequentes nos Abstracts:")
    for kw, cnt in total_counts.most_common(35):
        print(f"  {cnt:3d}x (em {doc_freq[kw]:2d} artigos) | {kw}")

    print("\nArquivos gerados:")
    print(f"  - {cfg.ABSTRACT_COUNTS_CSV}")
    print(f"  - {cfg.ABSTRACT_BY_ARTICLE_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
