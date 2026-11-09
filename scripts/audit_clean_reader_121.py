#!/usr/bin/env python3
"""Read-only integrity check for the book's reader-facing edition 1.2.1."""
from pathlib import Path
import argparse
import json
import re
import subprocess
import zipfile
import xml.etree.ElementTree as ET
from publication_config import ROOT, source_inputs

RELEASE = ROOT / "dist/v1.2.1"
STEM = "Caesar_Augustus_v1.2.1"
BAD = re.compile(r"(?:[Вв]ерси[яиюеы]+\s*1\.(?:1|2)(?!\d)|[Рр]едакци[яиюеи]+\s*1\.(?:1|2)(?!\d)|[Рр]абочая\s+редакция|[Нн]аучная\s+редакция\s*1\.2|\b(?:ChatGPT|Codex|GPT-?[456])\b)", re.I)

def ensure(condition, what):
    if not condition:
        raise SystemExit("Reader edition 1.2.1 audit failed: " + what)

def visible_markdown(s):
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"!\[([^]]*)\]\([^)]+\)(?:\{[^}]*\})?", r"\1", s)
    return s

def check(label, text):
    hit = BAD.search(text)
    ensure(hit is None, label + " contains " + (hit.group(0) if hit else ""))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sources-only", action="store_true")
    a = ap.parse_args()
    inputs = source_inputs()
    ensure(len(inputs) >= 20, "expected 16 chapters plus introduction, conclusion, appendices, bibliography")
    captions = 0
    disclosures = 0
    for path in inputs:
        raw = path.read_text(encoding="utf-8")
        captions += raw.count("assets/illustrations/v1.1/")
        txt = visible_markdown(raw)
        disclosures += txt.count("Инструменты ИИ использовались также")
        check(path.relative_to(ROOT).as_posix(), txt)
    ensure(captions == 34, "expected 34 illustrations, got " + str(captions))
    ensure(disclosures == 1, "expected exactly one transparent editorial AI disclosure")
    meta = (ROOT / "manuscript/metadata.yaml").read_text(encoding="utf-8")
    check("book metadata", meta)
    ensure("Рабочая исследовательская рукопись" not in meta, "draft rights metadata remain")
    result = {"release":"1.2.1","manuscript_files":len(inputs),"illustrations":captions,
              "single_disclosure":disclosures == 1,"reader_metadata_clean":True}
    if a.sources_only:
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return
    for ext in ("docx", "epub", "pdf"):
        ensure((RELEASE / (STEM + "." + ext)).is_file(), "missing " + ext)
    docx = RELEASE / (STEM + ".docx")
    with zipfile.ZipFile(docx) as z:
        xmlfiles = [n for n in z.namelist() if n.startswith("word/") and n.endswith(".xml") and any(t in n for t in ("document","header","footnotes"))]
        texts = []
        for name in xmlfiles:
            root = ET.fromstring(z.read(name))
            texts.append(" ".join((node.text or "") for node in root.iter() if node.tag.endswith("}t")))
        check("DOCX visible text", " ".join(texts))
    epub = RELEASE / (STEM + ".epub")
    with zipfile.ZipFile(epub) as z:
        items = []
        for name in z.namelist():
            if name.endswith((".xhtml",".opf",".ncx")):
                root = ET.fromstring(z.read(name))
                items.append(" ".join(t for t in root.itertext() if t))
        check("EPUB visible text and metadata", " ".join(items))
    pdf = RELEASE / (STEM + ".pdf")
    pdftext = subprocess.run(["pdftotext",str(pdf),"-"],check=True,capture_output=True,text=True).stdout
    check("PDF extracted text", pdftext)
    ensure("Цезарь и Август" in pdftext, "PDF text unavailable")
    result.update({"docx":"pass","epub":"pass","pdf":"pass"})
    (RELEASE / "reader_audit.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__ == "__main__":
    main()
