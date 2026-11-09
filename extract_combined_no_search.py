"""Soma e consolida as contagens de Keywords + Abstract + Título (todos sem termos da string de busca)."""
from collections import Counter
import csv
from pathlib import Path
import sys

import settings as cfg


def read_counts_csv(path: str) -> dict[str, int]:
    """Lê um CSV de contagem (keyword, count) e retorna dicionário."""
    counts = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            kw = row["keyword"].strip()
            cnt = int(row["count"])
            if kw and cnt > 0:
                counts[kw] = counts.get(kw, 0) + cnt
    return counts


def main() -> int:
    kw_counts = read_counts_csv(cfg.KEYWORDS_NO_SEARCH_COUNTS_CSV)
    abs_counts = read_counts_csv(cfg.ABSTRACT_NO_SEARCH_COUNTS_CSV)
    tit_counts = read_counts_csv(cfg.TITLE_NO_SEARCH_COUNTS_CSV)

    # Mapeia chave em minúsculas -> nome canônico preferencial (priorizando Keywords > Title > Abstract)
    canonical_name = {}
    for source in (abs_counts, tit_counts, kw_counts):
        for k in source:
            canonical_name[k.lower()] = k

    total_counts = Counter()
    kw_by_canon = Counter()
    abs_by_canon = Counter()
    tit_by_canon = Counter()

    for k, v in kw_counts.items():
        c = canonical_name[k.lower()]
        kw_by_canon[c] += v
        total_counts[c] += v

    for k, v in abs_counts.items():
        c = canonical_name[k.lower()]
        abs_by_canon[c] += v
        total_counts[c] += v

    for k, v in tit_counts.items():
        c = canonical_name[k.lower()]
        tit_by_canon[c] += v
        total_counts[c] += v

    out_dir = Path(cfg.COMBINED_NO_SEARCH_COUNTS_CSV).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(cfg.COMBINED_NO_SEARCH_COUNTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["keyword", "count", "keywords_count", "abstract_count", "title_count"])
        for kw, cnt in total_counts.most_common():
            writer.writerow([
                kw,
                cnt,
                kw_by_canon[kw],
                abs_by_canon[kw],
                tit_by_canon[kw],
            ])

    print("Consolidação concluída (Keywords + Abstract + Título sem termos de busca):")
    print(f"  - Ocorrências de Keywords (sem busca): {sum(kw_counts.values())}")
    print(f"  - Ocorrências de Abstract (sem busca): {sum(abs_counts.values())}")
    print(f"  - Ocorrências de Títulos  (sem busca): {sum(tit_counts.values())}")
    print(f"  = Total combinado de ocorrências:      {sum(total_counts.values())}")
    print(f"  = Total de termos distintos:           {len(total_counts)}")

    print("\nTop 30 termos combinados (Keywords + Abstract + Título sem busca):")
    for kw, cnt in total_counts.most_common(30):
        print(
            f"  {cnt:3d}x (KW:{kw_by_canon[kw]:2d} | ABS:{abs_by_canon[kw]:2d} | TIT:{tit_by_canon[kw]:2d}) | {kw}"
        )

    print(f"\nArquivo salvo em: {cfg.COMBINED_NO_SEARCH_COUNTS_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
