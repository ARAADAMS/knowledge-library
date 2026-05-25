#!/usr/bin/env python3
"""Process ~/Downloads/*.pdf into knowledge-library/<topic>/<slug>.md entries.

Per-PDF: extract title + authors + abstract from first 1-2 pages,
arxiv ID from filename or text, categorize by keyword matching against
topic taxonomy, write structured markdown entry.

Designed to be run idempotently — won't overwrite existing entries that
have been manually edited (checks for a "## Manual edits" marker).
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

import pypdfium2 as pdfium


DOWNLOADS = Path("/home/croft/Downloads")
LIBRARY = Path("/home/croft/user/knowledge-library")

# Topic taxonomy + keywords for auto-categorization. First-match wins.
# Order matters — more specific topics before more general ones.
TOPICS = {
    "htr": [
        "handwritten text recognition", "htr ", "kraken", "transkribus",
        "kurrent", "palaeography", "manuscript transcription", "historical document",
        "iam database", "rimes ", "bentham", "saint-gall",
    ],
    "ocr": [
        "ocr ", "optical character recognition", "text detection", "scene text",
        "doctr", "paddleocr", "trocr", "scribbling", "text spotting",
    ],
    "synth_data": [
        "synthetic data", "data augmentation", "elastic distortion",
        "generative augmentation", "domain randomization", "noisy student",
        "self-training", "pseudo-label", "knowledge distillation",
    ],
    "vision": [
        "image classification", "object detection", "semantic segmentation",
        "vision transformer", " vit ", "imagenet", "convolutional neural",
        "yolo", "image super-resolution",
    ],
    "audio_speech": [
        "speech recognition", "speech synthesis", "text-to-speech", "asr ",
        "wav2vec", "whisper", "spectrogram", "audio classification",
        "voice cloning", "fish speech",
    ],
    "hdc_vsa": [
        "hyperdimensional", "vector symbolic", " vsa ", " hdc ", "hypervector",
        "binding operation", "holographic reduced representation", "resonator network",
    ],
    "neuromorphic": [
        "active inference", "free energy principle", "predictive coding",
        "spiking neural", "neuromorphic", "loihi", " snn ",
        "biologically plausible", "hebbian",
    ],
    "ml_general": [
        "transformer", "attention is all", "self-attention",
        "fine-tuning", "transfer learning", "in-context learning",
        "lora", "adapter", "low-rank", "rlhf", "ppo ", "dpo ",
        "language model", "foundation model", "pre-training",
    ],
    "nlp": [
        "natural language", "machine translation", "named entity",
        "tokenization", "sentence embedding", "cross-lingual",
        "multilingual model", " bleu ", "translation",
    ],
    "deployment": [
        "onnx", "quantization", "edge deployment", "mobile inference",
        "embedded systems", "model compression", "pruning", "distillation",
        "tensorrt", "openvino", "tflite",
    ],
    "math_theory": [
        "topology", "manifold", "ricci flow", "geometric deep learning",
        "category theory", "algebraic", "homotopy", "sheaf",
        "millennium problem", "riemann", "navier-stokes",
        "complexity theory", "p versus np", "yang-mills",
    ],
    "security": [
        "vulnerability", "exploit", "smuggling", "request smuggling",
        "bug bounty", "penetration testing", "adversarial attack",
        "side channel", "cryptography",
    ],
    "neuroscience": [
        "brain", "cortex", "neuron", "synaptic", "neural circuit",
        "consciousness", "cognitive architecture", "hippocampus",
        "prefrontal", "oscillation",
    ],
    "rl": [
        "reinforcement learning", "policy gradient", "q-learning",
        "actor-critic", "ppo", "trpo", "world model", "model-based rl",
    ],
}


ARXIV_RE = re.compile(r"(\d{4}\.\d{4,5})(v\d+)?", re.IGNORECASE)
ARXIV_FILENAME_RE = re.compile(r"^(\d{4}\.\d{4,5})(v\d+)?\.pdf$", re.IGNORECASE)


def safe_slug(s: str, maxlen: int = 80) -> str:
    """Filename-safe slug."""
    s = re.sub(r"[^a-zA-Z0-9._-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_-.")
    return s[:maxlen].lower()


def extract_first_pages(pdf_path: Path, max_pages: int = 2) -> str:
    """Get first N pages of text via pypdfium2."""
    try:
        doc = pdfium.PdfDocument(str(pdf_path))
        out = []
        for i, page in enumerate(doc):
            if i >= max_pages:
                break
            try:
                txt = page.get_textpage().get_text_range()
                out.append(txt)
            except Exception:
                pass
        return "\n".join(out)
    except Exception as e:
        return ""


def parse_metadata(text: str, filename: str) -> dict:
    """Pull title + authors + abstract + arxiv ID from extracted text."""
    md = {"title": "", "authors": "", "abstract": "", "arxiv_id": "", "year": ""}

    # arxiv ID from filename first
    m = ARXIV_FILENAME_RE.match(filename)
    if m:
        md["arxiv_id"] = m.group(1)
        # arxiv YYMM → year
        try:
            yy = int(md["arxiv_id"][:2])
            md["year"] = str(2000 + yy if yy < 90 else 1900 + yy)
        except Exception:
            pass
    else:
        m = ARXIV_RE.search(text[:1000])
        if m:
            md["arxiv_id"] = m.group(1)
            try:
                yy = int(md["arxiv_id"][:2])
                md["year"] = str(2000 + yy if yy < 90 else 1900 + yy)
            except Exception:
                pass

    # Title: usually one of the first non-empty lines, often the longest
    # among the first 10 lines (heuristic).
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()][:15]
    if lines:
        # Skip arxiv ID lines and page numbers
        candidates = [ln for ln in lines if not (
            re.match(r"^arxiv:", ln, re.I) or
            re.match(r"^\d+$", ln) or
            re.match(r"^[A-Z]\d", ln) or
            len(ln) < 8
        )]
        if candidates:
            # Pick the longest candidate from the first 5 (likely title)
            md["title"] = max(candidates[:5], key=len)[:200]

    # Authors: usually right after title
    if md["title"]:
        try:
            idx = text.find(md["title"])
            if idx >= 0:
                after = text[idx + len(md["title"]):idx + len(md["title"]) + 500]
                # First substantive line after title
                for ln in after.split("\n"):
                    ln = ln.strip()
                    if ln and len(ln) > 3 and not ln.lower().startswith("abstract"):
                        md["authors"] = ln[:300]
                        break
        except Exception:
            pass

    # Abstract: text after "Abstract" keyword
    abstract_match = re.search(r"abstract\s*[—–.\-:]?\s*(.+?)(?=\n\s*\n|\n[A-Z][a-z]+ Introduction|index terms)",
                               text, re.IGNORECASE | re.DOTALL)
    if abstract_match:
        ab = re.sub(r"\s+", " ", abstract_match.group(1)).strip()
        md["abstract"] = ab[:1500]

    return md


def categorize(text: str, title: str) -> str:
    """Pick topic by keyword density in first-page text + title."""
    haystack = (title + " " + text[:3000]).lower()
    scores = {}
    for topic, keywords in TOPICS.items():
        score = sum(haystack.count(kw) for kw in keywords)
        if score > 0:
            scores[topic] = score
    if not scores:
        return "other"
    return max(scores.items(), key=lambda kv: kv[1])[0]


MANUAL_EDIT_MARKER = "<!-- manual-edits-below — do not regenerate -->"


def write_entry(out_path: Path, md: dict, pdf_path: Path, topic: str) -> bool:
    """Write entry. If file exists AND has manual edits, skip (return False)."""
    if out_path.exists():
        existing = out_path.read_text(encoding="utf-8", errors="replace")
        if MANUAL_EDIT_MARKER in existing:
            return False  # don't clobber manual edits

    rel_pdf = str(pdf_path)
    arxiv_url = f"https://arxiv.org/abs/{md['arxiv_id']}" if md["arxiv_id"] else ""

    content = f"""# {md['title'] or pdf_path.stem}

| Field | Value |
|---|---|
| Topic | {topic} |
| arXiv ID | {md['arxiv_id'] or '—'} |
| arXiv URL | {arxiv_url or '—'} |
| Year | {md['year'] or '—'} |
| Authors | {md['authors'] or '—'} |
| Local PDF | `{rel_pdf}` |

## Abstract

{md['abstract'] or '_(not auto-extracted — open PDF to read)_'}

## Why it matters for our work

_(empty — add notes here when you've engaged with this paper)_

## Key takeaways

_(empty — add notes here)_

## Cross-references

_(link related entries via `[[topic/slug]]`)_

{MANUAL_EDIT_MARKER}
"""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    return True


def main():
    pdfs = sorted(DOWNLOADS.glob("*.pdf"))
    print(f"Found {len(pdfs)} PDFs in {DOWNLOADS}")

    written = 0
    skipped_manual = 0
    by_topic: dict[str, int] = {}
    summary_rows = []

    for i, pdf in enumerate(pdfs, 1):
        text = extract_first_pages(pdf)
        if len(text) < 50:
            # Skip if we couldn't extract anything (scanned PDFs, etc.)
            print(f"[{i:3d}/{len(pdfs)}] SKIP (no text): {pdf.name}")
            continue

        md = parse_metadata(text, pdf.name)
        topic = categorize(text, md["title"])

        slug = md["arxiv_id"] or safe_slug(md["title"] or pdf.stem)
        out_path = LIBRARY / topic / f"{slug}.md"

        ok = write_entry(out_path, md, pdf, topic)
        if not ok:
            skipped_manual += 1
            print(f"[{i:3d}/{len(pdfs)}] KEEP (manual): {pdf.name} → {topic}/{slug}.md")
            continue

        written += 1
        by_topic[topic] = by_topic.get(topic, 0) + 1
        summary_rows.append({
            "pdf": pdf.name,
            "topic": topic,
            "slug": slug,
            "title": md["title"][:80],
            "arxiv_id": md["arxiv_id"],
        })
        if i % 20 == 0 or i == len(pdfs):
            print(f"[{i:3d}/{len(pdfs)}] {pdf.name} → {topic}/{slug}.md")

    # Build per-topic README listing entries
    for topic in by_topic:
        topic_dir = LIBRARY / topic
        entries = sorted(topic_dir.glob("*.md"))
        entries = [e for e in entries if e.name != "README.md"]
        readme = topic_dir / "README.md"
        lines = [f"# {topic.replace('_', ' ').title()}", "",
                 f"{len(entries)} entries.", ""]
        for e in entries:
            first_line = e.read_text(encoding='utf-8', errors='replace').split('\n')[0].lstrip('# ').strip()
            lines.append(f"- [{first_line}]({e.name})")
        readme.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Top-level summary
    (LIBRARY / "_build" / "summary.json").write_text(
        json.dumps({"by_topic": by_topic, "total_written": written,
                    "total_kept_manual": skipped_manual,
                    "rows": summary_rows}, indent=2)
    )

    print(f"\nDONE.  Written: {written}.  Kept (manual edits): {skipped_manual}.")
    print(f"By topic:")
    for topic, n in sorted(by_topic.items(), key=lambda kv: -kv[1]):
        print(f"  {topic:18s} {n}")


if __name__ == "__main__":
    main()
