#!/usr/bin/env python3
"""Audit story-text coverage; labels and string matches do not prove learning.

Usage: python audit_series.py SERIES_DIR
Prints a JSON report. Exit 0: valid records (coverage may be incomplete);
exit 1: inconsistent records; exit 2: unreadable input.
"""

import csv
import json
import re
import sys
from pathlib import Path


FIELDS = {
    "id", "headword", "meaning", "forms", "edition", "book", "unit",
    "source_status", "source",
}
READY = {"text_ready", "illustrated"}


def read_json(path):
    with path.open(encoding="utf-8-sig") as stream:
        return json.load(stream)


def audit(directory):
    base = Path(directory).resolve()
    errors, failures = [], []
    with (base / "vocabulary.csv").open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        if not FIELDS.issubset(reader.fieldnames or []):
            raise ValueError("vocabulary.csv 缺少字段：" + ", ".join(sorted(FIELDS - set(reader.fieldnames or []))))
        rows = list(reader)
    state = read_json(base / "state.json")
    if not isinstance(state, dict) or state.get("schema_version") != 1:
        raise ValueError("state.json 必须是 schema_version=1 的对象")
    vocab, patterns = {}, {}
    for line, row in enumerate(rows, 2):
        row = {key: (row.get(key) or "").strip() for key in FIELDS}
        wid = row["id"]
        if not wid or wid in vocab:
            errors.append(f"vocabulary.csv 第 {line} 行：词条 ID 缺失或重复：{wid!r}")
            continue
        if not row["headword"] or not row["meaning"]:
            errors.append(f"{wid}：headword 和 meaning 必须非空")
        if row["source_status"] not in {"verified", "provisional"}:
            errors.append(f"{wid}：source_status 非法")
        if row["source_status"] == "verified":
            unresolved = {"待核", "待确认", "pending", "unknown", "tbd"}
            missing = [key for key in ("edition", "book", "unit", "source") if not row[key] or row[key].lower() in unresolved]
            if missing:
                errors.append(f"{wid}：verified 词条缺少确切值 " + ", ".join(missing))
        forms = [row["headword"]] + row["forms"].split("|")
        forms = sorted({form.strip().lower() for form in forms if form.strip()}, key=lambda x: (-len(x), x))
        # Explicit forms only: no stemming, lemmatization, or sense inference.
        patterns[wid] = re.compile(r"(?<![A-Za-z])(?:" + "|".join(re.escape(form) for form in forms) + r")(?![A-Za-z])", re.I) if forms else None
        vocab[wid] = row

    curriculum = state.get("curriculum", {})
    if not isinstance(curriculum, dict):
        raise ValueError("curriculum 必须是对象")
    if curriculum.get("edition_status") not in {"pending", "confirmed"}:
        errors.append("curriculum.edition_status 非法")
    if type(curriculum.get("corpus_frozen")) is not bool:
        errors.append("curriculum.corpus_frozen 必须是布尔值")

    def book_list(key):
        values = curriculum.get(key, [])
        if not isinstance(values, list) or any(not isinstance(x, str) or not x.strip() for x in values):
            errors.append(f"curriculum.{key} 必须是非空书名组成的数组")
            return []
        if len(values) != len(set(values)):
            errors.append(f"curriculum.{key} 有重复书名")
        return values

    expected, checked_books = book_list("books_expected"), book_list("books_verified")
    if len(expected) != 8:
        errors.append("curriculum.books_expected 应包含 8 个不重复册名")
    episodes = state.get("episodes", [])
    if not isinstance(episodes, list):
        raise ValueError("episodes 必须是数组")
    seen_episodes, assigned = set(), {}
    introduced, qualified_episodes = set(), {wid: set() for wid in vocab}
    planned_count, ready_count = 0, 0
    for episode in episodes:
        if not isinstance(episode, dict):
            errors.append("episode 必须是对象")
            continue
        eid, status = episode.get("id"), episode.get("status")
        if not isinstance(eid, str) or not eid or eid in seen_episodes:
            errors.append(f"episode ID 缺失或重复：{eid!r}")
            continue
        seen_episodes.add(eid)
        if status not in READY | {"planned"}:
            errors.append(f"{eid}：status 非法")
            continue
        targets = {}
        for key in ("new_targets", "review_targets"):
            values = episode.get(key, [])
            if not isinstance(values, list) or any(not isinstance(x, str) for x in values):
                errors.append(f"{eid}.{key} 必须是词条 ID 数组")
                values = []
            if len(values) != len(set(values)):
                errors.append(f"{eid}.{key} 包含重复词条")
            targets[key] = set(values)
            for wid in values:
                if wid not in vocab:
                    errors.append(f"{eid}.{key} 引用未知词条：{wid}")
        if targets["new_targets"] & targets["review_targets"]:
            errors.append(f"{eid}：同一词条不能同时为新词和复习词")
        for wid in targets["new_targets"]:
            if wid in assigned:
                errors.append(f"{wid} 重复首次引入：{assigned[wid]} 与 {eid}")
            else:
                assigned[wid] = eid
        artifact_name = episode.get("artifact")
        if not isinstance(artifact_name, str) or not artifact_name:
            errors.append(f"{eid}：缺少 artifact 相对路径")
            continue
        artifact_path = (base / artifact_name).resolve()
        try:
            artifact_path.relative_to(base)
        except ValueError:
            errors.append(f"{eid}：artifact 不得指向系列目录以外")
            continue
        if status == "planned":
            planned_count += 1
            continue
        ready_count += 1
        # The episode array is the reading order; plans are not introductions.
        premature_reviews = (targets["review_targets"] & vocab.keys()) - introduced
        for wid in sorted(premature_reviews):
            errors.append(f"{eid}：复习词 {wid} 尚未在此前已交付正文中成功引入")
        try:
            artifact = read_json(artifact_path)
        except (OSError, ValueError) as exc:
            errors.append(f"{eid}：无法读取正文：{exc}")
            continue
        if not isinstance(artifact, dict) or artifact.get("id") != eid:
            errors.append(f"{eid}：正文 ID 不匹配或正文不是对象")
            continue
        pages = artifact.get("pages")
        if not isinstance(pages, list) or not pages:
            errors.append(f"{eid}：pages 必须是非空数组")
            continue
        texts, page_ids = [], set()
        for page in pages:
            if not isinstance(page, dict):
                errors.append(f"{eid}：page 必须是对象")
                continue
            page_id = page.get("page")
            if type(page_id) is not int or page_id < 1 or page_id in page_ids:
                errors.append(f"{eid}：页码缺失、非法或重复")
            else:
                page_ids.add(page_id)
            for key in ("chinese", "art_prompt"):
                if not isinstance(page.get(key), str):
                    errors.append(f"{eid} 第 {page_id} 页：缺少字符串字段 {key}")
            english = page.get("english")
            if isinstance(english, str):
                texts.append(english)
            elif isinstance(english, list) and all(isinstance(x, str) for x in english):
                texts.extend(english)
            else:
                errors.append(f"{eid} 第 {page_id} 页：english 必须为字符串或字符串数组")
        confirmed = artifact.get("sense_confirmed", [])
        if not isinstance(confirmed, list) or any(not isinstance(x, str) for x in confirmed):
            errors.append(f"{eid}：sense_confirmed 必须是词条 ID 数组")
            confirmed = []
        for wid in confirmed:
            if wid not in vocab:
                errors.append(f"{eid}.sense_confirmed 引用未知词条：{wid}")
        for wid in sorted((targets["new_targets"] | targets["review_targets"]) & vocab.keys()):
            count = sum(len(patterns[wid].findall(text)) for text in texts) if patterns[wid] else 0
            required = 3 if wid in targets["new_targets"] else 1
            if count >= required and wid in confirmed and wid not in premature_reviews:
                qualified_episodes[wid].add(eid)
                # A review can never establish first introduction.
                if wid in targets["new_targets"]:
                    introduced.add(wid)
            else:
                failures.append({"episode": eid, "word_id": wid, "occurrences": count, "required_occurrences": required, "sense_confirmed": wid in confirmed, "prior_introduction_missing": wid in premature_reviews})

    verified = {wid for wid, row in vocab.items() if row["source_status"] == "verified"}
    provisional = {wid for wid, row in vocab.items() if row["source_status"] == "provisional"}
    repeated = {wid for wid, eps in qualified_episodes.items() if len(eps) >= 3}
    verified_books = {vocab[wid]["book"] for wid in verified}
    conditions = {
        "records_valid": not errors,
        "corpus_frozen": curriculum.get("corpus_frozen") is True,
        "edition_confirmed": curriculum.get("edition_status") == "confirmed",
        "eight_books_verified_exactly": len(expected) == 8 and set(expected) == set(checked_books),
        "verified_entries_cover_expected_books": bool(expected) and verified_books == set(expected),
        "verified_corpus_nonempty": bool(verified),
        "all_verified_introduced": bool(verified) and verified <= introduced,
        "all_verified_in_at_least_three_episodes": bool(verified) and verified <= repeated,
    }
    return {
        "series": str(base),
        "verified_total": len(verified),
        "provisional_total": len(provisional),
        "text_qualified_introduced": {"verified": len(verified & introduced), "provisional": len(provisional & introduced)},
        "verified_not_yet_assigned": sorted(verified - assigned.keys()),
        "verified_not_yet_introduced": sorted(verified - introduced),
        "planned_episodes_ignored": planned_count,
        "text_episodes_checked": ready_count,
        "in_at_least_three_qualified_episodes": {"verified": len(verified & repeated), "provisional": len(provisional & repeated)},
        "full_coverage_conditions": conditions,
        "full_coverage": all(conditions.values()),
        "target_evidence_failures": failures,
        "errors": errors,
        "notes": [
            "只统计 text_ready/illustrated 正文中被明确指定的目标；planned、中文、绘图提示词和正文外单词表不计。",
            "新目标词每集至少出现 3 次，复习目标词每集至少出现 1 次；均须有 sense_confirmed 人工语义标记，满足对应阈值才计入跨集出现数。",
            "state.episodes 数组顺序视为编排顺序；复习词须已在此前 text_ready/illustrated 正文中成功引入，planned 不构成先前引入。",
            "字符串匹配和人工标记不能证明语义正确、使用自然或孩子已经掌握；不能自动合并词形或义项。",
            "verified/source/册名等标签本身不能证明来源为官方、语料完整或人工核对真实；冻结词表前仍需核验所选版次与原始词表。",
            "illustrated 是记录状态，本脚本不验证实际插图文件。",
        ],
    }


def main():
    if len(sys.argv) != 2:
        print("Usage: python audit_series.py SERIES_DIR", file=sys.stderr)
        return 2
    try:
        report = audit(sys.argv[1])
    except (OSError, ValueError, csv.Error) as exc:
        print(json.dumps({"full_coverage": False, "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
