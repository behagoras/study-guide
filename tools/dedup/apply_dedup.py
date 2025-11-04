#!/usr/bin/env python3
"""
Apply markdown deduplication by merging overlapping content into consolidated files by theme.

- Reads all .md files under --root
- Uses the same normalization and block extraction as dedupe.py
- Infers topic tags (tips, preguntas, lenguaje corporal, vestimenta, preparación, investigación)
- Clusters and deduplicates blocks per theme
- Writes consolidated files under <root>/<out_dir>/
- Optionally archives redundant source files under <root>/<archive_dir>/ (move)
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

# Ensure we can import sibling module
CURR = Path(__file__).resolve()
TOOLS_DIR = CURR.parent
WORKSPACE_ROOT = TOOLS_DIR.parent.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

try:
    # Import utilities from dedupe module
    from tools.dedup.dedupe import (
        FileRecord,
        SectionBlock,
        infer_topic_tags,
        build_file_record,
        iter_markdown_files,
        jaccard,
        cosine_from_counts,
    )
except Exception as e:
    print(f"Failed to import dedupe utilities: {e}", file=sys.stderr)
    sys.exit(2)


THEMES = {
    "tips": "Consolidado - Tips de Entrevista.md",
    "preguntas": "Consolidado - Preguntas de Entrevista.md",
    "lenguaje corporal": "Consolidado - Lenguaje Corporal.md",
    "vestimenta": "Consolidado - Vestimenta.md",
    "preparación": "Consolidado - Preparación.md",
    "investigación": "Consolidado - Investigación.md",
}


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Apply content consolidation by theme")
    p.add_argument("--root", required=True, help="Root directory to scan for .md files")
    p.add_argument("--out-dir", default="Consolidated", help="Directory (under root) to write consolidated files")
    p.add_argument("--archive-dir", default="Archive", help="Directory (under root) to archive redundant files")
    p.add_argument("--cluster-sim", type=float, default=0.90, help="Similarity threshold for block clustering")
    p.add_argument("--min-block-len", type=int, default=40, help="Minimum characters for a block to be considered")
    p.add_argument("--archive-threshold", type=float, default=0.80, help="If >= this fraction of a file's blocks are consolidated, archive the file")
    p.add_argument("--dry-run", action="store_true", help="Do not write files or archive; only print actions")
    return p.parse_args(argv)


def scan_records(root: Path) -> List[FileRecord]:
    paths = sorted(iter_markdown_files(root))
    records: List[FileRecord] = []
    for p in paths:
        try:
            rec = build_file_record(p)
            # filter out too-short blocks
            rec.sections = [b for b in rec.sections if len(b.block_text) >= 40]
            records.append(rec)
        except Exception as e:
            print(f"[apply] Failed to process {p}: {e}", file=sys.stderr)
    return records


def tag_blocks(records: List[FileRecord]) -> Dict[str, List[Tuple[FileRecord, SectionBlock]]]:
    theme_to_blocks: Dict[str, List[Tuple[FileRecord, SectionBlock]]] = defaultdict(list)
    for rec in records:
        for block in rec.sections:
            tags = infer_topic_tags(block.heading_breadcrumb + " " + block.block_text[:100])
            for t in tags:
                if t in THEMES:
                    theme_to_blocks[t].append((rec, block))
    return theme_to_blocks


def cluster_blocks(blocks: List[Tuple[FileRecord, SectionBlock]], threshold: float) -> List[List[Tuple[FileRecord, SectionBlock]]]:
    if not blocks:
        return []
    # Simple agglomerative clustering based on average of Jaccard and Cosine
    clusters: List[List[Tuple[FileRecord, SectionBlock]]] = []
    for pair in blocks:
        appended = False
        _, b = pair
        for cl in clusters:
            # Compare against cluster rep (first block)
            rep_b = cl[0][1]
            jac = jaccard(b.shingles_3, rep_b.shingles_3)
            cos = cosine_from_counts(b.word_counts, rep_b.word_counts)
            sim = (jac + cos) / 2.0
            if sim >= threshold:
                cl.append(pair)
                appended = True
                break
        if not appended:
            clusters.append([pair])
    return clusters


def choose_canonical_block(cluster: List[Tuple[FileRecord, SectionBlock]]) -> Tuple[FileRecord, SectionBlock]:
    # Longest block text wins; tie-breaker: path/heading
    return sorted(cluster, key=lambda t: (len(t[1].block_text), str(t[0].path), t[1].heading_breadcrumb), reverse=True)[0]


def write_consolidated_file(
    out_path: Path,
    theme: str,
    canonical_blocks: List[Tuple[FileRecord, SectionBlock]],
    dry_run: bool,
) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    lines: List[str] = []
    title = THEMES.get(theme, f"Consolidado - {theme.title()}.md")
    h1 = "# " + title.replace(".md", "")
    lines.append(h1)
    lines.append("")
    # Group by last heading segment for organization
    def last_heading(bc: str) -> str:
        parts = [p.strip() for p in bc.split("/") if p.strip()]
        return parts[-1] if parts else "General"

    grouped: Dict[str, List[Tuple[FileRecord, SectionBlock]]] = defaultdict(list)
    for rec, block in canonical_blocks:
        grouped[last_heading(block.heading_breadcrumb)].append((rec, block))

    for sub, items in sorted(grouped.items(), key=lambda kv: kv[0].lower()):
        lines.append(f"## {sub}")
        lines.append("")
        for rec, block in items:
            lines.append(block.block_text)
            lines.append("")
            lines.append(f"_Fuente: {rec.path} · {block.heading_breadcrumb}_")
            lines.append("")

    content = "\n".join(lines).rstrip() + "\n"
    if dry_run:
        print(f"[apply] Would write consolidated file: {out_path}")
    else:
        out_path.write_text(content, encoding="utf-8")


def compute_redundancy(records: List[FileRecord], selected_blocks: Set[Tuple[str, int]]) -> Dict[Path, float]:
    # selected_blocks keys are (str(path), index_in_file)
    fraction: Dict[Path, float] = {}
    for rec in records:
        total = len(rec.sections)
        if total == 0:
            fraction[rec.path] = 0.0
            continue
        selected = sum((str(rec.path), b.index_in_file) in selected_blocks for b in rec.sections)
        fraction[rec.path] = selected / total
    return fraction


def archive_redundant_files(
    root: Path, archive_dir: Path, redundancy: Dict[Path, float], threshold: float, dry_run: bool
) -> List[Path]:
    archived: List[Path] = []
    archive_dir.mkdir(parents=True, exist_ok=True)
    for path, frac in redundancy.items():
        if frac >= threshold:
            dest = archive_dir / path.name
            if dry_run:
                print(f"[apply] Would archive {path} -> {dest} (redundancy {frac:.2f})")
            else:
                # Move file
                dest_parent = dest.parent
                dest_parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(path), str(dest))
            archived.append(path)
    return archived


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = Path(args.root)
    out_dir = root / args.out_dir
    archive_dir = root / args.archive_dir
    print(f"[apply] Root: {root}")
    print(f"[apply] Consolidated out dir: {out_dir}")
    print(f"[apply] Archive dir: {archive_dir}")

    records = scan_records(root)
    print(f"[apply] Files scanned: {len(records)}")

    theme_to_blocks = tag_blocks(records)
    print("[apply] Theme counts:")
    for t in THEMES:
        print(f"  - {t}: {len(theme_to_blocks.get(t, []))} blocks")

    selected_blocks: Set[Tuple[str, int]] = set()

    # For each theme, cluster and pick canonical blocks, then write consolidated file
    for theme, filename in THEMES.items():
        blocks = theme_to_blocks.get(theme, [])
        if not blocks:
            continue
        clusters = cluster_blocks(blocks, threshold=float(args.cluster_sim))
        canonical_blocks = [choose_canonical_block(cl) for cl in clusters]
        # Track selected blocks for redundancy computation
        for rec, block in canonical_blocks:
            selected_blocks.add((str(rec.path), block.index_in_file))
        out_path = out_dir / filename
        write_consolidated_file(out_path, theme, canonical_blocks, dry_run=bool(args.dry_run))
        print(f"[apply] Consolidated {theme}: {len(canonical_blocks)} unique blocks -> {out_path}")

    # Archive redundant source files
    redundancy = compute_redundancy(records, selected_blocks)
    archived = archive_redundant_files(root, archive_dir, redundancy, float(args.archive_threshold), bool(args.dry_run))
    print(f"[apply] Archived files: {len(archived)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())


