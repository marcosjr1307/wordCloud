from collections import Counter
import csv
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

import settings as cfg


def read_xlsx_sheet(xlsx_path: str, sheet_name: str) -> list[dict[str, str]]:
    ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(xlsx_path) as z:
        wb = ET.fromstring(z.read("xl/workbook.xml"))
        sheets = [
            (s.attrib["name"], idx)
            for idx, s in enumerate(wb.findall(".//main:sheet", ns), 1)
        ]
        sheet_idx = next((idx for name, idx in sheets if name == sheet_name), 1)

        ss_xml = ET.fromstring(z.read("xl/sharedStrings.xml"))
        shared = [
            "".join(t.text or "" for t in si.findall(".//main:t", ns))
            for si in ss_xml.findall("main:si", ns)
        ]

        s_xml = ET.fromstring(z.read(f"xl/worksheets/sheet{sheet_idx}.xml"))
        rows_data = []
        headers = {}

        for r_idx, row in enumerate(s_xml.findall(".//main:row", ns)):
            row_cells = {}
            for c in row.findall("main:c", ns):
                ref = c.attrib.get("r", "")
                col = "".join(ch for ch in ref if ch.isalpha())
                t = c.attrib.get("t")
                v = c.find("main:v", ns)
                val = v.text if v is not None else ""
                if t == "s" and val != "":
                    val = shared[int(val)]
                row_cells[col] = val.strip()

            if r_idx == 0:
                headers = {col: name for col, name in row_cells.items() if name}
            else:
                if not any(row_cells.values()):
                    continue
                record = {
                    headers.get(col, col): row_cells.get(col, "")
                    for col in headers
                }
                if record.get("author") or record.get("title"):
                    rows_data.append(record)

        return rows_data


def normalize_keyword(kw: str) -> str:
    kw = " ".join(kw.strip().split())
    if not kw:
        return ""
    kw = cfg.ACRONYM_FIXES.get(kw, kw)
    if cfg.MERGE_ALIASES:
        for canonical, aliases in cfg.KEYWORD_ALIASES.items():
            if kw in aliases:
                return canonical
    return kw


def main() -> int:
    rows = read_xlsx_sheet(cfg.XLSX_PATH, cfg.SHEET_NAME)
    if not rows:
        print(f"Nenhum dado encontrado em {cfg.XLSX_PATH} (aba '{cfg.SHEET_NAME}').")
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

    out_dir = Path(cfg.KEYWORDS_COUNTS_CSV).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(cfg.KEYWORDS_COUNTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["keyword", "count"])
        for kw, cnt in counts.most_common():
            writer.writerow([kw, cnt])

    with open(cfg.KEYWORDS_BY_ARTICLE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["ID", "author", "year", "title", "num_keywords", "keywords"],
        )
        writer.writeheader()
        writer.writerows(article_records)

    print(f"Resumo por artigo ({len(article_records)} artigos):")
    for rec in article_records:
        print(
            f"  [{rec['ID']:2d}] {rec['author']} ({rec['year']}) -> "
            f"{rec['num_keywords']} keywords"
        )

    print(f"\nTotal de ocorrências de keywords: {len(all_keywords)}")
    print(f"Total de keywords distintas:      {len(counts)}")
    print("\nTop keywords (frequência >= 2):")
    for kw, cnt in counts.most_common():
        if cnt < 2:
            break
        print(f"  {cnt:2d}x | {kw}")

    print(f"\nArquivos gerados:")
    print(f"  - {cfg.KEYWORDS_COUNTS_CSV}")
    print(f"  - {cfg.KEYWORDS_BY_ARTICLE_CSV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
