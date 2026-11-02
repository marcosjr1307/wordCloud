from collections import Counter
import csv
from pathlib import Path
import sys

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from extract_abstract import ensure_nltk_resources, extract_terms_from_text
from extract_keywords import read_xlsx_sheet
import settings as cfg


def main() -> int:
    ensure_nltk_resources()
    nltk_stops = set(stopwords.words("english"))
    all_stops = nltk_stops | {w.lower() for w in cfg.CUSTOM_STOPWORDS}
    lemmatizer = WordNetLemmatizer()

    rows = read_xlsx_sheet(cfg.XLSX_PATH, cfg.SHEET_NAME_TITLE)
    if not rows:
        print(f"Nenhum dado encontrado em {cfg.XLSX_PATH} (aba '{cfg.SHEET_NAME_TITLE}').")
        return 1

    total_counts = Counter()
    doc_freq = Counter()
    article_records = []

    for idx, r in enumerate(rows, 1):
        title_text = r.get("title", "")
        terms = extract_terms_from_text(title_text, all_stops, lemmatizer)
        total_counts.update(terms)
        doc_freq.update(set(terms))

        article_records.append({
            "ID": r.get("ID", idx),
            "author": r.get("author", ""),
            "year": int(float(r["year"])) if r.get("year") else "",
            "title": title_text,
            "num_terms": len(terms),
            "extracted_terms": "; ".join(terms),
        })

    out_dir = Path(cfg.TITLE_COUNTS_CSV).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(cfg.TITLE_COUNTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["keyword", "count", "articles_count"])
        for kw, cnt in total_counts.most_common():
            writer.writerow([kw, cnt, doc_freq[kw]])

    with open(cfg.TITLE_BY_ARTICLE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["ID", "author", "year", "title", "num_terms", "extracted_terms"],
        )
        writer.writeheader()
        writer.writerows(article_records)

    print(f"Conferência dos Títulos ({len(article_records)} artigos):")
    for rec in article_records:
        print(
            f"  [ID {str(rec['ID']):>2s}] {rec['author']:20s} ({rec['year']}) -> "
            f"{rec['num_terms']:2d} termos: {rec['extracted_terms']}"
        )

    print(f"\nTotal de ocorrências extraídas dos Títulos: {sum(total_counts.values())}")
    print(f"Total de termos distintos:                  {len(total_counts)}")
    print("\nTop termos mais frequentes nos Títulos (frequência >= 2):")
    for kw, cnt in total_counts.most_common():
        if cnt < 2:
            break
        print(f"  {cnt:2d}x (em {doc_freq[kw]:2d} artigos) | {kw}")

    print("\nArquivos gerados:")
    print(f"  - {cfg.TITLE_COUNTS_CSV}")
    print(f"  - {cfg.TITLE_BY_ARTICLE_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
