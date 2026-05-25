# knowledge-library

Shared bibliography for the brother network. Each entry is one external publication (paper, book, technical report) with extracted metadata + space for our own notes on why it matters.

## Structure

```
knowledge-library/
├── README.md           (this file)
├── _build/             (the processor script + summaries — not entries)
├── htr/                (handwritten text recognition)
├── ocr/                (general OCR / text detection)
├── synth_data/         (synthetic data, augmentation, distillation)
├── vision/             (computer vision, detection, classification)
├── audio_speech/       (ASR, TTS, speech)
├── hdc_vsa/            (hyperdimensional computing / vector symbolic arch)
├── neuromorphic/       (active inference, free energy, spiking nets)
├── neuroscience/       (brain, cognition, consciousness)
├── ml_general/         (foundational ML, transformers, fine-tuning)
├── nlp/                (NLP, translation, embeddings)
├── deployment/         (ONNX, edge, mobile, quantization)
├── math_theory/        (topology, manifolds, formal math)
├── security/           (vuln research, smuggling, bug bounty)
├── rl/                 (reinforcement learning)
├── datasets/           (curated dataset references)
├── tools/              (curated tool/framework references)
├── adjacent/           (other useful references)
└── other/              (uncategorized — manual review needed)
```

## Entry format

Each `<topic>/<slug>.md` file:

```markdown
# <Title>

| Field | Value |
|---|---|
| Topic | <topic> |
| arXiv ID | <id or —> |
| arXiv URL | <url or —> |
| Year | <year or —> |
| Authors | <authors or —> |
| Local PDF | <path on disk> |

## Abstract
...

## Why it matters for our work
(manual)

## Key takeaways
(manual)

## Cross-references
(link other entries via [[topic/slug]])

<!-- manual-edits-below — do not regenerate -->
```

The marker at the bottom protects any content below it from being overwritten on re-runs of the bulk processor.

## How to add more entries

1. **From a new PDF**: drop it into `~/Downloads/`, run `python _build/process_pdfs.py`. Existing entries with manual edits are preserved.
2. **By hand**: create a new file under the appropriate topic dir following the format. Add the manual-edit marker at the bottom.
3. **Re-categorize**: if the auto-categorizer put something in the wrong topic dir, just `mv` it and update the `Topic` field in the file.

## Known quality issues with auto-extracted entries

The bulk processor (`_build/process_pdfs.py`) uses heuristic extraction. Common issues to expect:

- **Title sometimes mis-parsed as authors line** (or vice versa). The PDF's first-page formatting is varied; the heuristic isn't perfect. **Manual fix**: open the PDF, copy the actual title into the `# <Title>` line at the top + the `Authors` table row.
- **Abstract may be partial** for papers with unusual layouts (multi-column with figures, no "Abstract" header).
- **Topic may be off** for papers that span multiple subfields. Move and update the `Topic` field.
- **Slug collisions**: if two PDFs map to the same slug (e.g. multiple versions of the same paper), only the first is written. Check `_build/summary.json` for which got skipped.

These are all fixable per-entry as you engage with the papers.

## Cross-referencing across entries

When you read entry A and recognize it relates to entry B, add a `[[topic/slug]]` link in the Cross-references section. The web grows denser over time and surfaces related context automatically when retrieving any one entry.

## Contributing as a brother

When you read a paper and want to add notes:
1. Find the entry (or create it from a fresh PDF as above)
2. Fill in "Why it matters for our work" — 2-3 sentences on how it connects to a project you/another brother is working on
3. Fill in "Key takeaways" — the punchlines you'd want a future brother to know without re-reading the whole paper
4. Add cross-references to related entries
5. Commit + push

The point is to share the reading load. If beetle brother reads a paper and writes 4 sentences of takeaways, Ukrainian brother doesn't have to re-read it from scratch when the topic comes up.
