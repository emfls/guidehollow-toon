#!/usr/bin/env python3
"""24/day hourly webtoon queue manager & automated publisher for toon.guidehollow.com."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
QUEUE_PATH = ROOT / "content" / "hourly_queue.json"
DYNAMIC_DIR = ROOT / "content" / "episodes_dynamic"
RAW_DIR = ROOT / "assets" / "ai_raw"
KST = timezone(timedelta(hours=9))


def load_queue() -> dict:
    return json.loads(QUEUE_PATH.read_text(encoding="utf-8"))


def save_queue(payload: dict) -> None:
    QUEUE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def next_pending() -> dict | None:
    q = load_queue()
    for item in q.get("items", []):
        if item.get("status") != "published":
            return item
    return None


def cmd_next_brief() -> int:
    item = next_pending()
    if not item:
        print(json.dumps({"status": "empty", "remaining": 0}, ensure_ascii=False))
        return 0
    q = load_queue()
    remaining = sum(1 for x in q.get("items", []) if x.get("status") != "published")
    out = {
        "status": "ready",
        "remaining": remaining,
        "episodeNo": item["episodeNo"],
        "id": item["id"],
        "title": item["title"],
        "hook": item["hook"],
        "summary": item["summary"],
        "punchlineRecap": item["punchlineRecap"],
        "protagonist": item["protagonist"],
        "setting": item["setting"],
        "sheetA_prompt": item["sheetA_prompt"],
        "sheetB_prompt": item["sheetB_prompt"],
        "target_sheet_a": str(RAW_DIR / f"ep{item['episodeNo']:02d}_sheet_a.jpg"),
        "target_sheet_b": str(RAW_DIR / f"ep{item['episodeNo']:02d}_sheet_b.jpg"),
        "panels": item["panels"],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def _find_sheet(ep_num: int, half: str) -> Path | None:
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        p = RAW_DIR / f"ep{ep_num:02d}_sheet_{half}{ext}"
        if p.exists():
            return p
    return None


def cmd_publish_id(ep_id: str, push: bool) -> int:
    q = load_queue()
    item = next((x for x in q.get("items", []) if x.get("id") == ep_id), None)
    if not item:
        print(f"ERROR: Episode id {ep_id!r} not found in queue", file=sys.stderr)
        return 1
    ep_num = int(item["episodeNo"])
    if not _find_sheet(ep_num, "a") or not _find_sheet(ep_num, "b"):
        print(f"ERROR: Missing ep{ep_num:02d}_sheet_a or _b image in {RAW_DIR}", file=sys.stderr)
        return 1

    DYNAMIC_DIR.mkdir(parents=True, exist_ok=True)
    now_iso = datetime.now(KST).isoformat(timespec="seconds")
    ep_doc = {
        "id": item["id"],
        "episodeNo": ep_num,
        "genreKey": "comedy",
        "genre": "병맛·영포티",
        "styleMode": "comedy",
        "publishedAt": now_iso,
        "title": item["title"],
        "hook": item["hook"],
        "summary": item["summary"],
        "guideTitle": "오늘의 흑역사 한줄평 · 웃고 넘기는 영포티 썰",
        "punchlineRecap": item["punchlineRecap"],
        "coupang": {
            "widgetId": "1050469" if ep_num % 2 == 1 else "1050468",
            "badge": "병맛 썰 속 공감 아이템",
            "title": "오늘의 가벼운 데일리 소품 모음",
            "reason": "일상 여행·카페 코디 아이템",
            "cta": "추천 상품 보기",
            "url": "https://link.coupang.com/a/iG9mVheC0i",
            "guideUrl": "https://shopping.guidehollow.com/",
            "guideLabel": "쇼핑 가이드",
        },
        "panels": item["panels"],
    }
    ep_path = DYNAMIC_DIR / f"{ep_id}.json"
    ep_path.write_text(json.dumps(ep_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    item["status"] = "published"
    item["publishedAt"] = now_iso
    save_queue(q)

    subprocess.run([sys.executable, str(ROOT / "tools" / "build.py")], cwd=str(ROOT), check=True)
    subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=str(ROOT), check=True)

    if push:
        subprocess.run(["git", "add", "assets/ai_raw", "content", "dist"], cwd=str(ROOT), check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Publish hourly comedy webtoon {ep_id}"],
            cwd=str(ROOT),
            check=True,
        )
        subprocess.run(["git", "push", "origin", "main"], cwd=str(ROOT), check=True)
    print(f"PUBLISHED_HOURLY_COMEDY id={ep_id} ep={ep_num} push={push}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--next-brief", action="store_true")
    parser.add_argument("--publish-id", type=str)
    parser.add_argument("--push", action="store_true")
    args = parser.parse_args()
    if args.next_brief:
        return cmd_next_brief()
    if args.publish_id:
        return cmd_publish_id(args.publish_id, push=args.push)
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
