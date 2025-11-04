#!/usr/bin/env python3
"""
Markdown Content Deduplication CLI

Scans a directory for .md files, normalizes content, detects exact duplicates,
near-duplicates, and overlapping sections, and writes Markdown + JSON reports.

Usage example:
  python tools/dedup/dedupe.py \
    --root "/Users/behar/.cursor/worktrees/Private___Shared/cOk94/Job Interviews bb835cda4c474a6a8757788f7d0fe705" \
    --min-sim 0.80 --overlap-sim 0.85 \
    --out-md reports/dedupe-report.md --out-json reports/dedupe-report.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


# ------------------------------
# Model structures
# ------------------------------

@dataclass
class FileRecord:
    path: Path
    raw_text: str
    normalized_text: str
    content_hash: str
    shingles_3: Set[str]
    word_counts: Counter
    sections: List["SectionBlock"] = field(default_factory=list)


@dataclass
class SectionBlock:
    file_path: Path
    heading_breadcrumb: str
    block_text: str  # normalized block text
    index_in_file: int
    shingles_3: Set[str] = field(default_factory=set)
    word_counts: Counter = field(default_factory=Counter)


# ------------------------------
# Normalization utilities
# ------------------------------

def strip_frontmatter(text: str) -> str:
    # YAML frontmatter delimited by --- at top
    if text.startswith("---\n"):
        # Find the next line with --- that ends the frontmatter
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + len("\n---\n"):]
        # Also consider if file ends right after ---
        end2 = text.find("\n---\r\n", 4)
        if end2 != -1:
            return text[end2 + len("\n---\r\n"):]
    return text


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def strip_trailing_spaces(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.split("\n"))


def collapse_blank_lines(text: str) -> str:
    # Replace 3+ blank lines with 2, then 2 with 1
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def standardize_list_markers(text: str) -> str:
    lines = []
    for line in text.split("\n"):
        # Convert '* ' and '+ ' bullets to '- '
        if re.match(r"^[ \t]*[\*\+][ \t]+", line):
            line = re.sub(r"^[ \t]*[\*\+][ \t]+", "- ", line)
        # Normalize multiple spaces after '-' to single space
        if re.match(r"^[ \t]*-[ \t]+", line):
            line = re.sub(r"^[ \t]*-[ \t]+", "- ", line)
        lines.append(line)
    return "\n".join(lines)


def remove_code_fences(text: str) -> str:
    # Optionally remove fenced code blocks to focus on prose
    # We'll retain inline code. Remove triple-backtick fenced blocks.
    fenced_pattern = re.compile(r"```[\s\S]*?```", re.MULTILINE)
    return fenced_pattern.sub("\n", text)


def normalize_markdown(text: str, strip_fences: bool = True) -> str:
    text = normalize_newlines(text)
    text = strip_frontmatter(text)
    if strip_fences:
        text = remove_code_fences(text)
    text = standardize_list_markers(text)
    text = strip_trailing_spaces(text)
    text = collapse_blank_lines(text)
    # Collapse repeated whitespace to single spaces per line for stability
    text = "\n".join(re.sub(r"\s+", " ", line).strip() for line in text.split("\n"))
    return text.strip()


# ------------------------------
# Text similarity utilities
# ------------------------------

def make_char_ngrams(text: str, n: int = 3) -> Set[str]:
    if not text:
        return set()
    s = text.lower()
    s = re.sub(r"\s+", " ", s)
    if len(s) < n:
        return {s}
    return {s[i : i + n] for i in range(0, len(s) - n + 1)}


def tokenize_words(text: str) -> List[str]:
    # Simple word tokenizer suitable for Spanish/English
    return re.findall(r"[\p{L}\p{N}]+" if _HAS_REGEX_UNICODE else r"[A-Za-z0-9À-ÿ]+", text.lower())


def word_count(text: str) -> Counter:
    return Counter(tokenize_words(text))


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    if union == 0:
        return 0.0
    return inter / union


def cosine_from_counts(a: Counter, b: Counter) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    # dot product
    dot = 0.0
    for k, v in a.items():
        if k in b:
            dot += v * b[k]
    if dot == 0:
        return 0.0
    norm_a = math.sqrt(sum(v * v for v in a.values()))
    norm_b = math.sqrt(sum(v * v for v in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot) / (norm_a * norm_b)


# ------------------------------
# Markdown parsing (sections/paragraphs)
# ------------------------------

HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<title>.+?)\s*$")
LIST_ITEM_RE = re.compile(r"^[ \t]*-[ \t]+.+")


def extract_blocks(text: str, file_path: Path) -> List[SectionBlock]:
    lines = text.split("\n")
    heading_stack: List[str] = []
    blocks: List[SectionBlock] = []
    current_lines: List[str] = []
    current_is_list = False

    def flush_block():
        nonlocal current_lines, current_is_list
        if not current_lines:
            return
        block_text = "\n".join(current_lines).strip()
        block_text = re.sub(r"\s+", " ", block_text).strip()
        if len(block_text) < 40:
            # Ignore very short blocks (noise)
            current_lines = []
            current_is_list = False
            return
        breadcrumb = " / ".join(heading_stack) if heading_stack else "(no heading)"
        idx = len(blocks)
        block = SectionBlock(
            file_path=file_path,
            heading_breadcrumb=breadcrumb,
            block_text=block_text,
            index_in_file=idx,
        )
        block.shingles_3 = make_char_ngrams(block.block_text, 3)
        block.word_counts = word_count(block.block_text)
        blocks.append(block)
        current_lines = []
        current_is_list = False

    for raw_line in lines:
        line = raw_line.strip()
        m = HEADING_RE.match(raw_line)
        if m:
            # Flush existing block before changing heading context
            flush_block()
            level = len(m.group("hashes"))
            title = m.group("title").strip()
            # Update heading breadcrumb stack
            heading_stack = heading_stack[: level - 1]
            heading_stack.append(title)
            continue

        if line == "":
            # Blank line -> boundary between paragraphs
            flush_block()
            continue

        if LIST_ITEM_RE.match(raw_line):
            if not current_is_list:
                # Starting a list block; flush any pending paragraph
                flush_block()
                current_is_list = True
            current_lines.append(line)
            continue

        # Regular paragraph line
        if current_is_list:
            # List ended when a non-list line appears
            flush_block()
        current_lines.append(line)

    # Flush last block
    flush_block()

    return blocks


# ------------------------------
# Scanner and record builder
# ------------------------------

def iter_markdown_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*.md"):
        if p.is_file():
            yield p


def read_text_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Fallback to latin-1 and then decode to utf-8 best-effort
        with path.open("rb") as f:
            data = f.read()
        try:
            return data.decode("latin-1")
        except Exception:
            return data.decode("utf-8", errors="ignore")


def build_file_record(path: Path) -> FileRecord:
    raw = read_text_file(path)
    normalized = normalize_markdown(raw)
    content_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    shingles = make_char_ngrams(normalized, 3)
    wc = word_count(normalized)
    rec = FileRecord(
        path=path,
        raw_text=raw,
        normalized_text=normalized,
        content_hash=content_hash,
        shingles_3=shingles,
        word_counts=wc,
    )
    rec.sections = extract_blocks(normalized, path)
    return rec


# ------------------------------
# Duplicate detection
# ------------------------------

def group_exact_duplicates(records: List[FileRecord]) -> List[List[FileRecord]]:
    by_hash: Dict[str, List[FileRecord]] = defaultdict(list)
    for r in records:
        by_hash[r.content_hash].append(r)
    clusters = [lst for lst in by_hash.values() if len(lst) > 1]
    return clusters


def compute_near_duplicates(
    records: List[FileRecord], min_sim: float
) -> Tuple[List[Tuple[int, int, float, float]], List[List[int]]]:
    """
    Returns:
      pairs: list of (i, j, jaccard, cosine)
      components: list of connected components (list of indices) based on threshold
    """
    n = len(records)
    pairs: List[Tuple[int, int, float, float]] = []
    adj: Dict[int, Set[int]] = defaultdict(set)
    for i in range(n):
        for j in range(i + 1, n):
            r1, r2 = records[i], records[j]
            jac = jaccard(r1.shingles_3, r2.shingles_3)
            cos = 0.0
            if jac >= min_sim or (0.60 <= jac < min_sim):
                cos = cosine_from_counts(r1.word_counts, r2.word_counts)
            # Decision: accept if jac >= min_sim OR (jac in [0.6, min_sim) and cos >= min_sim)
            accept = jac >= min_sim or (0.60 <= jac < min_sim and cos >= min_sim)
            if accept:
                pairs.append((i, j, jac, cos))
                adj[i].add(j)
                adj[j].add(i)

    # Connected components
    visited: Set[int] = set()
    components: List[List[int]] = []
    for i in range(n):
        if i in visited or i not in adj:
            continue
        stack = [i]
        comp = []
        visited.add(i)
        while stack:
            node = stack.pop()
            comp.append(node)
            for nb in adj[node]:
                if nb not in visited:
                    visited.add(nb)
                    stack.append(nb)
        components.append(sorted(comp))

    return pairs, components


def detect_overlapping_sections(
    records: List[FileRecord], overlap_sim: float, max_pairs: int
) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    # Build all blocks with file index
    blocks: List[Tuple[int, SectionBlock]] = []
    for idx, rec in enumerate(records):
        for block in rec.sections:
            blocks.append((idx, block))

    # Compare blocks from different files
    checked = 0
    for i in range(len(blocks)):
        fi, bi = blocks[i]
        for j in range(i + 1, len(blocks)):
            fj, bj = blocks[j]
            if fi == fj:
                continue
            jac = jaccard(bi.shingles_3, bj.shingles_3)
            if jac >= overlap_sim:
                cos = cosine_from_counts(bi.word_counts, bj.word_counts)
                if cos >= overlap_sim:
                    snippet = bi.block_text[:200].replace("\n", " ")
                    topic_tags = infer_topic_tags(bi.heading_breadcrumb + " " + bj.heading_breadcrumb)
                    results.append(
                        {
                            "similarity": round((jac + cos) / 2, 4),
                            "file_a": str(records[fi].path),
                            "file_b": str(records[fj].path),
                            "location_a": bi.heading_breadcrumb,
                            "location_b": bj.heading_breadcrumb,
                            "snippet": snippet,
                            "topics": topic_tags,
                        }
                    )
                    checked += 1
                    if checked >= max_pairs:
                        return results
    return results


def infer_topic_tags(text: str) -> List[str]:
    # Very simple keyword-based tags
    tags = []
    lowered = text.lower()
    tag_map = {
        "tips": ["tips", "consejos"],
        "preguntas": ["preguntas", "questions"],
        "lenguaje corporal": ["lenguaje corporal", "body language"],
        "puntualidad": ["puntualidad", "punctuality"],
        "vestimenta": ["vestimenta", "dress"],
        "preparación": ["preparación", "preparation"],
        "investigación": ["investigación", "research"],
    }
    for tag, kws in tag_map.items():
        if any(kw in lowered for kw in kws):
            tags.append(tag)
    return tags


# ------------------------------
# Canonical selection and recommendations
# ------------------------------

def choose_canonical(records: List[FileRecord]) -> FileRecord:
    # Most comprehensive = longest normalized text, tie-breaker: most sections
    best = sorted(
        records,
        key=lambda r: (len(r.normalized_text), len(r.sections), str(r.path)),
        reverse=True,
    )[0]
    return best


def build_recommendations(
    exact_clusters: List[List[FileRecord]],
    near_components: List[List[int]],
    records: List[FileRecord],
) -> Dict[str, object]:
    recs: Dict[str, object] = {"exact": [], "near": []}
    for cluster in exact_clusters:
        canonical = choose_canonical(cluster)
        others = [r for r in cluster if r.path != canonical.path]
        recs["exact"].append(
            {
                "canonical": str(canonical.path),
                "delete": [str(r.path) for r in others],
                "reason": "Exact duplicate content (hash match)",
            }
        )

    for comp in near_components:
        comp_records = [records[i] for i in comp]
        canonical = choose_canonical(comp_records)
        others = [r for r in comp_records if r.path != canonical.path]
        recs["near"].append(
            {
                "canonical": str(canonical.path),
                "merge": [str(r.path) for r in others],
                "reason": "Highly similar content (near-duplicate cluster)",
            }
        )
    return recs


# ------------------------------
# Report writers
# ------------------------------

def write_markdown_report(
    out_path: Path,
    records: List[FileRecord],
    exact_clusters: List[List[FileRecord]],
    near_pairs: List[Tuple[int, int, float, float]],
    near_components: List[List[int]],
    overlaps: List[Dict[str, object]],
    recs: Dict[str, object],
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    total_files = len(records)
    total_exact = sum(len(c) for c in exact_clusters)
    with out_path.open("w", encoding="utf-8") as f:
        f.write("# Dedupe Report\n\n")
        f.write(f"- Total files analyzed: {total_files}\n")
        f.write(f"- Exact duplicate clusters: {len(exact_clusters)}\n")
        f.write(f"- Near-duplicate pairs: {len(near_pairs)}\n")
        f.write(f"- Near-duplicate clusters: {len(near_components)}\n")
        f.write(f"- Overlapping sections found: {len(overlaps)}\n\n")

        if exact_clusters:
            f.write("## Exact Duplicates\n\n")
            for idx, cluster in enumerate(exact_clusters, 1):
                f.write(f"### Cluster {idx}\n")
                for r in cluster:
                    f.write(f"- {r.path}\n")
                f.write("\n")

        if near_pairs:
            f.write("## Near-Duplicate Pairs (file-level)\n\n")
            # Show top 50 by avg score
            top_pairs = sorted(
                near_pairs,
                key=lambda t: (t[2] + t[3]) / 2.0,
                reverse=True,
            )[:50]
            for (i, j, jac, cos) in top_pairs:
                f.write(
                    f"- {records[i].path} ↔ {records[j].path} (Jaccard: {jac:.3f}, Cosine: {cos:.3f})\n"
                )
            f.write("\n")

        if near_components:
            f.write("## Near-Duplicate Clusters\n\n")
            for idx, comp in enumerate(near_components, 1):
                f.write(f"### Cluster {idx}\n")
                for k in comp:
                    f.write(f"- {records[k].path}\n")
                f.write("\n")

        if overlaps:
            f.write("## Overlapping Sections\n\n")
            # Show top 100 by similarity
            top_overlaps = sorted(overlaps, key=lambda d: float(d["similarity"]), reverse=True)[:100]
            for item in top_overlaps:
                f.write(
                    f"- {item['file_a']} [{item['location_a']}] ↔ {item['file_b']} [{item['location_b']}] "
                )
                f.write(f"(sim: {item['similarity']:.3f})\n")
                f.write(f"  - Topics: {', '.join(item.get('topics', []))}\n")
                f.write(f"  - Snippet: {item['snippet']}\n")
            f.write("\n")

        if recs:
            f.write("## Recommendations\n\n")
            if recs.get("exact"):
                f.write("### Exact duplicates\n")
                for r in recs["exact"]:
                    f.write(f"- Keep: {r['canonical']}\n")
                    if r.get("delete"):
                        for d in r["delete"]:
                            f.write(f"  - Delete: {d}\n")
                f.write("\n")

            if recs.get("near"):
                f.write("### Near-duplicate clusters\n")
                for r in recs["near"]:
                    f.write(f"- Keep: {r['canonical']}\n")
                    if r.get("merge"):
                        for m in r["merge"]:
                            f.write(f"  - Merge: {m}\n")
                f.write("\n")


def write_json_report(
    out_path: Path,
    records: List[FileRecord],
    exact_clusters: List[List[FileRecord]],
    near_pairs: List[Tuple[int, int, float, float]],
    near_components: List[List[int]],
    overlaps: List[Dict[str, object]],
    recs: Dict[str, object],
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    def rec_to_json(r: FileRecord) -> Dict[str, object]:
        return {
            "path": str(r.path),
            "hash": r.content_hash,
            "sections": [
                {
                    "heading": s.heading_breadcrumb,
                    "index": s.index_in_file,
                    "length": len(s.block_text),
                }
                for s in r.sections
            ],
            "length": len(r.normalized_text),
        }

    payload = {
        "stats": {
            "total_files": len(records),
            "exact_duplicate_clusters": len(exact_clusters),
            "near_duplicate_pairs": len(near_pairs),
            "near_duplicate_clusters": len(near_components),
            "overlapping_sections": len(overlaps),
        },
        "exact_duplicates": [
            [rec_to_json(r) for r in cluster] for cluster in exact_clusters
        ],
        "near_duplicate_pairs": [
            {
                "a": str(records[i].path),
                "b": str(records[j].path),
                "jaccard": round(j, 4),
                "cosine": round(c, 4),
            }
            for (i, j, j, c) in near_pairs
        ],
        "near_duplicate_clusters": [
            [str(records[i].path) for i in comp] for comp in near_components
        ],
        "overlapping_sections": overlaps,
        "recommendations": recs,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


# ------------------------------
# CLI
# ------------------------------

def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Markdown content deduplication CLI")
    p.add_argument("--root", required=True, help="Root directory to scan for .md files")
    p.add_argument("--min-sim", type=float, default=0.80, help="File-level near-duplicate similarity threshold")
    p.add_argument("--overlap-sim", type=float, default=0.85, help="Section-level overlap similarity threshold")
    p.add_argument("--out-md", default="reports/dedupe-report.md", help="Path to write Markdown report")
    p.add_argument("--out-json", default="reports/dedupe-report.json", help="Path to write JSON report")
    p.add_argument("--max-pairs", type=int, default=2000, help="Max overlapping section pairs to report")
    p.add_argument("--lang", default="es,en", help="Languages hint (unused, reserved)")
    return p.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = Path(args.root)
    if not root.exists() or not root.is_dir():
        print(f"[dedupe] Root not found or not a directory: {root}", file=sys.stderr)
        return 2

    print(f"[dedupe] Scanning for markdown files under: {root}")
    paths = sorted(iter_markdown_files(root))
    print(f"[dedupe] Found {len(paths)} markdown files")

    records: List[FileRecord] = []
    for p in paths:
        try:
            rec = build_file_record(p)
            records.append(rec)
        except Exception as e:
            print(f"[dedupe] Failed to process {p}: {e}", file=sys.stderr)

    # Exact duplicates
    exact_clusters = group_exact_duplicates(records)
    print(f"[dedupe] Exact duplicate clusters: {len(exact_clusters)}")

    # Near-duplicates (file-level)
    near_pairs, near_components = compute_near_duplicates(records, float(args.min_sim))
    print(f"[dedupe] Near-duplicate pairs: {len(near_pairs)}; clusters: {len(near_components)}")

    # Overlapping sections
    overlaps = detect_overlapping_sections(records, float(args.overlap_sim), int(args.max_pairs))
    print(f"[dedupe] Overlapping sections recorded: {len(overlaps)} (capped at {args.max_pairs})")

    # Recommendations
    recs = build_recommendations(exact_clusters, near_components, records)

    # Write reports
    out_md = Path(args.out_md)
    out_json = Path(args.out_json)
    write_markdown_report(out_md, records, exact_clusters, near_pairs, near_components, overlaps, recs)
    write_json_report(out_json, records, exact_clusters, near_pairs, near_components, overlaps, recs)

    print(f"[dedupe] Wrote Markdown report: {out_md}")
    print(f"[dedupe] Wrote JSON report: {out_json}")
    return 0


# Regex Unicode availability detection for tokenize_words
try:
    import regex as _regex  # type: ignore

    _HAS_REGEX_UNICODE = True

    def _compile_unicode_word_re():
        # Using Unicode properties for words (letters + numbers)
        return _regex.compile(r"\p{L}+[\p{L}\p{N}_-]*|\p{N}+")

    _UNICODE_WORD_RE = _compile_unicode_word_re()

    def tokenize_words(text: str) -> List[str]:  # type: ignore[override]
        return _UNICODE_WORD_RE.findall(text.lower())

except Exception:
    _HAS_REGEX_UNICODE = False


if __name__ == "__main__":
    sys.exit(main())


