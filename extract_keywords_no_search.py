from collections import Counter
import csv
from pathlib import Path
import sys

from extract_keywords import normalize_keyword, read_xlsx_sheet
import settings as cfg


def main() -> int:
    rows = read_xlsx_sheet(cfg.XLSX_PATH, cfg.SHEET_NAME_NO_SEARCH)
    if not rows:
        print(f"Nenhum dado encontrado em {cfg.XLSX_PATH} (aba '{cfg.SHEET_NAME_NO_SEARCH}').")
        return 1

    kw_cols = [c for c in rows[0].keys() if c.lower().startswith("keyword")]

    all_keywords = []
    article_records = []

    for idx, r in enumerate(rows, 1):
        art_kws = []
        for col in kw_cols:
            raw_kw = r.get(col, "")
            norm_kw = normalize_keyword(raw_kw)
            if norm_kw:
                art_kws.append(norm_kw)
                all_keywords.append(norm_kw)

        article_records.append({
            "ID": idx,
            "author": r.get("author", ""),
            "year": int(float(r["year"])) if r.get("year") else "",
            "title": r.get("title", ""),
            "num_keywords": len(art_kws),
            "keywords": "; ".join(art_kws),
        })

    counts = Counter(all_keywords)

    out_dir = Path(cfg.KEYWORDS_NO_SEARCH_COUNTS_CSV).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(cfg.KEYWORDS_NO_SEARCH_COUNTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["keyword", "count"])
        for kw, cnt in counts.most_common():
            writer.writerow([kw, cnt])

    with open(cfg.KEYWORDS_NO_SEARCH_BY_ARTICLE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["ID", "author", "year", "title", "num_keywords", "keywords"],
        )
        writer.writeheader()
        writer.writerows(article_records)

    print(f"Resumo por artigo ({len(article_records)} artigos) - Aba '{cfg.SHEET_NAME_NO_SEARCH}':")
    for rec in article_records:
        print(
            f"  [{rec['ID']:2d}] {rec['author']} ({rec['year']}) -> "
            f"{rec['num_keywords']} keywords"
        )

    print(f"\nTotal de ocorrências de keywords (sem termos de busca): {len(all_keywords)}")
    print(f"Total de keywords distintas:                            {len(counts)}")
    print("\nTop keywords (frequência >= 2):")
    for kw, cnt in counts.most_common():
        if cnt < 2:
            break
        print(f"  {cnt:2d}x | {kw}")

    print("\nArquivos gerados:")
    print(f"  - {cfg.KEYWORDS_NO_SEARCH_COUNTS_CSV}")
    print(f"  - {cfg.KEYWORDS_NO_SEARCH_BY_ARTICLE_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
