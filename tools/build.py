#!/usr/bin/env python3
"""Authentic comic.naver.com style static webtoon portal builder for toon.guidehollow.com."""
from __future__ import annotations

import argparse
import base64
import html
import io
import json
from pathlib import Path
import shutil
import sys
import textwrap

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from content.episodes import EPISODES  # noqa: E402

DIST = ROOT / "dist"
AI_RAW_DIR = ROOT / "assets" / "ai_raw"
SITE_URL = "https://toon.guidehollow.com"
ADSENSE_PUB = "ca-pub-8830524482034754"
ADSENSE_TXT = "google.com, pub-8830524482034754, DIRECT, f08c47fec0942fa0\n"
GA4_ID = "G-QP5Q67GE5B"
COUPANG_DISCLOSURE = "이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."
AI_IMAGE_NOTICE = "* 본 웹툰 이미지는 AI 도구를 활용해 제작되었습니다."

EPISODE_CUT_COUNTS = {
    "ep01-office-cider": 18,
    "ep02-love-wedding": 14,
    "ep03-car-parking": 16,
    "ep04-mystery-mirror": 15,
    "ep05-finance-jeonse": 17,
    "ep06-secondhand-brick": 13,
    "ep07-cafe-receipt": 12,
    "ep08-upstairs-noise": 15,
    "ep09-groupbuy-scam": 16,
    "ep10-gym-refund": 14,
}

DISALLOWED_EDITOR_MARKERS = [
    "미리보기",
    "생성하기",
    "장면 커스텀",
    "DIY",
    "대사 입력",
    "말풍선 문구",
    "에디터 스튜디오",
]

DISALLOWED_FAKE_SERVER_MARKERS = [
    "이번 화 별점 주기",
    "별점순",
    "베스트 댓글",
    "댓글 (",
    "댓글을 입력",
    "관심 13,946",
]


def prepare_episodes() -> list[dict]:
    """Return deep-cleaned episodes with variable cut counts and zero fake rating/comment metadata."""
    cleaned: list[dict] = []
    for ep in EPISODES:
        raw_panels = ep["panels"]
        target_n = EPISODE_CUT_COUNTS.get(ep["id"], len(raw_panels))
        if target_n < len(raw_panels) and target_n >= 4:
            picked = raw_panels[: target_n - 2] + raw_panels[-2:]
        else:
            picked = list(raw_panels)
        panels = []
        for idx, p in enumerate(picked, start=1):
            np = dict(p)
            np["sourceCut"] = int(p.get("cut", idx))
            np["cut"] = idx
            panels.append(np)
        ep_copy = {
            k: v
            for k, v in ep.items()
            if k not in ("rating", "viewsLabel", "bestComments", "panels", "badgeText")
        }
        for txt_field in ("summary", "aiDisclosure"):
            if isinstance(ep_copy.get(txt_field), str):
                ep_copy[txt_field] = ep_copy[txt_field].replace("18컷", f"{len(panels)}컷")
        ep_copy["cutCount"] = len(panels)
        ep_copy["panels"] = panels
        cleaned.append(ep_copy)
    return cleaned


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def wrap_ko(text: str, width: int = 16, max_lines: int = 3) -> list[str]:
    clean = " ".join(str(text or "").split())
    if not clean:
        return []
    lines = textwrap.wrap(clean, width=width, break_long_words=True)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        if len(lines[-1]) > 2:
            lines[-1] = lines[-1][:-1] + "…"
    return lines


_SHEET_CACHE: dict[Path, Image.Image] = {}


def _load_sheet(ep_num: int, half: str) -> Image.Image:
    path = AI_RAW_DIR / f"ep{ep_num:02d}_sheet_{half}.jpg"
    if not path.exists():
        raise FileNotFoundError(f"Missing AI webtoon sheet: {path}")
    if path not in _SHEET_CACHE:
        _SHEET_CACHE[path] = Image.open(path).convert("RGB")
    return _SHEET_CACHE[path]


def _slice_cell_b64(
    ep_num: int,
    cut_index_1based: int,
    size: tuple[int, int],
    centering: tuple[float, float] = (0.5, 0.35),
    quality: int = 82,
) -> str:
    """Slice one cell from the episode's 3x3 AI sheet cleanly with divider borders trimmed."""
    half = "a" if cut_index_1based <= 9 else "b"
    cell_idx = (cut_index_1based - 1) if cut_index_1based <= 9 else (cut_index_1based - 10)
    sheet = _load_sheet(ep_num, half)
    w, h = sheet.size
    col = cell_idx % 3
    row = cell_idx // 3
    cw = w / 3.0
    ch = h / 3.0
    pad_x = cw * 0.048
    pad_y = ch * 0.048
    box = (
        int(round(col * cw + pad_x)),
        int(round(row * ch + pad_y)),
        int(round((col + 1) * cw - pad_x)),
        int(round((row + 1) * ch - pad_y)),
    )
    cropped = sheet.crop(box)
    fitted = ImageOps.fit(cropped, size, method=Image.Resampling.LANCZOS, centering=centering)
    buf = io.BytesIO()
    fitted.save(buf, format="JPEG", quality=quality, optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def render_cover_svg(ep: dict) -> str:
    """Render an authentic clean comic.naver.com 480x620 poster with circle badge & title logo only."""
    w, h = 480, 620
    title_lines = wrap_ko(ep["title"], width=14, max_lines=3)
    img_b64 = _slice_cell_b64(ep["episodeNo"], 1, (w, h), centering=(0.5, 0.25), quality=84)
    badge = "신작" if ep["episodeNo"] <= 3 else "UP"
    badge_bg = "#00dc64" if badge == "신작" else "#ff3b30"
    badge_fg = "#111111" if badge == "신작" else "#ffffff"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(ep["title"])}">',
        f'<image href="data:image/jpeg;base64,{img_b64}" x="0" y="0" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice"/>',
        '<defs><linearGradient id="nv-cover-grad" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#000000" stop-opacity="0"/>'
        '<stop offset="55%" stop-color="#000000" stop-opacity="0.48"/>'
        '<stop offset="100%" stop-color="#000000" stop-opacity="0.92"/>'
        '</linearGradient></defs>',
        '<rect x="0" y="340" width="480" height="280" fill="url(#nv-cover-grad)"/>',
        f'<circle cx="38" cy="38" r="20" fill="{badge_bg}"/>',
        f'<text x="38" y="43" text-anchor="middle" font-family="Pretendard, Apple SD Gothic Neo, sans-serif" font-size="13" font-weight="900" fill="{badge_fg}">{badge}</text>',
    ]
    base_y = 582 - (len(title_lines) - 1) * 34
    for idx, line in enumerate(title_lines):
        parts.append(
            f'<text x="20" y="{base_y + idx * 34}" font-family="Pretendard, Apple SD Gothic Neo, sans-serif" '
            f'font-size="24" font-weight="900" fill="#ffffff" stroke="#111111" stroke-width="1.2" paint-order="stroke fill">{esc(line)}</text>'
        )
    parts.append("</svg>")
    return "\n".join(parts)


def render_panel_svg(ep: dict, idx: int, panel: dict, total: int) -> str:
    """Render an authentic 690x1120 Naver Webtoon vertical white-paper panel with white gutters & oval bubbles."""
    w, h = 690, 1120
    source_cut = int(panel.get("sourceCut", idx))
    img_b64 = _slice_cell_b64(ep["episodeNo"], source_cut, (650, 740), centering=(0.5, 0.34), quality=82)
    is_left = (idx % 2 == 1)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(ep["title"])} {idx}컷">',
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>',
    ]

    # Top narration box on clean white paper gutter (matching Naver Webtoon boxed narration)
    sub_lines = wrap_ko(panel["subline"], width=27, max_lines=2)
    if sub_lines:
        n_h = 26 + len(sub_lines) * 26
        parts.append(
            f'<rect x="115" y="14" width="460" height="{n_h}" fill="#ffffff" stroke="#111111" stroke-width="2"/>'
        )
        for s_idx, s_line in enumerate(sub_lines):
            parts.append(
                f'<text x="345" y="{42 + s_idx * 26}" text-anchor="middle" '
                f'font-family="Pretendard, Apple SD Gothic Neo, sans-serif" font-size="18.5" font-weight="700" fill="#111111">{esc(s_line)}</text>'
            )

    # Sharp rectangular AI illustration panel on pure white paper (y=220..960)
    parts.append(
        f'<image href="data:image/jpeg;base64,{img_b64}" x="20" y="220" width="650" height="740" preserveAspectRatio="xMidYMid slice"/>'
    )
    parts.append(
        '<rect x="20" y="220" width="650" height="740" fill="none" stroke="#111111" stroke-width="2.2"/>'
    )

    # Authentic white oval comic speech bubble hovering smoothly from top white gutter into upper panel
    d_lines = wrap_ko(panel["line"], width=16, max_lines=3)
    bw = 340
    bh = 36 + len(d_lines) * 28
    bx = 44 if is_left else 306
    by = 104
    tx = bx + (bw * 2 // 3 if is_left else bw // 3)
    parts.append(
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="{bh // 2}" fill="#ffffff" stroke="#111111" stroke-width="2.2"/>'
    )
    parts.append(
        f'<polygon points="{tx-10},{by+bh-1} {tx+2},{by+bh+28} {tx+14},{by+bh-1}" fill="#ffffff" stroke="#111111" stroke-width="2" stroke-linejoin="round"/>'
    )
    parts.append(f'<rect x="{tx-8}" y="{by+bh-5}" width="20" height="8" fill="#ffffff"/>')
    for d_idx, d_line in enumerate(d_lines):
        parts.append(
            f'<text x="{bx + bw // 2}" y="{by + 36 + d_idx * 28}" text-anchor="middle" '
            f'font-family="Pretendard, Apple SD Gothic Neo, sans-serif" font-size="20" font-weight="800" fill="#111111">{esc(d_line)}</text>'
        )

    # Hand-lettered comic SFX with thick white halo stroke (no red UI button)
    sfx = panel.get("sfx", "")
    if sfx:
        sx = 575 if is_left else 115
        rot = -8 if is_left else 7
        parts.append(
            f'<text x="{sx}" y="932" text-anchor="middle" transform="rotate({rot} {sx} 932)" '
            f'font-family="Pretendard, Apple SD Gothic Neo, sans-serif" font-size="38" font-weight="900" '
            f'fill="#111111" stroke="#ffffff" stroke-width="10" stroke-linejoin="round" paint-order="stroke fill">{esc(sfx)}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


STYLE_CSS = """
:root {
  --nv-green: #00dc64;
  --nv-green-dark: #00b853;
  --ink: #111111;
  --muted: #666666;
  --line: #ebebeb;
  --bg: #ffffff;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; overflow-x: hidden; background: #ffffff; color: #111111; font-family: "Pretendard", "Apple SD Gothic Neo", "Noto Sans KR", sans-serif; line-height: 1.5; }
a { color: inherit; text-decoration: none; }
img { display: block; max-width: 100%; height: auto; }
.wrap { width: 100%; max-width: 1190px; margin: 0 auto; padding: 0 16px; }

/* Naver Webtoon 3-Tier White Header */
.nv-top-strip { border-bottom: 1px solid #f0f0f0; background: #ffffff; }
.nv-top-inner { display: flex; align-items: center; justify-content: space-between; height: 52px; gap: 12px; }
.nv-brand-group { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.nv-logo { display: inline-flex; align-items: center; gap: 6px; font-weight: 900; font-size: 18px; letter-spacing: -0.04em; color: #111111; }
.nv-logo-mark { font-weight: 900; font-size: 13px; color: #111111; letter-spacing: -0.03em; }
.nv-logo-dot { color: #d1d5db; }
.nv-logo-sub { font-size: 13.5px; font-weight: 600; color: #767676; }
.nv-search-row { display: flex; align-items: center; gap: 10px; }
.nv-search-box { display: inline-flex; align-items: center; border: 1px solid #d9d9d9; border-radius: 4px; height: 34px; padding: 0 10px; background: #ffffff; width: 230px; }
.nv-search-box input { border: 0; outline: 0; font-size: 13px; width: 100%; font-family: inherit; }
.nv-creator-btn { display: inline-flex; align-items: center; background: var(--nv-green); color: #111111; font-size: 12px; font-weight: 900; padding: 7px 14px; border-radius: 4px; letter-spacing: 0.02em; }

.nv-main-nav { border-bottom: 1px solid #ebebeb; background: #ffffff; }
.nv-main-tabs { display: flex; align-items: center; height: 48px; gap: 2px; }
.nv-main-tabs a { display: inline-flex; align-items: center; height: 48px; padding: 0 18px; font-size: 15px; font-weight: 800; color: #111111; }
.nv-main-tabs a.is-on { background: var(--nv-green); color: #111111; }

.nv-sub-nav { border-bottom: 1px solid #ebebeb; background: #ffffff; overflow-x: auto; }
.nv-sub-tabs { display: flex; align-items: center; height: 44px; gap: 18px; min-width: max-content; }
.nv-sub-btn { background: none; border: 0; border-bottom: 2px solid transparent; height: 44px; padding: 0 2px; font-size: 14px; font-weight: 700; color: #333333; cursor: pointer; font-family: inherit; }
.nv-sub-btn.is-active { color: #00b853; border-bottom-color: var(--nv-green); font-weight: 800; }

/* 이달의 신규 웹툰 3-column horizontal showcase */
.nv-sec-title-row { display: flex; align-items: center; justify-content: space-between; margin: 28px 0 14px; gap: 12px; flex-wrap: wrap; }
.nv-sec-title { margin: 0; font-size: 20px; font-weight: 800; color: #111111; letter-spacing: -0.02em; }
.nv-sec-more { font-size: 13.5px; color: #666666; font-weight: 600; }
.new-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; }
.new-card { display: flex; flex-direction: column; }
.new-thumb { position: relative; aspect-ratio: 4 / 3; border-radius: 4px; overflow: hidden; border: 1px solid rgba(0, 0, 0, 0.08); background: #f3f4f6; margin-bottom: 10px; }
.new-thumb img { width: 100%; height: 100%; object-fit: cover; object-position: top; }
.new-badge-circle { position: absolute; top: 10px; left: 10px; width: 32px; height: 32px; border-radius: 50%; background: var(--nv-green); color: #111111; font-size: 11px; font-weight: 900; display: flex; align-items: center; justify-content: center; }
.new-title { margin: 0 0 3px; font-size: 15.5px; font-weight: 800; color: #111111; line-height: 1.38; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.new-author { font-size: 13px; color: #444444; font-weight: 600; margin-bottom: 4px; }
.new-desc { margin: 0; font-size: 12.5px; color: #767676; line-height: 1.45; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

/* 요일별 / 전체 웹툰 5-column clean grid */
.wt-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 22px 16px; }
.wt-card { display: flex; flex-direction: column; gap: 7px; }
.wt-cover { aspect-ratio: 48 / 62; border-radius: 4px; overflow: hidden; border: 1px solid rgba(0, 0, 0, 0.08); background: #f8f9fa; }
.wt-cover img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.18s ease; }
.wt-card:hover .wt-cover img { transform: scale(1.03); }
.wt-title { margin: 0; font-size: 14.5px; font-weight: 800; color: #111111; line-height: 1.36; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.wt-meta { font-size: 12.5px; color: #666666; font-weight: 600; }

/* 작품 홈 헤더 + 회차 리스트 (comic.naver.com/webtoon/list style) */
.series-home-box { margin-top: 34px; border: 1px solid #ebebeb; border-radius: 6px; padding: 24px; background: #ffffff; }
.series-top { display: grid; grid-template-columns: 185px 1fr; gap: 24px; align-items: start; margin-bottom: 22px; }
.series-poster { width: 185px; aspect-ratio: 48 / 62; border-radius: 4px; overflow: hidden; border: 1px solid rgba(0, 0, 0, 0.08); }
.series-poster img { width: 100%; height: 100%; object-fit: cover; }
.series-h2 { margin: 0 0 8px; font-size: 22px; font-weight: 800; color: #111111; line-height: 1.32; }
.series-authors { font-size: 13.5px; color: #666666; margin-bottom: 10px; font-weight: 600; }
.series-authors strong { color: #111111; }
.series-synop { margin: 0 0 14px; font-size: 14px; color: #333333; line-height: 1.6; }
.series-tags { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 16px; }
.series-tag { font-size: 12px; color: #555555; background: #f3f4f6; padding: 5px 10px; border-radius: 4px; font-weight: 600; }
.series-cta-row { display: flex; gap: 8px; flex-wrap: wrap; }
.btn-first-ep { flex: 1; min-width: 190px; height: 46px; display: inline-flex; align-items: center; justify-content: center; background: var(--nv-green); color: #111111; font-weight: 900; font-size: 15px; border-radius: 4px; }
.btn-sub-outline { height: 46px; padding: 0 18px; display: inline-flex; align-items: center; justify-content: center; background: #f7f7f7; border: 1px solid #e5e5e5; color: #111111; font-weight: 700; font-size: 14px; border-radius: 4px; cursor: pointer; }

.ep-list { border-top: 1px solid #111111; }
.ep-item { display: grid; grid-template-columns: 98px 1fr 120px; gap: 14px; align-items: center; padding: 12px 10px; border-bottom: 1px solid #ebebeb; transition: background 0.12s ease; }
.ep-item:hover { background: #f9fafb; }
.ep-item-thumb { width: 98px; height: 58px; border-radius: 4px; overflow: hidden; border: 1px solid #e5e5e5; }
.ep-item-thumb img { width: 100%; height: 100%; object-fit: cover; object-position: top; }
.ep-item-name { font-size: 15px; font-weight: 700; color: #111111; margin-bottom: 3px; }
.ep-item-sub { font-size: 12.5px; color: #595959; }
.ep-item-right { text-align: right; font-size: 13px; color: #595959; }

/* Authentic Pure White Paper Vertical Webtoon Viewer (comic.naver.com/webtoon/detail) */
body.viewer-body { background: #ffffff; color: #111111; }
.read-progress { position: fixed; top: 0; left: 0; width: 100%; height: 2.5px; z-index: 95; background: #f0f0f0; }
.read-progress-fill { height: 100%; width: 0%; background: var(--nv-green); }
.viewer-bar { position: sticky; top: 0; z-index: 70; background: rgba(255, 255, 255, 0.96); backdrop-filter: blur(8px); border-bottom: 1px solid #ebebeb; color: #111111; }
.viewer-bar-inner { display: flex; align-items: center; justify-content: space-between; gap: 10px; min-height: 54px; padding: 6px 0; }
.viewer-title-group { display: flex; align-items: center; gap: 10px; min-width: 0; flex: 1; }
.viewer-back { display: inline-flex; align-items: center; font-size: 13.5px; font-weight: 700; color: #111111; padding: 6px 10px; border: 1px solid #e0e0e0; border-radius: 4px; flex-shrink: 0; min-height: 36px; }
.viewer-h1 { margin: 0; font-size: 15px; font-weight: 800; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.viewer-controls { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
.v-ep-select { height: 36px; max-width: 168px; border: 1px solid #d9d9d9; border-radius: 4px; background: #ffffff; color: #111111; font-size: 12.5px; font-weight: 700; padding: 0 6px; font-family: inherit; }
.v-btn { font-size: 13px; font-weight: 700; padding: 6px 12px; border: 1px solid #e0e0e0; border-radius: 4px; background: #ffffff; color: #111111; cursor: pointer; min-height: 36px; display: inline-flex; align-items: center; justify-content: center; }
.v-btn.primary { background: var(--nv-green); border-color: var(--nv-green); color: #111111; font-weight: 900; }
.v-btn.is-disabled { color: #9ca3af; background: #f9fafb; pointer-events: none; }

.ep-head-meta { max-width: 690px; margin: 22px auto 12px; padding: 0 12px; text-align: center; }
.ep-head-meta h2 { margin: 0 0 8px; font-size: clamp(19px, 3vw, 24px); font-weight: 800; color: #111111; line-height: 1.35; }
.ep-head-meta p { margin: 0; font-size: 14px; color: #444444; }
.ai-disclosure-sm { margin-top: 8px; font-size: 11.5px; color: #595959; }

.comic-canvas { width: 100%; max-width: 690px; margin: 0 auto; background: #ffffff; }
.comic-cut { width: 100%; margin: 0; padding: 0; background: #ffffff; }
.comic-cut img { width: 100%; height: auto; display: block; }

.float-scroll-nav { position: fixed; right: 20px; bottom: 24px; z-index: 80; display: flex; flex-direction: column; gap: 8px; }
.float-circle { width: 42px; height: 42px; border-radius: 50%; background: #ffffff; border: 1px solid #d9d9d9; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12); display: flex; align-items: center; justify-content: center; font-size: 15px; font-weight: 800; color: #333333; cursor: pointer; }

.reader-post { max-width: 690px; margin: 20px auto 64px; display: flex; flex-direction: column; gap: 18px; padding: 0 12px; }
.nv-box { background: #ffffff; border: 1px solid #ebebeb; border-radius: 6px; padding: 20px; }
.next-ep-banner { display: grid; grid-template-columns: 72px 1fr auto; gap: 14px; align-items: center; border: 1px solid #ebebeb; border-radius: 6px; padding: 14px; background: #fafafa; }
.next-ep-banner img { width: 72px; height: 92px; object-fit: cover; border-radius: 4px; }
.ad-box { background: #ffffff; border: 1px solid #ebebeb; border-radius: 6px; padding: 18px; }
.ad-disclosure { font-size: 11px; color: #595959; margin-bottom: 6px; line-height: 1.4; }
.coupang-banner { display: grid; gap: 8px; }
.coupang-cta { display: inline-flex; align-items: center; justify-content: center; background: #111111; color: #ffffff; font-weight: 700; font-size: 13.5px; padding: 9px 15px; border-radius: 4px; }

/* Multi-Zone Coupang Placements: Desktop Left/Right Wings (>=1180px), Mid-Stream, Mobile */
.home-stage { width: 100%; max-width: 1190px; margin: 0 auto; padding: 0 16px; }
.viewer-stage { width: 100%; max-width: 690px; margin: 0 auto; }
.wing-ad { display: none; }
.wing-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 6px; padding: 14px; margin-bottom: 12px; display: grid; gap: 7px; }
.wing-badge { font-size: 11px; font-weight: 800; color: #00a64c; }
.wing-title { font-size: 13.5px; font-weight: 800; color: #111111; line-height: 1.4; }
.wing-reason { font-size: 12px; color: #555555; line-height: 1.45; }
.wing-cta { display: block; text-align: center; background: #111111; color: #ffffff; font-size: 12.5px; font-weight: 700; padding: 8px 10px; border-radius: 4px; }
.wing-guide { font-size: 12px; font-weight: 700; color: #2563eb; text-align: center; }

.infeed-coupang-card { margin: 16px 0; padding: 16px 18px; background: #f9fafb; border: 1px solid #e5e7eb; border-top: 2.5px solid var(--nv-green); border-radius: 6px; }
.mobile-top-coupang { margin: 0 auto 14px; max-width: 690px; padding: 0 12px; }
.mobile-top-coupang .infeed-coupang-card { margin: 0; }
.coupang-strip-box { margin: 22px 0; padding: 18px; background: #f9fafb; border: 1px solid #ebebeb; border-radius: 6px; }
.coupang-strip-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }
.coupang-strip-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.coupang-mini-card { background: #ffffff; border: 1px solid #e5e7eb; border-radius: 6px; padding: 14px; display: flex; flex-direction: column; justify-content: space-between; gap: 8px; }

@media (min-width: 1180px) {
  .viewer-stage { max-width: 1150px; display: grid; grid-template-columns: 200px minmax(0, 690px) 200px; gap: 20px; align-items: start; justify-content: center; }
  .wing-ad { display: block; position: sticky; top: 72px; }
  .mobile-top-coupang { display: none; }
}
@media (min-width: 1420px) {
  .home-stage { max-width: 1420px; display: grid; grid-template-columns: 188px minmax(0, 980px) 188px; gap: 20px; align-items: start; justify-content: center; }
}

.site-footer { margin-top: 48px; border-top: 1px solid #ebebeb; padding: 28px 0 42px; font-size: 12.5px; color: #767676; background: #ffffff; }
.footer-links { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 8px; }
.prose-card { background: #ffffff; border: 1px solid #ebebeb; border-radius: 6px; padding: 24px; margin: 22px 0; }

@media (max-width: 960px) {
  .new-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .wt-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .coupang-strip-grid { grid-template-columns: 1fr; }
  .nv-search-box { display: none; }
}
@media (max-width: 640px) {
  .new-grid { grid-template-columns: 1fr; gap: 16px; }
  .wt-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px 10px; }
  .series-top { grid-template-columns: 1fr; gap: 14px; }
  .series-poster { width: 130px; }
  .ep-item { grid-template-columns: 74px 1fr; }
  .ep-item-right { display: none; }
  .viewer-bar-inner { flex-wrap: wrap; padding: 8px 0; gap: 6px; }
  .viewer-back, .v-btn, .v-ep-select { min-height: 44px; }
  .viewer-h1 { font-size: 14px; }
  .next-ep-banner { grid-template-columns: 60px 1fr; }
  .next-ep-banner a { grid-column: 1 / -1; text-align: center; }
  .float-scroll-nav { right: 10px; bottom: 14px; }
}
@media (max-width: 350px) {
  .wrap, .home-stage { padding: 0 10px; }
  .nv-main-tabs a { padding: 0 10px; font-size: 13.5px; }
}
""".strip()


AD_MANAGER_JS = """
(function () {
  const params = new URLSearchParams(window.location.search);
  const override = params.get("ad_mode");
  const AD_MODE = (override === "adsense" || override === "coupang") ? override : "{DEFAULT_MODE}";
  window.GH_TOON_AD_MODE = AD_MODE;

  const COUPANG_FTC = "{FTC_TEXT}";
  const ADSENSE_PUB = "{PUB_ID}";

  function esc(v) {
    return String(v || "").replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\\"": "&quot;", "'": "&#39;" }[c];
    });
  }

  function renderAdSenseSlot(container, layout) {
    const isArticle = layout === "in-article";
    container.innerHTML =
      '<div class="ad-disclosure">Advertisement</div>' +
      '<ins class="adsbygoogle" style="display:block;min-height:90px;text-align:center;" ' +
      'data-ad-client="' + ADSENSE_PUB + '" data-ad-slot="auto" ' +
      (isArticle ? 'data-ad-layout="in-article" data-ad-format="fluid" ' : 'data-ad-format="auto" data-full-width-responsive="true" ') +
      '></ins>';
    try { if (window.adsbygoogle) window.adsbygoogle.push({}); } catch (e) {}
  }

  function renderCoupangSlot(el) {
    const title = el.getAttribute("data-title") || "";
    const reason = el.getAttribute("data-reason") || "";
    const cta = el.getAttribute("data-cta") || "쿠팡 최저가 보기";
    const url = el.getAttribute("data-url") || "https://shopping.guidehollow.com/";
    const badge = el.getAttribute("data-badge") || "상황 맞춤 추천";
    const guideUrl = el.getAttribute("data-guide-url") || "https://shopping.guidehollow.com/";
    const guideLabel = el.getAttribute("data-guide-label") || "구매 가이드";
    const variant = el.getAttribute("data-gh-slot-variant") || "banner";
    if (variant === "wing") {
      el.innerHTML =
        '<div class="ad-disclosure">' + esc(COUPANG_FTC) + '</div>' +
        '<div class="wing-badge">' + esc(badge) + '</div>' +
        '<div class="wing-title">' + esc(title) + '</div>' +
        '<div class="wing-reason">' + esc(reason) + '</div>' +
        '<a class="wing-cta" href="' + esc(url) + '" target="_blank" rel="noopener noreferrer sponsored">' + esc(cta) + ' ↗</a>' +
        '<a class="wing-guide" href="' + esc(guideUrl) + '" target="_blank" rel="noopener noreferrer">' + esc(guideLabel) + ' →</a>';
      return;
    }
    el.innerHTML =
      '<div class="ad-disclosure">' + esc(COUPANG_FTC) + '</div>' +
      '<div class="coupang-banner">' +
      '  <div style="font-size:12px;font-weight:800;color:#059669;">' + esc(badge) + '</div>' +
      '  <div style="font-size:16px;font-weight:800;color:#111111;">' + esc(title) + '</div>' +
      '  <div style="font-size:13.5px;color:#555555;">' + esc(reason) + '</div>' +
      '  <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:4px;">' +
      '    <a class="coupang-cta" href="' + esc(url) + '" target="_blank" rel="noopener noreferrer sponsored">' + esc(cta) + ' ↗</a>' +
      '    <a style="display:inline-flex;align-items:center;font-size:13px;font-weight:700;color:#2563eb;" href="' + esc(guideUrl) + '" target="_blank" rel="noopener noreferrer">' + esc(guideLabel) + ' →</a>' +
      '  </div>' +
      '</div>';
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (AD_MODE === "adsense") {
      if (!document.querySelector('script[src*="adsbygoogle.js"]')) {
        const s = document.createElement("script");
        s.async = true;
        s.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + ADSENSE_PUB;
        s.crossOrigin = "anonymous";
        document.head.appendChild(s);
      }
      document.querySelectorAll("[data-gh-ad-slot]").forEach(function (el) {
        renderAdSenseSlot(el, el.getAttribute("data-ad-layout") || "auto");
      });
    } else {
      document.querySelectorAll("[data-gh-ad-slot]").forEach(function (el) {
        if (!el.querySelector(".coupang-banner, .wing-cta")) {
          renderCoupangSlot(el);
        }
      });
    }
  });
})();
""".strip()


VIEWER_JS = """
(function () {
  const tabs = document.querySelectorAll(".nv-sub-btn");
  const cards = document.querySelectorAll("[data-genre-item]");
  const searchInput = document.getElementById("wt-search-input");

  function applyFilter() {
    const activeBtn = document.querySelector(".nv-sub-btn.is-active");
    const target = activeBtn ? activeBtn.getAttribute("data-genre") : "all";
    const q = searchInput ? searchInput.value.trim().toLowerCase() : "";
    cards.forEach(function (card) {
      const g = card.getAttribute("data-genre-item") || "";
      const txt = (card.textContent || "").toLowerCase();
      const matchGenre = (target === "all" || target === g);
      const matchSearch = (!q || txt.includes(q));
      card.style.display = (matchGenre && matchSearch) ? "" : "none";
    });
    const newGrid = document.querySelector(".new-grid");
    const newHead = document.getElementById("new-sec-head");
    if (newGrid && newHead) {
      const visNew = Array.from(newGrid.querySelectorAll("[data-genre-item]")).filter(el => el.style.display !== "none").length;
      newGrid.style.display = visNew ? "" : "none";
      newHead.style.display = visNew ? "" : "none";
    }
    const wtGrid = document.querySelector(".wt-grid");
    const emptyMsg = document.getElementById("wt-empty-msg");
    if (wtGrid && emptyMsg) {
      const visWt = Array.from(wtGrid.querySelectorAll("[data-genre-item]")).filter(el => el.style.display !== "none").length;
      emptyMsg.style.display = visWt ? "none" : "block";
    }
  }

  tabs.forEach(function (btn) {
    btn.addEventListener("click", function () {
      tabs.forEach(function (t) { t.classList.remove("is-active"); });
      btn.classList.add("is-active");
      applyFilter();
    });
  });
  if (searchInput) {
    searchInput.addEventListener("input", applyFilter);
  }

  const fill = document.getElementById("read-progress-fill");
  const canvasEl = document.querySelector(".comic-canvas");
  if (fill) {
    window.addEventListener("scroll", function () {
      if (canvasEl) {
        const rect = canvasEl.getBoundingClientRect();
        const total = Math.max(1, canvasEl.offsetHeight - window.innerHeight);
        const passed = Math.max(0, -rect.top);
        fill.style.width = Math.min(100, Math.round((passed / total) * 100)) + "%";
      } else {
        const docH = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
        fill.style.width = Math.min(100, Math.max(0, Math.round((window.scrollY / docH) * 100))) + "%";
      }
    }, { passive: true });
  }
})();
""".strip()


def _head_html(title: str, description: str, canonical: str, og_image: str | None = None) -> str:
    og_img_tag = f'<meta property="og:image" content="{esc(og_image)}" />' if og_image else ""
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}" />
  <link rel="canonical" href="{esc(canonical)}" />
  <meta property="og:type" content="website" />
  <meta property="og:locale" content="ko_KR" />
  <meta property="og:site_name" content="GuideHollow 웹툰" />
  <meta property="og:url" content="{esc(canonical)}" />
  <meta property="og:title" content="{esc(title)}" />
  <meta property="og:description" content="{esc(description)}" />
  {og_img_tag}
  <link rel="stylesheet" href="/assets/style.css" />
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag("js", new Date());
    gtag("config", "{GA4_ID}");
  </script>
</head>"""


def _gnb_html(active: str = "home") -> str:
    return f"""
  <header>
    <div class="nv-top-strip">
      <div class="wrap nv-top-inner">
        <div class="nv-brand-group">
          <a class="nv-logo" href="/">
            <span class="nv-logo-mark">GUIDEHOLLOW</span>
            <span>웹툰</span>
          </a>
          <span class="nv-logo-dot">|</span>
          <a class="nv-logo-sub" href="/studio/">전체 정주행</a>
          <span class="nv-logo-dot">|</span>
          <a class="nv-logo-sub" href="https://shopping.guidehollow.com/" target="_blank" rel="noopener noreferrer">쇼핑가이드</a>
        </div>
        <div class="nv-search-row">
          <div class="nv-search-box">
            <input id="wt-search-input" type="search" placeholder="제목/장르로 검색할 수 있습니다." aria-label="웹툰 검색" />
          </div>
          <a class="nv-creator-btn" href="/episodes/ep01-office-cider/">오늘 1화 보기</a>
        </div>
      </div>
    </div>
    <nav class="nv-main-nav" aria-label="주요 메뉴">
      <div class="wrap nv-main-tabs">
        <a href="/" class="{'is-on' if active == 'home' else ''}">웹툰</a>
        <a href="/studio/" class="{'is-on' if active == 'studio' else ''}">완결·전체</a>
        <a href="/about/" class="{'is-on' if active == 'about' else ''}">연재원칙</a>
        <a href="https://emfls.github.io/kor/util/ssultoon-maker/" target="_blank" rel="noopener noreferrer">사이다 썰툰관</a>
      </div>
    </nav>
    <div class="nv-sub-nav">
      <div class="wrap nv-sub-tabs" role="tablist" aria-label="장르별 보기">
        <button type="button" class="nv-sub-btn is-active" data-genre="all">요일전체</button>
        <button type="button" class="nv-sub-btn" data-genre="office">직장·알바</button>
        <button type="button" class="nv-sub-btn" data-genre="love">연애·관계</button>
        <button type="button" class="nv-sub-btn" data-genre="car">주차·도로</button>
        <button type="button" class="nv-sub-btn" data-genre="mystery">미스터리</button>
        <button type="button" class="nv-sub-btn" data-genre="finance">전세·경제</button>
        <button type="button" class="nv-sub-btn" data-genre="living">중고·공구</button>
        <button type="button" class="nv-sub-btn" data-genre="apartment">층간소음</button>
      </div>
    </div>
  </header>"""


def _footer_html() -> str:
    return f"""
  <footer class="site-footer">
    <div class="wrap">
      <div class="footer-links">
        <a href="/">웹툰 홈</a>
        <a href="/studio/">전체 회차 정주행</a>
        <a href="/about/">연재·제작 안내</a>
        <a href="/privacy/">개인정보처리방침</a>
        <a href="/terms/">이용약관</a>
        <a href="/contact/">문의하기</a>
      </div>
      <div>GuideHollow 웹툰 · 전 회차 세로 스크롤 무료 연재 · 모든 회차 하단에 현실 분쟁 대응 가이드를 함께 수록합니다.</div>
      <div class="ai-disclosure-sm">{AI_IMAGE_NOTICE}</div>
    </div>
  </footer>
  <script src="/assets/ad-manager.js"></script>
  <script src="/assets/viewer.js"></script>"""


def _coupang_item_for(episodes: list[dict], idx: int) -> dict:
    ep = episodes[idx % len(episodes)]
    return ep["coupang"]


def _render_wing_card_html(coup: dict) -> str:
    return (
        f'<div class="wing-card" data-gh-ad-slot="wing" data-gh-slot-variant="wing" '
        f'data-widget-id="{esc(coup["widgetId"])}" data-badge="{esc(coup["badge"])}" '
        f'data-title="{esc(coup["title"])}" data-reason="{esc(coup["reason"])}" '
        f'data-cta="{esc(coup["cta"])}" data-url="{esc(coup["url"])}" '
        f'data-guide-url="{esc(coup["guideUrl"])}" data-guide-label="{esc(coup["guideLabel"])}">'
        f'  <div class="ad-disclosure">{COUPANG_DISCLOSURE}</div>'
        f'  <div class="wing-badge">{esc(coup["badge"])}</div>'
        f'  <div class="wing-title">{esc(coup["title"])}</div>'
        f'  <div class="wing-reason">{esc(coup["reason"])}</div>'
        f'  <a class="wing-cta" href="{esc(coup["url"])}" target="_blank" rel="noopener noreferrer sponsored">{esc(coup["cta"])} ↗</a>'
        f'  <a class="wing-guide" href="{esc(coup["guideUrl"])}" target="_blank" rel="noopener noreferrer">{esc(coup["guideLabel"])} →</a>'
        f'</div>'
    )


def _render_wing_aside(episodes: list[dict], start_idx: int, side: str) -> str:
    cards = "\n".join(
        _render_wing_card_html(_coupang_item_for(episodes, start_idx + offset))
        for offset in range(2)
    )
    aria = "좌측 여백 생활 추천 상품" if side == "left" else "우측 여백 생활 추천 상품"
    return f'<aside class="wing-ad wing-ad-{side}" aria-label="{aria}">\n{cards}\n</aside>'


def _render_infeed_coupang_card(coup: dict, slot_name: str, extra_class: str = "infeed-coupang-card") -> str:
    return (
        f'<aside class="{extra_class}" aria-label="상황 맞춤 생활·상품 추천" '
        f'       data-gh-ad-slot="{esc(slot_name)}" data-ad-kind="contextual" data-ad-layout="in-article" '
        f'       data-widget-id="{esc(coup["widgetId"])}" data-badge="{esc(coup["badge"])}" '
        f'       data-title="{esc(coup["title"])}" data-reason="{esc(coup["reason"])}" '
        f'       data-cta="{esc(coup["cta"])}" data-url="{esc(coup["url"])}" '
        f'       data-guide-url="{esc(coup["guideUrl"])}" data-guide-label="{esc(coup["guideLabel"])}">'
        f'  <div class="ad-disclosure">{COUPANG_DISCLOSURE}</div>'
        f'  <div class="coupang-banner">'
        f'    <div style="font-size:12px;font-weight:800;color:#059669;">{esc(coup["badge"])}</div>'
        f'    <div style="font-size:16px;font-weight:800;color:#111111;">{esc(coup["title"])}</div>'
        f'    <div style="font-size:13.5px;color:#555555;">{esc(coup["reason"])}</div>'
        f'    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:4px;">'
        f'      <a class="coupang-cta" href="{esc(coup["url"])}" target="_blank" rel="noopener noreferrer sponsored">{esc(coup["cta"])} ↗</a>'
        f'      <a style="display:inline-flex;align-items:center;font-size:13px;font-weight:700;color:#2563eb;" href="{esc(coup["guideUrl"])}" target="_blank" rel="noopener noreferrer">{esc(coup["guideLabel"])} →</a>'
        f'    </div>'
        f'  </div>'
        f'</aside>'
    )


def _render_coupang_strip(episodes: list[dict], start_idx: int, heading: str) -> str:
    mini_cards = []
    for offset in range(3):
        coup = _coupang_item_for(episodes, start_idx + offset)
        mini_cards.append(
            f'<div class="coupang-mini-card">'
            f'  <div>'
            f'    <div class="wing-badge" style="margin-bottom:4px;">{esc(coup["badge"])}</div>'
            f'    <div class="wing-title" style="margin-bottom:5px;">{esc(coup["title"])}</div>'
            f'    <div class="wing-reason">{esc(coup["reason"])}</div>'
            f'  </div>'
            f'  <div style="display:grid;gap:5px;margin-top:6px;">'
            f'    <a class="wing-cta" href="{esc(coup["url"])}" target="_blank" rel="noopener noreferrer sponsored">{esc(coup["cta"])} ↗</a>'
            f'    <a class="wing-guide" href="{esc(coup["guideUrl"])}" target="_blank" rel="noopener noreferrer">{esc(coup["guideLabel"])} →</a>'
            f'  </div>'
            f'</div>'
        )
    return (
        f'<section class="coupang-strip-box" aria-label="{esc(heading)}">'
        f'  <div class="coupang-strip-head">'
        f'    <h2 style="margin:0;font-size:16px;font-weight:800;color:#111111;">{esc(heading)}</h2>'
        f'    <span class="ad-disclosure" style="margin:0;">{COUPANG_DISCLOSURE}</span>'
        f'  </div>'
        f'  <div class="coupang-strip-grid">\n{chr(10).join(mini_cards)}\n  </div>'
        f'</section>'
    )


def _render_new_cards(episodes: list[dict]) -> str:
    items = []
    for ep in episodes[:3]:
        eid = ep["id"]
        items.append(
            f'<a class="new-card" href="/episodes/{esc(eid)}/" data-genre-item="{esc(ep["genreKey"])}">'
            f'  <div class="new-thumb">'
            f'    <img src="/assets/toons/{esc(eid)}/cover.svg" alt="{esc(ep["title"])}" loading="eager" width="480" height="620" />'
            f'    <span class="new-badge-circle">{ep["cutCount"]}컷</span>'
            f'  </div>'
            f'  <h3 class="new-title">{esc(ep["title"])}</h3>'
            f'  <div class="new-author">GuideHollow 스튜디오 · {esc(ep["genre"])} · {ep["cutCount"]}컷</div>'
            f'  <p class="new-desc">{esc(ep["hook"])}</p>'
            f'</a>'
        )
    return "\n".join(items)


def _render_poster_cards(episodes: list[dict]) -> str:
    cards = []
    for ep in episodes:
        eid = ep["id"]
        cards.append(
            f'<a class="wt-card" href="/episodes/{esc(eid)}/" data-genre-item="{esc(ep["genreKey"])}">'
            f'  <div class="wt-cover">'
            f'    <img src="/assets/toons/{esc(eid)}/cover.svg" alt="{esc(ep["title"])}" loading="lazy" width="480" height="620" />'
            f'  </div>'
            f'  <h3 class="wt-title">{esc(ep["title"])}</h3>'
            f'  <div class="wt-meta">{esc(ep["genre"])} · {ep["cutCount"]}컷 · 무료연재</div>'
            f'</a>'
        )
    return "\n".join(cards)


def _render_episode_table(episodes: list[dict]) -> str:
    rows = []
    for ep in episodes:
        eid = ep["id"]
        rows.append(
            f'<a class="ep-item" href="/episodes/{esc(eid)}/" data-genre-item="{esc(ep["genreKey"])}">'
            f'  <div class="ep-item-thumb"><img src="/assets/toons/{esc(eid)}/cover.svg" alt="{esc(ep["title"])}" loading="lazy" /></div>'
            f'  <div>'
            f'    <div class="ep-item-name">{ep["episodeNo"]:02d}화 {esc(ep["title"])}</div>'
            f'    <div class="ep-item-sub">26.11.18 &nbsp;·&nbsp; {ep["cutCount"]}컷 &nbsp;·&nbsp; 무료정주행</div>'
            f'  </div>'
            f'  <div class="ep-item-right">{esc(ep["genre"])}</div>'
            f'</a>'
        )
    return "\n".join(rows)


def build_home_html(episodes: list[dict]) -> str:
    top = episodes[0]
    total_cuts = sum(ep["cutCount"] for ep in episodes)
    head = _head_html(
        "GuideHollow 웹툰 — 사이다 실화 연재관",
        f"네이버 웹툰 스타일 세로 스크롤 {len(episodes)}화(총 {total_cuts}컷) 사이다 실화 웹툰을 무료로 감상하세요.",
        f"{SITE_URL}/",
        f"{SITE_URL}/assets/toons/{top['id']}/cover.svg",
    )
    return f"""{head}
<body>
{_gnb_html("home")}
  <div class="home-stage">
{_render_wing_aside(episodes, 0, "left")}
  <main style="min-width:0;">
    <div id="new-sec-head" class="nv-sec-title-row">
      <h1 class="nv-sec-title">이달의 신규 웹툰</h1>
      <a class="nv-sec-more" href="/studio/">신작웹툰 더보기 &gt;</a>
    </div>
    <section class="new-grid" aria-label="이달의 신규 웹툰">
{_render_new_cards(episodes)}
    </section>

{_render_coupang_strip(episodes, 0, "웹툰 상황별 생활·데스크 인기템 추천")}

    <div class="nv-sec-title-row">
      <h2 class="nv-sec-title">요일별 전체 웹툰</h2>
      <span class="nv-sec-more">에피소드 길이별 맞춤 컷수(12~18컷) · 전 회차 무료</span>
    </div>
    <section class="wt-grid" aria-label="전체 웹툰 포스터">
{_render_poster_cards(episodes)}
    </section>
    <div id="wt-empty-msg" style="display:none;padding:28px 16px;text-align:center;color:#595959;border:1px dashed #d1d5db;border-radius:6px;margin-top:12px;font-size:14px;">조건에 맞는 웹툰이 없습니다. 상단 '요일전체' 탭을 눌러 전체 작품을 확인하세요.</div>

{_render_coupang_strip(episodes, 4, "자취·주거·일상 예방 필수품 모아보기")}

    <section id="episode-list-anchor" class="series-home-box" aria-label="대표 연재작 회차 목록">
      <div class="series-top">
        <div class="series-poster">
          <img src="/assets/toons/{esc(top['id'])}/cover.svg" alt="{esc(top['title'])}" width="480" height="620" />
        </div>
        <div>
          <h2 class="series-h2">오늘의 베스트 사이다 썰툰 모음집</h2>
          <div class="series-authors"><strong>GuideHollow 편집팀</strong> · 글 / <strong>AI 웹툰 스튜디오</strong> · 그림 &nbsp;|&nbsp; 스토리 맞춤 12~18컷 무료 연재</div>
          <p class="series-synop">{esc(top['summary'])} 직장·연애·주차·전세·중고거래 등 현실에서 누구나 겪는 답답한 상황을 이야기의 호흡에 맞춘 맞춤 컷수로 풀어낸 세로 웹툰 모음입니다.</p>
          <div class="series-tags">
            <span class="series-tag">#사이다참교육</span>
            <span class="series-tag">#직장실화</span>
            <span class="series-tag">#스토리별가변컷</span>
            <span class="series-tag">#전세사기방어</span>
            <span class="series-tag">#무료정주행</span>
          </div>
          <div class="series-cta-row">
            <a class="btn-first-ep" href="/episodes/{esc(top['id'])}/">첫 화 보기</a>
            <a class="btn-sub-outline" href="/studio/">전체 {len(episodes)}작 모아보기</a>
            <a class="btn-sub-outline" href="/about/">연재 안내</a>
          </div>
        </div>
      </div>
      <div style="font-size:14px;font-weight:700;margin-bottom:10px;">총 {len(episodes)}화 · 누적 {total_cuts}컷</div>
      <div class="ep-list">
{_render_episode_table(episodes)}
      </div>
    </section>
  </main>
{_render_wing_aside(episodes, 5, "right")}
  </div>
{_footer_html()}
</body>
</html>"""


def build_studio_archive_html(episodes: list[dict]) -> str:
    total_cuts = sum(ep["cutCount"] for ep in episodes)
    head = _head_html(
        "완결·전체 정주행 모아보기 | GuideHollow 웹툰",
        f"GuideHollow 오리지널 {len(episodes)}화 {total_cuts}컷 세로 웹툰을 한눈에 모아보고 무료 감상하세요.",
        f"{SITE_URL}/studio/",
    )
    return f"""{head}
<body>
{_gnb_html("studio")}
  <main class="wrap">
    <div class="nv-sec-title-row">
      <h1 class="nv-sec-title">전체 완결·인기 웹툰 모아보기 ({len(episodes)}작 · 총 {total_cuts}컷)</h1>
    </div>
{_render_coupang_strip(episodes, 1, "정주행 독자들이 자주 찾는 생활·가전 추천")}
    <section class="wt-grid" style="margin-bottom:28px;">
{_render_poster_cards(episodes)}
    </section>
    <div class="ep-list" style="border-top:1px solid #111111;">
{_render_episode_table(episodes)}
    </div>
  </main>
{_footer_html()}
</body>
</html>"""


def build_episode_html(idx: int, ep: dict, episodes: list[dict]) -> str:
    eid = ep["id"]
    prev_ep = episodes[idx - 1] if idx > 0 else episodes[-1]
    next_ep = episodes[idx + 1] if idx + 1 < len(episodes) else episodes[0]
    total = len(ep["panels"])
    mobile_top_slot = _coupang_item_for(episodes, idx + 4)
    mid_slot_a = ep["coupang"]
    mid_slot_b = _coupang_item_for(episodes, idx + 2)
    end_slot = _coupang_item_for(episodes, idx + 6)
    ep_options = "\n".join(
        f'<option value="/episodes/{esc(item["id"])}/"{" selected" if item["id"] == eid else ""}>{item["episodeNo"]:02d}화 ({item["cutCount"]}컷) · {esc(item["genre"])}</option>'
        for item in episodes
    )
    prev_ctrl = (
        '<span class="v-btn is-disabled" aria-disabled="true">◀ 처음</span>'
        if idx == 0
        else f'<a class="v-btn" href="/episodes/{esc(prev_ep["id"])}/">◀ 이전화</a>'
    )

    cuts_html = []
    for c_idx, p in enumerate(ep["panels"], start=1):
        cuts_html.append(
            f'<div class="comic-cut" data-cut-num="{c_idx}">'
            f'  <img src="/assets/toons/{esc(eid)}/cut-{c_idx:02d}.svg" alt="{esc(ep["title"])} {c_idx}컷 - {esc(p["line"])}" width="690" height="1120" loading="{"eager" if c_idx <= 3 else "lazy"}" />'
            f'</div>'
        )
        if c_idx == 4:
            cuts_html.append(_render_infeed_coupang_card(mid_slot_a, "ep-mid-cut4"))
        elif c_idx == 9 and total >= 11:
            cuts_html.append(_render_infeed_coupang_card(mid_slot_b, "ep-mid-cut9"))

    checklist_html = "\n".join(f"<li style='margin-bottom:6px;'>{esc(item)}</li>" for item in ep["checklist"])
    head = _head_html(
        f"{ep['episodeNo']:02d}화 {ep['title']} | GuideHollow 웹툰",
        f"{ep['hook']} {ep['summary']}",
        f"{SITE_URL}/episodes/{eid}/",
        f"{SITE_URL}/assets/toons/{eid}/cover.svg",
    )

    return f"""{head}
<body class="viewer-body">
  <div class="read-progress"><div id="read-progress-fill" class="read-progress-fill"></div></div>
  <header class="viewer-bar">
    <div class="wrap viewer-bar-inner">
      <div class="viewer-title-group">
        <a class="viewer-back" href="/">← 목록</a>
        <h1 class="viewer-h1">{ep['episodeNo']:02d}화 {esc(ep['title'])}</h1>
      </div>
      <div class="viewer-controls">
        <select class="v-ep-select" aria-label="회차 빠른 이동" onchange="if(this.value)location.href=this.value">
{ep_options}
        </select>
        {prev_ctrl}
        <a class="v-btn primary" href="/episodes/{esc(next_ep['id'])}/">다음화 ▶</a>
      </div>
    </div>
  </header>

  <main>
    <div class="ep-head-meta">
      <h2>{ep['episodeNo']:02d}화. {esc(ep['title'])}</h2>
      <p>{esc(ep['hook'])}</p>
      <div style="margin-top:6px;font-size:12.5px;color:#008f42;font-weight:700;">{ep['episodeNo']:02d} / {len(episodes)}화 · {esc(ep['genre'])} · 총 {total}컷 · 무료 정주행</div>
      <div class="ai-disclosure-sm">{AI_IMAGE_NOTICE}</div>
    </div>

    <div class="mobile-top-coupang">
      {_render_infeed_coupang_card(mobile_top_slot, "ep-mobile-top", extra_class="infeed-coupang-card")}
    </div>

    <div class="viewer-stage">
{_render_wing_aside(episodes, idx + 1, "left")}
      <div style="min-width:0;">
        <article class="comic-canvas" aria-label="웹툰 본문 세로 스크롤">
{chr(10).join(cuts_html)}
        </article>
      </div>
{_render_wing_aside(episodes, idx + 5, "right")}
    </div>

    <div class="float-scroll-nav" aria-label="스크롤 이동 버튼">
      <button type="button" class="float-circle" aria-label="맨 위로" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">∧</button>
      <button type="button" class="float-circle" aria-label="아래로" onclick="window.scrollTo({{top:document.body.scrollHeight,behavior:'smooth'}})">∨</button>
    </div>

    <section class="reader-post" aria-label="다음화, 생활 추천 및 실전 해결 가이드">
      <div class="next-ep-banner">
        <img src="/assets/toons/{esc(next_ep['id'])}/cover.svg" alt="{esc(next_ep['title'])}" />
        <div>
          <div style="font-size:12px;font-weight:800;color:#00b853;">다음화 · {next_ep['episodeNo']:02d}화 ({next_ep['cutCount']}컷)</div>
          <div style="font-size:15px;font-weight:800;color:#111111;margin:3px 0;">{esc(next_ep['title'])}</div>
          <div style="font-size:13px;color:#666666;">{esc(next_ep['hook'])}</div>
        </div>
        <a class="v-btn primary" href="/episodes/{esc(next_ep['id'])}/">다음화 보기 ▶</a>
      </div>

      {_render_infeed_coupang_card(end_slot, "ep-bottom", extra_class="ad-box")}

      <div class="nv-box">
        <h3 style="margin:0 0 8px;font-size:16px;font-weight:800;">{esc(ep['guideTitle'])}</h3>
        <p style="margin:0 0 12px;font-size:14px;color:#444444;">{esc(ep['guideBody'])}</p>
        <div style="font-size:14px;font-weight:800;margin-bottom:6px;color:#00b853;">실전 확인 체크리스트</div>
        <ul style="margin:0;padding-left:18px;font-size:13.5px;color:#333333;">
{checklist_html}
        </ul>
        <div class="ai-disclosure-sm" style="margin-top:12px;">{AI_IMAGE_NOTICE}</div>
      </div>
    </section>
  </main>

  <script src="/assets/ad-manager.js"></script>
  <script src="/assets/viewer.js"></script>
</body>
</html>"""


def build_policy_page(slug: str, title: str, heading: str, body_html: str) -> str:
    head = _head_html(f"{title} | GuideHollow 웹툰", title, f"{SITE_URL}/{slug}/")
    return f"""{head}
<body>
{_gnb_html(slug if slug == 'about' else '')}
  <main class="wrap">
    <article class="prose-card">
      <h1 style="margin-top:0;">{esc(heading)}</h1>
      {body_html}
    </article>
  </main>
{_footer_html()}
</body>
</html>"""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_site(ad_mode: str = "coupang") -> dict:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True, exist_ok=True)

    episodes = prepare_episodes()
    total_cuts = sum(ep["cutCount"] for ep in episodes)

    write_text(DIST / "CNAME", "toon.guidehollow.com\n")
    write_text(
        DIST / "_headers",
        "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n",
    )
    write_text(DIST / "ads.txt", ADSENSE_TXT)
    write_text(
        DIST / "robots.txt",
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n",
    )
    write_text(DIST / "assets" / "style.css", STYLE_CSS + "\n")
    write_text(
        DIST / "assets" / "ad-manager.js",
        AD_MANAGER_JS.replace("{DEFAULT_MODE}", ad_mode)
        .replace("{FTC_TEXT}", COUPANG_DISCLOSURE)
        .replace("{PUB_ID}", ADSENSE_PUB)
        + "\n",
    )
    write_text(DIST / "assets" / "viewer.js", VIEWER_JS + "\n")
    write_text(
        DIST / "assets" / "episodes.json",
        json.dumps({"episodes": episodes}, ensure_ascii=False, indent=2) + "\n",
    )

    svg_count = 0
    sitemap_urls = [f"{SITE_URL}/", f"{SITE_URL}/studio/", f"{SITE_URL}/about/"]
    for idx, ep in enumerate(episodes):
        eid = ep["id"]
        write_text(DIST / "assets" / "toons" / eid / "cover.svg", render_cover_svg(ep))
        svg_count += 1
        total = len(ep["panels"])
        for c_idx, panel in enumerate(ep["panels"], start=1):
            write_text(
                DIST / "assets" / "toons" / eid / f"cut-{c_idx:02d}.svg",
                render_panel_svg(ep, c_idx, panel, total),
            )
            svg_count += 1
        write_text(DIST / "episodes" / eid / "index.html", build_episode_html(idx, ep, episodes))
        sitemap_urls.append(f"{SITE_URL}/episodes/{eid}/")

    write_text(DIST / "index.html", build_home_html(episodes))
    write_text(DIST / "studio" / "index.html", build_studio_archive_html(episodes))
    write_text(
        DIST / "about" / "index.html",
        build_policy_page(
            "about",
            "연재·편집 원칙",
            "GuideHollow 웹툰 연재·편집 원칙",
            f"<p>전 에피소드는 직장·계약·중고거래·이웃 분쟁 등 일상에서 벌어지는 실제 고민을 이야기 길이에 따라 12~18컷 세로 스크롤 웹툰으로 각색(현재 {len(episodes)}화 총 {total_cuts}컷)하고, 하단에 법적 대응과 생활 체크리스트를 함께 수록합니다.</p>"
            "<p>모든 웹툰 작화는 AI 생성 일러스트와 한국어 웹툰 식자 조판을 결합해 제작되며, 별도 회원가입·댓글·평점 없이 모바일과 PC 모두에서 끊김 없는 무료 정주행을 즐길 수 있습니다.</p>",
        ),
    )
    write_text(
        DIST / "privacy" / "index.html",
        build_policy_page(
            "privacy",
            "개인정보처리방침",
            "개인정보처리방침",
            "<p>본 웹툰 연재관은 방문자 통계를 위해 Google Analytics(GA4)를 사용하며 별도의 회원가입이나 개인 식별 정보를 저장하지 않습니다.</p>",
        ),
    )
    write_text(
        DIST / "terms" / "index.html",
        build_policy_page(
            "terms",
            "이용약관",
            "이용약관",
            "<p>수록된 모든 웹툰 회차와 가이드는 일상 정보 공유 목적이며 구체적 법률 사건은 관할 기관 또는 전문가 확인을 권장합니다.</p>",
        ),
    )
    write_text(
        DIST / "contact" / "index.html",
        build_policy_page(
            "contact",
            "문의하기",
            "문의하기",
            "<p>웹툰 제보 및 콘텐츠 관련 문의는 shopping.guidehollow.com 안내 채널을 통해 접수하실 수 있습니다.</p>",
        ),
    )

    sitemap_body = "\n".join(f"  <url><loc>{esc(u)}</loc></url>" for u in sitemap_urls)
    write_text(
        DIST / "sitemap.xml",
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sitemap_body}\n</urlset>\n',
    )
    return {"episodes": len(episodes), "svgs": svg_count, "urls": len(sitemap_urls), "cuts": total_cuts}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ad-mode", choices=["coupang", "adsense"], default="coupang")
    args = parser.parse_args()
    stats = build_site(ad_mode=args.ad_mode)
    print(f"BUILT_NAVER_STYLE_PORTAL episodes={stats['episodes']} cuts={stats['cuts']} svgs={stats['svgs']} urls={stats['urls']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
