#!/usr/bin/env python3
"""Static webtoon portal builder for toon.guidehollow.com (18-cut Naver Webtoon style)."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import shutil
import sys
import textwrap

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from content.episodes import EPISODES  # noqa: E402

DIST = ROOT / "dist"
SITE_URL = "https://toon.guidehollow.com"
ADSENSE_PUB = "ca-pub-8830524482034754"
ADSENSE_TXT = "google.com, pub-8830524482034754, DIRECT, f08c47fec0942fa0\n"
GA4_ID = "G-QP5Q67GE5B"
COUPANG_DISCLOSURE = "이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."

DISALLOWED_EDITOR_MARKERS = [
    "미리보기",
    "생성하기",
    "장면 커스텀",
    "DIY",
    "대사 입력",
    "말풍선 문구",
    "에디터 스튜디오",
]

THEME_PALETTE = {
    "office": {"sky1": "#13293d", "sky2": "#1b4965", "accent": "#00dc64", "glow": "#38bdf8", "suit": "#243b53", "villain": "#991b1b"},
    "love": {"sky1": "#2e1065", "sky2": "#4c1d95", "accent": "#fb7185", "glow": "#fda4af", "suit": "#be185d", "villain": "#6d28d9"},
    "car": {"sky1": "#0f172a", "sky2": "#1e3a8a", "accent": "#f59e0b", "glow": "#fde047", "suit": "#1d4ed8", "villain": "#374151"},
    "mystery": {"sky1": "#05070b", "sky2": "#1f2937", "accent": "#e11d48", "glow": "#f43f5e", "suit": "#334155", "villain": "#111827"},
    "finance": {"sky1": "#064e3b", "sky2": "#047857", "accent": "#10b981", "glow": "#6ee7b7", "suit": "#0f766e", "villain": "#7c2d12"},
    "living": {"sky1": "#1e293b", "sky2": "#334155", "accent": "#0ea5e9", "glow": "#7dd3fc", "suit": "#0369a1", "villain": "#9a3412"},
    "apartment": {"sky1": "#1c1917", "sky2": "#44403c", "accent": "#f97316", "glow": "#fdba74", "suit": "#292524", "villain": "#7f1d1d"},
}


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def wrap_ko(text: str, width: int = 17, max_lines: int = 3) -> list[str]:
    clean = " ".join(str(text or "").split())
    if not clean:
        return []
    lines = textwrap.wrap(clean, width=width, break_long_words=True)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        if len(lines[-1]) > 2:
            lines[-1] = lines[-1][:-1] + "…"
    return lines


def _draw_character(
    cx: float,
    cy: float,
    scale: float,
    shirt_color: str,
    hair_color: str,
    emotion: str,
    is_villain: bool = False,
) -> str:
    """Render an expressive flat Korean webtoon bust/upper body inside SVG."""
    parts = [f'<g transform="translate({cx},{cy}) scale({scale})">']
    # Shoulders & Torso
    parts.append(
        f'<path d="M-85 155 C-82 70 -48 45 0 45 C48 45 82 70 85 155 Z" '
        f'fill="{shirt_color}" stroke="#0b0f19" stroke-width="4.5"/>'
    )
    parts.append('<path d="M-24 46 L0 86 L24 46" fill="#ffffff" stroke="#0b0f19" stroke-width="3.5"/>')
    if is_villain:
        parts.append('<path d="M-8 68 L8 68 L14 145 L-14 145 Z" fill="#dc2626" stroke="#0b0f19" stroke-width="3"/>')
    else:
        parts.append('<path d="M-7 72 L7 72 L10 140 L-10 140 Z" fill="#00dc64" stroke="#0b0f19" stroke-width="3"/>')

    # Neck
    parts.append('<rect x="-15" y="16" width="30" height="34" rx="10" fill="#fde2c8" stroke="#0b0f19" stroke-width="3.5"/>')
    # Back hair / Ears
    parts.append(f'<ellipse cx="-48" cy="-24" rx="10" ry="15" fill="#fbd4b2" stroke="#0b0f19" stroke-width="3.5"/>')
    parts.append(f'<ellipse cx="48" cy="-24" rx="10" ry="15" fill="#fbd4b2" stroke="#0b0f19" stroke-width="3.5"/>')
    parts.append(f'<circle cx="0" cy="-42" r="54" fill="{hair_color}" stroke="#0b0f19" stroke-width="4"/>')
    # Face
    parts.append('<path d="M-46 -40 C-48 8 -26 30 0 32 C26 30 48 8 46 -40 C44 -72 -44 -72 -46 -40 Z" fill="#fde2c8" stroke="#0b0f19" stroke-width="4"/>')
    # Forehead Bangs
    if is_villain:
        parts.append(
            f'<path d="M-50 -46 C-42 -84 42 -84 50 -46 C36 -56 20 -58 6 -44 C-8 -60 -28 -58 -50 -46 Z" '
            f'fill="{hair_color}" stroke="#0b0f19" stroke-width="4"/>'
        )
    else:
        parts.append(
            f'<path d="M-50 -44 C-46 -86 46 -86 50 -44 C34 -60 12 -52 0 -38 C-14 -54 -36 -58 -50 -44 Z" '
            f'fill="{hair_color}" stroke="#0b0f19" stroke-width="4"/>'
        )

    # Eyes & Brows
    if emotion in ("angry", "scary"):
        parts.append('<path d="M-34 -42 L-10 -34 M10 -34 L34 -42" stroke="#0b0f19" stroke-width="4.5" stroke-linecap="round"/>')
        parts.append('<ellipse cx="-20" cy="-26" rx="7" ry="8" fill="#0b0f19"/>')
        parts.append('<ellipse cx="20" cy="-26" rx="7" ry="8" fill="#0b0f19"/>')
        parts.append('<circle cx="-18" cy="-28" r="2.2" fill="#ffffff"/>')
        parts.append('<circle cx="22" cy="-28" r="2.2" fill="#ffffff"/>')
        parts.append('<path d="M-16 8 Q0 -6 16 8" fill="#991b1b" stroke="#0b0f19" stroke-width="3.5"/>')
        parts.append('<path d="M36 -58 L44 -50 M44 -58 L36 -50" stroke="#ef4444" stroke-width="3.5" stroke-linecap="round"/>')
    elif emotion == "shocked":
        parts.append('<path d="M-32 -46 Q-20 -54 -8 -44 M8 -44 Q20 -54 32 -46" fill="none" stroke="#0b0f19" stroke-width="4"/>')
        parts.append('<circle cx="-20" cy="-26" r="10" fill="#ffffff" stroke="#0b0f19" stroke-width="3.5"/>')
        parts.append('<circle cx="20" cy="-26" r="10" fill="#ffffff" stroke="#0b0f19" stroke-width="3.5"/>')
        parts.append('<circle cx="-20" cy="-26" r="3.5" fill="#0b0f19"/>')
        parts.append('<circle cx="20" cy="-26" r="3.5" fill="#0b0f19"/>')
        parts.append('<ellipse cx="0" cy="8" rx="12" ry="10" fill="#7f1d1d" stroke="#0b0f19" stroke-width="3.5"/>')
        parts.append('<path d="M-42 -58 C-48 -42 -36 -42 -42 -58 Z" fill="#60a5fa" stroke="#0b0f19" stroke-width="2"/>')
    elif emotion == "crying":
        parts.append('<path d="M-34 -34 L-12 -42 M12 -42 L34 -34" stroke="#0b0f19" stroke-width="4" stroke-linecap="round"/>')
        parts.append('<path d="M-28 -24 Q-18 -30 -10 -24 M10 -24 Q18 -30 28 -24" fill="none" stroke="#0b0f19" stroke-width="4"/>')
        parts.append('<path d="M-26 -18 Q-28 0 -22 14 M26 -18 Q28 0 22 14" stroke="#38bdf8" stroke-width="5" stroke-linecap="round" opacity="0.85"/>')
        parts.append('<path d="M-14 12 Q0 2 14 12" fill="none" stroke="#0b0f19" stroke-width="4" stroke-linecap="round"/>')
    elif emotion in ("calm_smirk", "determined"):
        parts.append('<path d="M-32 -40 L-10 -36 M10 -36 L32 -40" stroke="#0b0f19" stroke-width="4" stroke-linecap="round"/>')
        parts.append('<ellipse cx="-20" cy="-26" rx="7.5" ry="6.5" fill="#0b0f19"/>')
        parts.append('<ellipse cx="20" cy="-26" rx="7.5" ry="6.5" fill="#0b0f19"/>')
        parts.append('<circle cx="-18" cy="-28" r="2.4" fill="#ffffff"/>')
        parts.append('<circle cx="22" cy="-28" r="2.4" fill="#ffffff"/>')
        parts.append('<path d="M-12 6 Q2 16 18 4" fill="none" stroke="#0b0f19" stroke-width="4" stroke-linecap="round"/>')
    else:  # smug
        parts.append('<path d="M-34 -42 Q-20 -48 -8 -38 M8 -38 Q22 -48 34 -42" fill="none" stroke="#0b0f19" stroke-width="4"/>')
        parts.append('<path d="M-28 -26 Q-18 -30 -10 -24 M10 -24 Q18 -30 28 -26" fill="none" stroke="#0b0f19" stroke-width="4"/>')
        parts.append('<circle cx="-19" cy="-25" r="4" fill="#0b0f19"/>')
        parts.append('<circle cx="19" cy="-25" r="4" fill="#0b0f19"/>')
        parts.append('<path d="M-10 8 Q8 16 20 2" fill="none" stroke="#0b0f19" stroke-width="4" stroke-linecap="round"/>')

    # Nose
    parts.append('<path d="M-2 -12 L2 -2 L-4 0" fill="none" stroke="#0b0f19" stroke-width="2.5" stroke-linecap="round"/>')
    parts.append("</g>")
    return "\n".join(parts)


def _draw_backdrop(scene: str, w: int, h: int, pal: dict[str, str]) -> str:
    """Render an atmospheric Korean webtoon scene backdrop."""
    elems = [
        f'<defs><linearGradient id="bg-{scene}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{pal["sky1"]}"/><stop offset="100%" stop-color="{pal["sky2"]}"/></linearGradient>'
        f'<radialGradient id="glow-{scene}" cx="50%" cy="42%" r="52%">'
        f'<stop offset="0%" stop-color="{pal["glow"]}" stop-opacity="0.34"/>'
        f'<stop offset="100%" stop-color="{pal["sky1"]}" stop-opacity="0"/></radialGradient></defs>',
        f'<rect width="{w}" height="{h}" fill="url(#bg-{scene})"/>',
        f'<rect width="{w}" height="{h}" fill="url(#glow-{scene})"/>',
    ]
    if scene in ("office", "police", "realestate"):
        # Tall windows + blinds + desk silhouette
        for x in range(40, w - 60, 120):
            elems.append(f'<rect x="{x}" y="90" width="84" height="240" rx="4" fill="#e2e8f0" opacity="0.14"/>')
            for y in range(110, 320, 26):
                elems.append(f'<line x1="{x}" y1="{y}" x2="{x+84}" y2="{y}" stroke="#0f172a" stroke-width="3" opacity="0.25"/>')
        elems.append(f'<rect x="0" y="{h-170}" width="{w}" height="170" fill="#0f172a" opacity="0.55"/>')
    elif scene in ("messenger",):
        # Digital chat glow grid + floating chat bubbles
        for y in range(110, h - 180, 95):
            elems.append(f'<rect x="44" y="{y}" width="260" height="42" rx="18" fill="#fef08a" opacity="0.18"/>')
            elems.append(f'<rect x="{w-310}" y="{y+36}" width="266" height="42" rx="18" fill="#38bdf8" opacity="0.18"/>')
    elif scene in ("parking", "apartment"):
        # Concrete pillars & caution yellow/black stripes
        elems.append(f'<rect x="30" y="100" width="76" height="{h-180}" fill="#000000" opacity="0.28"/>')
        elems.append(f'<rect x="{w-106}" y="100" width="76" height="{h-180}" fill="#000000" opacity="0.28"/>')
        elems.append(f'<rect x="0" y="{h-120}" width="{w}" height="28" fill="#facc15" opacity="0.24"/>')
    elif scene in ("darkroom",):
        # Noir speed/tension lines
        for deg in range(0, 360, 18):
            elems.append(
                f'<line x1="{w//2}" y1="{h//2}" x2="{w//2 + 520}" y2="{h//2}" '
                f'stroke="#f43f5e" stroke-width="2" opacity="0.22" transform="rotate({deg} {w//2} {h//2})"/>'
            )
    elif scene in ("wedding", "cafe", "celebration"):
        # Warm bokeh ceiling lights
        for bx, by, br in [(110, 140, 26), (260, 110, 18), (450, 130, 30), (610, 150, 22), (180, 220, 14), (540, 230, 20)]:
            if bx < w:
                elems.append(f'<circle cx="{bx}" cy="{by}" r="{br}" fill="#fde68a" opacity="0.28"/>')
    else:
        for i in range(6):
            elems.append(f'<circle cx="{(i*145)%w + 40}" cy="{130 + (i%3)*70}" r="42" fill="#ffffff" opacity="0.06"/>')
    return "\n".join(elems)


def _draw_comic_lines(cx: float, cy: float, color: str = "#ffffff", count: int = 24) -> str:
    lines = []
    for i in range(count):
        ang = i * (360 / count)
        lines.append(
            f'<line x1="{cx+140}" y1="{cy}" x2="{cx+460}" y2="{cy}" '
            f'stroke="{color}" stroke-width="3.5" opacity="0.35" transform="rotate({ang} {cx} {cy})"/>'
        )
    return "\n".join(lines)


def _draw_bubble(
    x: int,
    y: int,
    w: int,
    speaker: str,
    text: str,
    width_chars: int = 17,
    style: str = "speech",
    tail_dir: str = "down",
) -> str:
    wrapped = wrap_ko(text, width=width_chars, max_lines=3)
    bh = max(92, 46 + len(wrapped) * 34)
    rx = 26 if style != "narration" else 10
    bg = "#ffffff" if style != "narration" else "#fef9c3"
    stroke = "#0b0f19"
    parts = ['<g>']
    # Drop shadow
    parts.append(f'<rect x="{x+5}" y="{y+6}" width="{w}" height="{bh}" rx="{rx}" fill="#0b0f19" opacity="0.28"/>')
    # Main bubble box
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{bh}" rx="{rx}" fill="{bg}" stroke="{stroke}" stroke-width="4.5"/>')
    if style == "speech":
        tx = x + (w // 3 if tail_dir == "left" else (2 * w // 3 if tail_dir == "right" else w // 2))
        if tail_dir == "up":
            parts.append(f'<polygon points="{tx-16},{y} {tx+4},{y-26} {tx+18},{y}" fill="{bg}" stroke="{stroke}" stroke-width="4" stroke-linejoin="round"/>')
            parts.append(f'<rect x="{tx-14}" y="{y-2}" width="30" height="8" fill="{bg}"/>')
        else:
            parts.append(f'<polygon points="{tx-18},{y+bh} {tx+4},{y+bh+28} {tx+18},{y+bh}" fill="{bg}" stroke="{stroke}" stroke-width="4" stroke-linejoin="round"/>')
            parts.append(f'<rect x="{tx-15}" y="{y+bh-5}" width="31" height="9" fill="{bg}"/>')
    # Speaker tag pill
    parts.append(f'<rect x="{x+18}" y="{y-16}" width="{min(w-36, max(110, len(speaker)*16 + 34))}" height="32" rx="16" fill="#0b0f19"/>')
    parts.append(f'<text x="{x+34}" y="{y+6}" font-family="Pretendard, Apple SD Gothic Neo, sans-serif" font-size="16" font-weight="800" fill="#00dc64">{esc(speaker)}</text>')
    # Dialogue lines
    for idx, line in enumerate(wrapped):
        ty = y + 54 + idx * 34
        parts.append(
            f'<text x="{x + w//2}" y="{ty}" text-anchor="middle" '
            f'font-family="Pretendard, Apple SD Gothic Neo, sans-serif" font-size="23" font-weight="800" fill="#0b0f19">{esc(line)}</text>'
        )
    parts.append("</g>")
    return "\n".join(parts)


def render_cover_svg(ep: dict) -> str:
    """Render a 480x640 3:4 Naver Webtoon vertical series poster cover."""
    w, h = 480, 640
    pal = THEME_PALETTE.get(ep["genreKey"], THEME_PALETTE["office"])
    rank = ep["episodeNo"]
    title_lines = wrap_ko(ep["title"], width=15, max_lines=3)
    body = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(ep["title"])}">',
        _draw_backdrop(ep["genreKey"], w, h, pal),
        _draw_comic_lines(w // 2, 270, pal["glow"], 20),
        # Villain ominous shadow behind
        _draw_character(335, 250, 0.92, pal["villain"], "#1f2937", "smug", is_villain=True),
        # Hero confident foreground
        _draw_character(170, 290, 1.18, pal["suit"], "#0f172a", "determined", is_villain=False),
        # Bottom dark cinematic gradient scrim for title punch (single crisp corner layer from HTML overlay)
        '<defs><linearGradient id="cover-scrim" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="#05070b" stop-opacity="0"/>'
        '<stop offset="35%" stop-color="#05070b" stop-opacity="0.62"/>'
        '<stop offset="100%" stop-color="#05070b" stop-opacity="0.96"/>'
        '</linearGradient></defs>',
        '<rect x="0" y="290" width="480" height="350" fill="url(#cover-scrim)"/>',
        # Genre pill
        f'<rect x="20" y="412" width="184" height="30" rx="15" fill="{pal["accent"]}"/>',
        f'<text x="112" y="432" text-anchor="middle" font-family="Pretendard, Apple SD Gothic Neo, sans-serif" font-size="14" font-weight="900" fill="#05070b">{esc(ep["genre"])}</text>',
    ]
    for idx, line in enumerate(title_lines):
        body.append(
            f'<text x="22" y="{482 + idx * 36}" font-family="Pretendard, Apple SD Gothic Neo, sans-serif" '
            f'font-size="25" font-weight="900" fill="#ffffff" stroke="#000000" stroke-width="1">{esc(line)}</text>'
        )
    body.append(
        f'<text x="22" y="612" font-family="Pretendard, Apple SD Gothic Neo, sans-serif" font-size="15" font-weight="800" fill="#fde047">★ {esc(ep["rating"])} · 조회 {esc(ep["viewsLabel"])} · 클릭해서 결말 보기 ▶</text>'
    )
    body.append("</svg>")
    return "\n".join(body)


def render_panel_svg(ep: dict, idx: int, panel: dict, total: int) -> str:
    """Render a full 720x880 Korean vertical webtoon cut with cinematic camera framings."""
    w, h = 720, 880
    scene = panel["scene"]
    pal = THEME_PALETTE.get(ep["genreKey"], THEME_PALETTE["office"])
    camera = panel.get("camera", "wide")
    emotion = panel.get("emotion", "determined")
    speaker = panel.get("speaker", "주인공")
    is_villain = any(k in speaker for k in ("팀장", "동기", "차주", "판매자", "구매자", "집주인", "중개사", "진상", "윗집", "총대", "관장"))

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(ep["title"])} {idx}컷">',
        _draw_backdrop(scene, w, h, pal),
    ]

    # Cinematic camera framing
    if camera == "split_versus":
        parts.append('<rect x="0" y="60" width="356" height="600" fill="#7f1d1d" opacity="0.28"/>')
        parts.append('<rect x="364" y="60" width="356" height="600" fill="#064e3b" opacity="0.28"/>')
        parts.append('<line x1="360" y1="60" x2="360" y2="660" stroke="#fde047" stroke-width="6" stroke-dasharray="18,10"/>')
        parts.append(_draw_character(180, 410, 1.35, pal["villain"], "#1f2937", "angry" if is_villain else "smug", is_villain=True))
        parts.append(_draw_character(540, 410, 1.35, pal["suit"], "#0f172a", "determined", is_villain=False))
    elif camera == "closeup_villain":
        parts.append(_draw_comic_lines(360, 430, "#ef4444", 28))
        parts.append(_draw_character(360, 455, 2.05, pal["villain"], "#1e293b", emotion, is_villain=True))
    elif camera == "closeup_hero":
        parts.append(_draw_comic_lines(360, 430, "#00dc64", 22))
        parts.append(_draw_character(360, 455, 2.05, pal["suit"], "#0f172a", emotion, is_villain=False))
    elif camera == "evidence_zoom":
        # Framed smartphone / official document close-up + character corner reaction
        parts.append(_draw_character(135, 500, 1.0, pal["suit"], "#0f172a", "calm_smirk", is_villain=False))
        parts.append('<g transform="translate(235, 250) rotate(-2)">')
        parts.append('<rect x="0" y="0" width="430" height="310" rx="22" fill="#f8fafc" stroke="#0b0f19" stroke-width="6"/>')
        parts.append('<rect x="0" y="0" width="430" height="54" rx="22" fill="#0b0f19"/>')
        parts.append(f'<text x="24" y="34" font-family="Pretendard, Apple SD Gothic Neo, sans-serif" font-size="18" font-weight="900" fill="#00dc64">📋 결정적 증거 확보 · {esc(speaker)}</text>')
        for row_y in (92, 134, 176, 218):
            parts.append(f'<line x1="28" y1="{row_y}" x2="402" y2="{row_y}" stroke="#cbd5e1" stroke-width="4" stroke-linecap="round"/>')
        parts.append('<rect x="275" y="185" width="128" height="46" rx="10" fill="none" stroke="#ef4444" stroke-width="4.5" transform="rotate(-8 339 208)"/>')
        parts.append('<text x="339" y="215" text-anchor="middle" font-family="Pretendard, Apple SD Gothic Neo, sans-serif" font-size="19" font-weight="900" fill="#ef4444" transform="rotate(-8 339 208)">원본 입증</text>')
        parts.append('</g>')
    elif camera == "climax_impact":
        parts.append(_draw_comic_lines(360, 400, "#fde047", 36))
        parts.append(f'<circle cx="360" cy="400" r="190" fill="{pal["accent"]}" opacity="0.24"/>')
        parts.append(_draw_character(360, 465, 1.9, pal["villain"] if is_villain else pal["suit"], "#0f172a", emotion, is_villain=is_villain))
    else:  # wide
        parts.append(_draw_character(215, 445, 1.38, pal["suit"], "#0f172a", "determined" if not is_villain else "shocked", is_villain=False))
        parts.append(_draw_character(510, 445, 1.38, pal["villain"], "#334155", emotion if is_villain else "smug", is_villain=True))

    # Top cut header strip (clean, comic style)
    parts.append('<rect x="0" y="0" width="720" height="54" fill="#05070b" opacity="0.88"/>')
    parts.append(
        f'<text x="24" y="34" font-family="Pretendard, Apple SD Gothic Neo, sans-serif" font-size="17" font-weight="800" fill="#00dc64">'
        f'EP.{ep["episodeNo"]} · {esc(panel["act"])}</text>'
    )
    parts.append(
        f'<text x="696" y="34" text-anchor="end" font-family="Pretendard, Apple SD Gothic Neo, sans-serif" font-size="16" font-weight="800" fill="#e2e8f0">'
        f'CUT {idx:02d} / {total}</text>'
    )

    # Main speech bubble near top (clean unobstructed over forehead/above frame)
    parts.append(_draw_bubble(34, 86, 610, speaker, panel["line"], width_chars=21, style="speech", tail_dir="down"))

    # Dramatic SFX splash positioned cleanly below bubble right shoulder so it never clips
    sfx = panel.get("sfx", "")
    if sfx:
        parts.append(
            f'<g transform="translate(592, 286) rotate(6)">'
            f'<rect x="-86" y="-30" width="172" height="52" rx="14" fill="#ef4444" stroke="#ffffff" stroke-width="4"/>'
            f'<text x="0" y="5" text-anchor="middle" font-family="Pretendard, Apple SD Gothic Neo, sans-serif" font-size="25" font-weight="900" fill="#fde047">{esc(sfx)}</text>'
            f'</g>'
        )

    # Bottom narrative box (strong black border & warm comic tint)
    sub_lines = wrap_ko(panel["subline"], width=27, max_lines=2)
    box_h = 34 + len(sub_lines) * 32
    by = h - box_h - 28
    parts.append(f'<rect x="34" y="{by}" width="652" height="{box_h}" rx="14" fill="#0b0f19" opacity="0.93" stroke="#00dc64" stroke-width="3.5"/>')
    for s_idx, s_line in enumerate(sub_lines):
        parts.append(
            f'<text x="360" y="{by + 36 + s_idx * 32}" text-anchor="middle" '
            f'font-family="Pretendard, Apple SD Gothic Neo, sans-serif" font-size="20" font-weight="700" fill="#f8fafc">{esc(s_line)}</text>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


STYLE_CSS = """
:root {
  --nv-green: #00dc64;
  --nv-green-dark: #00b853;
  --nv-red: #ff3b30;
  --bg-page: #f8f9fa;
  --bg-card: #ffffff;
  --ink-strong: #111827;
  --ink-muted: #5b6472;
  --line: #e5e8eb;
  --viewer-bg: #0b0d10;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; overflow-x: hidden; background: var(--bg-page); color: var(--ink-strong); font-family: "Pretendard", "Apple SD Gothic Neo", "Noto Sans KR", sans-serif; line-height: 1.55; }
a { color: inherit; text-decoration: none; }
img { display: block; max-width: 100%; height: auto; }
.wrap { width: 100%; max-width: 1180px; margin: 0 auto; padding: 0 16px; }

/* Naver Webtoon Top GNB */
.nv-gnb { position: sticky; top: 0; z-index: 60; background: #ffffff; border-bottom: 1px solid var(--line); }
.nv-gnb-inner { display: flex; align-items: center; justify-content: space-between; gap: 14px; min-height: 60px; flex-wrap: wrap; padding: 8px 0; }
.nv-brand { display: inline-flex; align-items: center; gap: 10px; font-weight: 900; font-size: 19px; letter-spacing: -0.03em; }
.nv-badge { display: inline-flex; align-items: center; justify-content: center; background: var(--nv-green); color: #ffffff; font-weight: 900; font-size: 13px; padding: 5px 10px; border-radius: 6px; letter-spacing: 0.02em; }
.nv-sub-pill { font-size: 11px; font-weight: 800; color: #059669; background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 999px; padding: 2px 8px; }
.nv-nav { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; }
.nv-nav a { font-size: 15px; font-weight: 700; color: #374151; padding: 8px 2px; border-bottom: 3px solid transparent; }
.nv-nav a.active, .nv-nav a:hover { color: #00b853; border-bottom-color: var(--nv-green); }

/* Genre Filter Tabs */
.nv-subbar { background: #ffffff; border-bottom: 1px solid var(--line); overflow-x: auto; }
.nv-tabs { display: flex; align-items: center; gap: 8px; padding: 10px 0; min-width: max-content; }
.nv-tab-btn { border: 1px solid #e5e8eb; background: #f8f9fa; color: #374151; font-weight: 700; font-size: 13.5px; border-radius: 999px; padding: 7px 14px; cursor: pointer; font-family: inherit; }
.nv-tab-btn.is-active { background: #111827; border-color: #111827; color: #ffffff; }

/* Today Spotlight Banner */
.hero-spot { margin-top: 18px; background: linear-gradient(125deg, #0b1120 0%, #172554 55%, #064e3b 100%); border-radius: 16px; padding: 22px; color: #ffffff; display: grid; grid-template-columns: 180px 1fr; gap: 22px; align-items: center; box-shadow: 0 12px 30px rgba(15, 23, 42, 0.14); }
.hero-cover { width: 180px; border-radius: 10px; overflow: hidden; box-shadow: 0 10px 24px rgba(0, 0, 0, 0.45); border: 2px solid rgba(255, 255, 255, 0.16); }
.hero-kicker { display: inline-flex; align-items: center; gap: 8px; background: var(--nv-red); color: #ffffff; font-size: 12px; font-weight: 900; border-radius: 6px; padding: 4px 10px; margin-bottom: 10px; }
.hero-title { margin: 0 0 10px; font-size: clamp(20px, 2.6vw, 27px); font-weight: 900; line-height: 1.32; letter-spacing: -0.02em; }
.hero-hook { margin: 0 0 16px; font-size: 15px; color: #e2e8f0; line-height: 1.55; }
.hero-actions { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.btn-nv { display: inline-flex; align-items: center; justify-content: center; gap: 6px; background: var(--nv-green); color: #052e16; font-weight: 900; font-size: 15px; padding: 12px 22px; border-radius: 8px; border: 0; cursor: pointer; }
.btn-nv:hover { background: #14eb74; }
.hero-meta { font-size: 13.5px; color: #fde047; font-weight: 800; }

/* 3:4 Naver Webtoon Poster Grid */
.sec-head { display: flex; align-items: flex-end; justify-content: space-between; gap: 12px; margin: 28px 0 14px; flex-wrap: wrap; }
.sec-title { margin: 0; font-size: 20px; font-weight: 900; letter-spacing: -0.02em; }
.sec-sub { font-size: 13px; color: var(--ink-muted); font-weight: 600; }
.poster-grid { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 16px 14px; }
.poster-card { display: flex; flex-direction: column; gap: 8px; background: transparent; transition: transform 0.16s ease; }
.poster-card:hover { transform: translateY(-3px); }
.poster-thumb { position: relative; aspect-ratio: 3 / 4; border-radius: 10px; overflow: hidden; border: 1px solid #d1d5db; background: #111827; box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08); }
.poster-thumb img { width: 100%; height: 100%; object-fit: cover; }
.poster-rank { position: absolute; top: 8px; left: 8px; background: rgba(11, 15, 25, 0.88); color: var(--nv-green); font-size: 12px; font-weight: 900; padding: 3px 8px; border-radius: 6px; }
.poster-up { position: absolute; top: 8px; right: 8px; background: var(--nv-red); color: #ffffff; font-size: 11px; font-weight: 900; padding: 3px 7px; border-radius: 6px; }
.poster-ep-title { margin: 0; font-size: 14.5px; font-weight: 800; line-height: 1.38; color: var(--ink-strong); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.poster-hook { margin: 0; font-size: 12.5px; color: var(--ink-muted); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.poster-stats { font-size: 12px; font-weight: 800; color: #d97706; display: flex; align-items: center; gap: 8px; }
.poster-stats span.views { color: #6b7280; font-weight: 600; }

/* Naver Webtoon Episode List Table */
.ep-table-box { background: #ffffff; border: 1px solid var(--line); border-radius: 12px; overflow: hidden; margin-bottom: 32px; }
.ep-row { display: grid; grid-template-columns: 84px 1fr 110px 94px; gap: 14px; align-items: center; padding: 14px 16px; border-bottom: 1px solid #f1f5f9; transition: background 0.14s ease; }
.ep-row:last-child { border-bottom: 0; }
.ep-row:hover { background: #f8fafc; }
.ep-row-thumb { width: 84px; height: 58px; border-radius: 6px; overflow: hidden; border: 1px solid #e5e8eb; background: #0f172a; }
.ep-row-thumb img { width: 100%; height: 100%; object-fit: cover; object-position: top; }
.ep-row-badge { display: inline-block; font-size: 11px; font-weight: 900; color: #059669; background: #ecfdf5; border-radius: 4px; padding: 2px 6px; margin-bottom: 4px; }
.ep-row-title { font-size: 15px; font-weight: 800; color: #111827; line-height: 1.38; margin: 0 0 3px; }
.ep-row-desc { font-size: 13px; color: #64748b; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ep-row-rate { font-size: 13.5px; font-weight: 900; color: #e11d48; text-align: right; }
.ep-row-len { font-size: 12px; color: #64748b; font-weight: 700; display: block; }
.ep-row-cta { text-align: center; font-size: 13px; font-weight: 800; background: var(--nv-green); color: #052e16; padding: 8px 10px; border-radius: 6px; }

/* Immersive Vertical Webtoon Viewer */
body.viewer-body { background: var(--viewer-bg); color: #f8fafc; }
body.viewer-body.light-mode { background: #f3f4f6; color: #111827; }
.read-progress { position: fixed; top: 0; left: 0; width: 100%; height: 3px; z-index: 90; background: rgba(255, 255, 255, 0.12); }
.read-progress-fill { height: 100%; width: 0%; background: var(--nv-green); transition: width 0.08s linear; }
.viewer-bar { position: sticky; top: 0; z-index: 70; background: rgba(20, 23, 28, 0.96); backdrop-filter: blur(8px); border-bottom: 1px solid #27272a; color: #ffffff; }
body.viewer-body.light-mode .viewer-bar { background: rgba(255, 255, 255, 0.96); color: #111827; border-bottom-color: #e5e8eb; }
.viewer-bar-inner { display: flex; align-items: center; justify-content: space-between; gap: 10px; min-height: 54px; padding: 6px 0; }
.viewer-title-group { display: flex; align-items: center; gap: 10px; min-width: 0; flex: 1; }
.viewer-back { display: inline-flex; align-items: center; gap: 4px; font-size: 13.5px; font-weight: 800; background: #27272a; color: #ffffff; padding: 7px 12px; border-radius: 8px; flex-shrink: 0; }
body.viewer-body.light-mode .viewer-back { background: #f1f5f9; color: #111827; }
.viewer-h1 { margin: 0; font-size: 14.5px; font-weight: 800; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.viewer-controls { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.ctrl-btn { border: 1px solid #3f3f46; background: #18181b; color: #f8fafc; font-size: 12.5px; font-weight: 800; padding: 7px 10px; border-radius: 8px; cursor: pointer; font-family: inherit; }
body.viewer-body.light-mode .ctrl-btn { background: #ffffff; color: #111827; border-color: #d1d5db; }
.ctrl-btn.primary { background: var(--nv-green); color: #052e16; border-color: var(--nv-green); }

/* Vertical Full-Bleed Webtoon Canvas (18 Cuts Stacked Seamlessly) */
.ep-intro-strip { max-width: 720px; margin: 16px auto 12px; padding: 16px 18px; background: #161b22; border: 1px solid #30363d; border-radius: 12px; }
body.viewer-body.light-mode .ep-intro-strip { background: #ffffff; border-color: #e5e8eb; }
.ep-intro-strip h2 { margin: 0 0 8px; font-size: clamp(19px, 3vw, 24px); font-weight: 900; line-height: 1.35; }
.ep-intro-strip p { margin: 0; font-size: 14.5px; color: #cbd5e1; }
body.viewer-body.light-mode .ep-intro-strip p { color: #475569; }
.comic-canvas { width: 100%; max-width: 720px; margin: 0 auto; background: #000000; box-shadow: 0 0 40px rgba(0, 0, 0, 0.55); }
.comic-cut { width: 100%; margin: 0; padding: 0; background: #000000; }
.comic-cut img { width: 100%; height: auto; display: block; }
.act-gutter { padding: 18px 16px 10px; text-align: center; background: #05070b; color: var(--nv-green); font-size: 12.5px; font-weight: 900; letter-spacing: 0.08em; border-top: 1px solid #1e293b; }
.cut-float-counter { position: fixed; right: 16px; bottom: 72px; z-index: 65; background: rgba(11, 15, 25, 0.88); color: #00dc64; font-size: 12px; font-weight: 900; padding: 6px 12px; border-radius: 999px; border: 1px solid rgba(0, 220, 100, 0.4); }

/* Reader Footer: Rating + Next Preview + Comments + Guide */
.reader-post { max-width: 720px; margin: 20px auto 90px; display: flex; flex-direction: column; gap: 16px; padding: 0 12px; }
.nv-box { background: #ffffff; color: #111827; border: 1px solid #e5e8eb; border-radius: 14px; padding: 20px; }
.rate-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.star-btns { display: flex; gap: 6px; }
.star-btn { font-size: 20px; background: #fef9c3; border: 1px solid #fde047; border-radius: 8px; padding: 6px 10px; cursor: pointer; }
.next-preview { display: grid; grid-template-columns: 76px 1fr auto; gap: 14px; align-items: center; background: #ecfdf5; border: 1px solid #a7f3d0; border-radius: 12px; padding: 14px; }
.next-preview img { width: 76px; height: 100px; object-fit: cover; border-radius: 8px; }
.comment-item { padding: 14px 0; border-bottom: 1px solid #f1f5f9; }
.comment-item:last-child { border-bottom: 0; }
.best-pill { display: inline-block; background: #ef4444; color: #ffffff; font-size: 10.5px; font-weight: 900; padding: 2px 6px; border-radius: 4px; margin-right: 6px; }
.comment-form { display: flex; gap: 8px; margin-top: 12px; }
.comment-form input { flex: 1; padding: 10px 12px; border: 1px solid #d1d5db; border-radius: 8px; font-size: 14px; font-family: inherit; }
.comment-form button { background: var(--nv-green); color: #052e16; font-weight: 900; border: 0; padding: 0 16px; border-radius: 8px; cursor: pointer; font-family: inherit; }
.ad-box { background: #ffffff; color: #111827; border: 1px solid #e5e8eb; border-radius: 14px; padding: 18px; }
.ad-disclosure { font-size: 11.5px; color: #6b7280; margin-bottom: 6px; }
.coupang-banner { display: grid; gap: 8px; }
.coupang-cta { display: inline-flex; align-items: center; justify-content: center; background: #0f172a; color: #ffffff; font-weight: 800; font-size: 14px; padding: 11px 16px; border-radius: 8px; }
.bottom-dock { position: fixed; left: 0; right: 0; bottom: 0; z-index: 80; background: rgba(17, 24, 39, 0.96); border-top: 1px solid #374151; padding: 8px 14px; display: flex; justify-content: center; gap: 10px; }
.bottom-dock a, .bottom-dock button { font-size: 13px; font-weight: 800; color: #ffffff; background: #1f2937; border: 1px solid #374151; padding: 8px 14px; border-radius: 8px; cursor: pointer; font-family: inherit; }
.bottom-dock a.go-next { background: var(--nv-green); color: #052e16; border-color: var(--nv-green); }

.site-footer { margin-top: 40px; background: #ffffff; border-top: 1px solid var(--line); padding: 28px 0 40px; font-size: 13px; color: #6b7280; }
.footer-links { display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 8px; }
.prose-card { background: #ffffff; border: 1px solid var(--line); border-radius: 14px; padding: 24px; margin: 22px 0; }

@media (max-width: 960px) {
  .poster-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}
@media (max-width: 640px) {
  .hero-spot { grid-template-columns: 1fr; padding: 16px; }
  .hero-cover { width: 140px; }
  .poster-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px 10px; }
  .ep-row { grid-template-columns: 64px 1fr auto; }
  .ep-row-cta { display: none; }
  .ep-row-thumb { width: 64px; height: 50px; }
  .reader-post { padding: 0 8px; }
  .next-preview { grid-template-columns: 60px 1fr; }
  .next-preview a { grid-column: 1 / -1; text-align: center; }
}
@media (max-width: 350px) {
  .wrap { padding: 0 10px; }
  .nv-nav { gap: 10px; }
  .nv-nav a { font-size: 13.5px; }
}
""".strip()


AD_MANAGER_JS = """
// Dual-Mode Ad Manager for GuideHollow 웹툰 (toon.guidehollow.com)
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
    el.innerHTML =
      '<div class="ad-disclosure">' + esc(COUPANG_FTC) + '</div>' +
      '<div class="coupang-banner">' +
      '  <div style="font-size:12px;font-weight:800;color:#059669;">' + esc(badge) + '</div>' +
      '  <div style="font-size:17px;font-weight:900;color:#111827;">' + esc(title) + '</div>' +
      '  <div style="font-size:13.5px;color:#4b5563;">' + esc(reason) + '</div>' +
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
      document.querySelectorAll("[data-gh-ad-slot]").forEach(renderCoupangSlot);
    }
  });
})();
""".strip()


VIEWER_JS = """
(function () {
  // Genre Filter on Home / Studio
  const tabs = document.querySelectorAll(".nv-tab-btn");
  const cards = document.querySelectorAll("[data-genre-item]");
  tabs.forEach(function (btn) {
    btn.addEventListener("click", function () {
      const target = btn.getAttribute("data-genre") || "all";
      tabs.forEach(function (t) { t.classList.remove("is-active"); });
      btn.classList.add("is-active");
      cards.forEach(function (card) {
        const g = card.getAttribute("data-genre-item") || "";
        card.style.display = (target === "all" || target === g) ? "" : "none";
      });
    });
  });

  // Reading Progress + Cut Counter on Episode Page
  const fill = document.getElementById("read-progress-fill");
  const cutLabel = document.getElementById("cut-float-counter");
  const cuts = Array.from(document.querySelectorAll(".comic-cut"));
  if (fill || cutLabel) {
    window.addEventListener("scroll", function () {
      const docH = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      const pct = Math.min(100, Math.max(0, Math.round((window.scrollY / docH) * 100)));
      if (fill) fill.style.width = pct + "%";
      if (cutLabel && cuts.length) {
        const mid = window.scrollY + window.innerHeight * 0.4;
        let current = 1;
        cuts.forEach(function (c, i) {
          if (c.offsetTop <= mid) current = i + 1;
        });
        cutLabel.textContent = current + " / " + cuts.length + "컷";
      }
    }, { passive: true });
  }

  // Light / Dark Mode Toggle
  const modeBtn = document.getElementById("toggle-theme-btn");
  if (modeBtn) {
    modeBtn.addEventListener("click", function () {
      document.body.classList.toggle("light-mode");
      modeBtn.textContent = document.body.classList.contains("light-mode") ? "🌙 다크" : "☀️ 라이트";
    });
  }

  // Star Rating Feedback
  const rateMsg = document.getElementById("star-msg");
  document.querySelectorAll(".star-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const val = btn.getAttribute("data-star") || "5";
      if (rateMsg) rateMsg.textContent = "별점 " + val + "점 참여가 반영되었습니다! 감사합니다.";
    });
  });

  // Interactive Reader Comment Append
  const cForm = document.getElementById("reader-comment-form");
  const cInput = document.getElementById("reader-comment-input");
  const cList = document.getElementById("comment-list");
  if (cForm && cInput && cList) {
    cForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const txt = cInput.value.trim();
      if (!txt) return;
      const item = document.createElement("div");
      item.className = "comment-item";
      item.innerHTML = '<div style="font-size:13px;font-weight:800;margin-bottom:4px;"><span class="best-pill" style="background:#00dc64;color:#052e16;">NEW</span>방금 남긴 댓글</div><div style="font-size:14px;"></div>';
      item.querySelector("div:last-child").textContent = txt;
      cList.prepend(item);
      cInput.value = "";
    });
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
  <header class="nv-gnb">
    <div class="wrap nv-gnb-inner">
      <a class="nv-brand" href="/">
        <span class="nv-badge">WEBTOON</span>
        <span>GuideHollow 썰툰</span>
        <span class="nv-sub-pill">18컷 장편 연재</span>
      </a>
      <nav class="nv-nav" aria-label="주요 메뉴">
        <a href="/" class="{'active' if active == 'home' else ''}">요일·인기 웹툰</a>
        <a href="/studio/" class="{'active' if active == 'studio' else ''}">완결·전체 정주행</a>
        <a href="/about/" class="{'active' if active == 'about' else ''}">연재 원칙</a>
        <a href="https://shopping.guidehollow.com/" target="_blank" rel="noopener noreferrer">🛒 쇼핑 가이드 ↗</a>
      </nav>
    </div>
  </header>"""


def _footer_html() -> str:
    return """
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
      <div>GuideHollow 웹툰 연재관 · 전 에피소드 18컷 풀스토리 세로 스크롤 제공 · 각 에피소드는 현실 분쟁 예방 가이드와 함께 제공됩니다.</div>
    </div>
  </footer>
  <script src="/assets/ad-manager.js"></script>
  <script src="/assets/viewer.js"></script>"""


def _render_genre_tabs() -> str:
    return """
  <div class="nv-subbar">
    <div class="wrap nv-tabs" role="tablist" aria-label="웹툰 장르 필터">
      <button type="button" class="nv-tab-btn is-active" data-genre="all">🔥 전체 웹툰 (10작)</button>
      <button type="button" class="nv-tab-btn" data-genre="office">💼 직장·알바 참교육</button>
      <button type="button" class="nv-tab-btn" data-genre="love">💍 연애·인간관계</button>
      <button type="button" class="nv-tab-btn" data-genre="car">🚗 주차·도로 참교육</button>
      <button type="button" class="nv-tab-btn" data-genre="mystery">👻 새벽 소름·미스터리</button>
      <button type="button" class="nv-tab-btn" data-genre="finance">🏦 전세·생활경제</button>
      <button type="button" class="nv-tab-btn" data-genre="living">📦 중고·공구 역관광</button>
      <button type="button" class="nv-tab-btn" data-genre="apartment">🏢 층간소음 해결</button>
    </div>
  </div>"""


def _render_poster_cards() -> str:
    cards = []
    for idx, ep in enumerate(EPISODES, start=1):
        eid = ep["id"]
        cards.append(
            f'<a class="poster-card" href="/episodes/{esc(eid)}/" data-genre-item="{esc(ep["genreKey"])}">'
            f'  <div class="poster-thumb">'
            f'    <img src="/assets/toons/{esc(eid)}/cover.svg" alt="{esc(ep["title"])}" loading="lazy" width="480" height="640" />'
            f'    <span class="poster-rank">{idx}</span>'
            f'    <span class="poster-up">{esc(ep["badgeText"])}</span>'
            f'  </div>'
            f'  <h3 class="poster-ep-title">{esc(ep["title"])}</h3>'
            f'  <p class="poster-hook">{esc(ep["hook"])}</p>'
            f'  <div class="poster-stats">★ {esc(ep["rating"])} <span class="views">조회 {esc(ep["viewsLabel"])} · 18컷</span></div>'
            f'</a>'
        )
    return "\n".join(cards)


def _render_episode_table() -> str:
    rows = []
    for ep in EPISODES:
        eid = ep["id"]
        rows.append(
            f'<a class="ep-row" href="/episodes/{esc(eid)}/" data-genre-item="{esc(ep["genreKey"])}">'
            f'  <div class="ep-row-thumb"><img src="/assets/toons/{esc(eid)}/cover.svg" alt="{esc(ep["title"])}" loading="lazy" /></div>'
            f'  <div style="min-width:0;">'
            f'    <span class="ep-row-badge">{esc(ep["episodeNo"])}화 · {esc(ep["genre"])}</span>'
            f'    <h3 class="ep-row-title">{esc(ep["title"])}</h3>'
            f'    <p class="ep-row-desc">{esc(ep["summary"])}</p>'
            f'  </div>'
            f'  <div class="ep-row-rate">★ {esc(ep["rating"])}<span class="ep-row-len">18컷 장편 · 세로정주행</span></div>'
            f'  <div class="ep-row-cta">감상하기 ▶</div>'
            f'</a>'
        )
    return "\n".join(rows)


def build_home_html() -> str:
    top = EPISODES[0]
    head = _head_html(
        "GuideHollow 웹툰 — 실시간 사이다 썰툰 연재관 (전 회차 18컷 장편)",
        "직장 갑질, 결혼식 축의금, 악성 이중주차, 전세 사기, 새벽 무료나눔 실화를 네이버 웹툰 스타일 18컷 장편 세로 스크롤로 무료 감상하세요.",
        f"{SITE_URL}/",
        f"{SITE_URL}/assets/toons/{top['id']}/cover.svg",
    )
    return f"""{head}
<body>
{_gnb_html("home")}
{_render_genre_tabs()}
  <main class="wrap">
    <section class="hero-spot" aria-label="오늘의 인기 급상승 웹툰">
      <div class="hero-cover">
        <img src="/assets/toons/{esc(top['id'])}/cover.svg" alt="{esc(top['title'])}" width="480" height="640" />
      </div>
      <div>
        <span class="hero-kicker">🔥 실시간 1위 · 오늘 가장 많이 정주행한 웹툰</span>
        <h1 class="hero-title">{esc(top['title'])}</h1>
        <p class="hero-hook">{esc(top['hook'])} — {esc(top['summary'])}</p>
        <div class="hero-actions">
          <a class="btn-nv" href="/episodes/{esc(top['id'])}/">18컷 풀스토리 지금 바로 보기 ▶</a>
          <span class="hero-meta">★ {esc(top['rating'])} · 조회 {esc(top['viewsLabel'])} · 18컷 세로 장편</span>
        </div>
      </div>
    </section>

    <div class="sec-head">
      <h2 class="sec-title">오늘의 인기 연재 웹툰</h2>
      <span class="sec-sub">포스터를 누르면 18컷 장편 세로 웹툰 뷰어로 바로 이동합니다</span>
    </div>
    <section class="poster-grid" aria-label="인기 웹툰 포스터 목록">
{_render_poster_cards()}
    </section>

    <div class="sec-head">
      <h2 class="sec-title">전체 회차 · 한눈에 정주행 리스트</h2>
      <span class="sec-sub">전 회차 1화~10화 · 각 18컷 세로 풀사이즈 무료 공개</span>
    </div>
    <section class="ep-table-box" aria-label="전체 회차 리스트">
{_render_episode_table()}
    </section>
  </main>
{_footer_html()}
</body>
</html>"""


def build_studio_archive_html() -> str:
    head = _head_html(
        "완결·전체 정주행 모아보기 | GuideHollow 웹툰",
        "GuideHollow 오리지널 사이다 썰툰 전 10화 180컷 장편 웹툰 일러스트를 장르별로 골라 바로 정주행하세요.",
        f"{SITE_URL}/studio/",
    )
    return f"""{head}
<body>
{_gnb_html("studio")}
{_render_genre_tabs()}
  <main class="wrap">
    <div class="sec-head">
      <h1 class="sec-title">🔥 전체 10작 180컷 정주행 아카이브</h1>
      <span class="sec-sub">직장·연애·주차·전세·중고거래 레전드 실화 완결 모음</span>
    </div>
    <section class="poster-grid" style="margin-bottom:28px;">
{_render_poster_cards()}
    </section>
    <section class="ep-table-box">
{_render_episode_table()}
    </section>
  </main>
{_footer_html()}
</body>
</html>"""


def build_episode_html(idx: int, ep: dict) -> str:
    eid = ep["id"]
    prev_ep = EPISODES[idx - 1] if idx > 0 else EPISODES[-1]
    next_ep = EPISODES[idx + 1] if idx + 1 < len(EPISODES) else EPISODES[0]
    cuts_html = []
    last_act = ""
    total = len(ep["panels"])
    for c_idx, p in enumerate(ep["panels"], start=1):
        act = p["act"]
        if act != last_act:
            cuts_html.append(f'<div class="act-gutter">▼ {esc(act)} ({c_idx}컷~) ▼</div>')
            last_act = act
        cuts_html.append(
            f'<div class="comic-cut" data-cut-num="{c_idx}">'
            f'  <img src="/assets/toons/{esc(eid)}/cut-{c_idx:02d}.svg" alt="{esc(ep["title"])} {c_idx}컷 - {esc(p["line"])}" width="720" height="880" loading="{"eager" if c_idx <= 3 else "lazy"}" />'
            f'</div>'
        )

    comments_html = "\n".join(
        f'<div class="comment-item">'
        f'  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">'
        f'    <span style="font-size:13.5px;font-weight:800;"><span class="best-pill">BEST</span>{esc(c["user"])}</span>'
        f'    <span style="font-size:12.5px;font-weight:700;color:#64748b;">👍 {esc(c["likes"])}</span>'
        f'  </div>'
        f'  <div style="font-size:14.5px;color:#1e293b;">{esc(c["text"])}</div>'
        f'</div>'
        for c in ep["bestComments"]
    )
    checklist_html = "\n".join(f"<li style='margin-bottom:6px;'>{esc(item)}</li>" for item in ep["checklist"])
    coup = ep["coupang"]
    head = _head_html(
        f"{ep['episodeNo']}화. {ep['title']} | GuideHollow 웹툰",
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
        <h1 class="viewer-h1">{ep['episodeNo']}화. {esc(ep['title'])}</h1>
      </div>
      <div class="viewer-controls">
        <button id="toggle-theme-btn" type="button" class="ctrl-btn">☀️ 라이트</button>
        <a class="ctrl-btn" href="/episodes/{esc(prev_ep['id'])}/">◀ 이전</a>
        <a class="ctrl-btn primary" href="/episodes/{esc(next_ep['id'])}/">다음화 ▶</a>
      </div>
    </div>
  </header>

  <main>
    <div class="ep-intro-strip">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;flex-wrap:wrap;">
        <span class="nv-badge" style="font-size:11.5px;padding:3px 8px;">{ep['episodeNo']}화 · 18컷 장편</span>
        <span style="font-size:12.5px;font-weight:800;color:#fde047;">★ {esc(ep['rating'])} · 조회 {esc(ep['viewsLabel'])}</span>
      </div>
      <h2>{esc(ep['title'])}</h2>
      <p>{esc(ep['hook'])}</p>
    </div>

    <div id="cut-float-counter" class="cut-float-counter">1 / {total}컷</div>

    <article class="comic-canvas" aria-label="웹툰 본문 세로 스크롤 컷 모음">
{chr(10).join(cuts_html)}
    </article>

    <section class="reader-post" aria-label="감상 후 참여 및 다음화 안내">
      <div class="nv-box">
        <div class="rate-row">
          <div>
            <div style="font-size:16px;font-weight:900;">이번 화 재미있게 보셨나요? (★ {esc(ep['rating'])})</div>
            <div id="star-msg" style="font-size:13px;color:#059669;font-weight:700;margin-top:2px;">별점을 눌러 작가에게 사이다 응원을 남겨주세요!</div>
          </div>
          <div class="star-btns">
            <button type="button" class="star-btn" data-star="5">⭐ 5점 최고</button>
            <button type="button" class="star-btn" data-star="4">★ 4점</button>
          </div>
        </div>
      </div>

      <div class="next-preview">
        <img src="/assets/toons/{esc(next_ep['id'])}/cover.svg" alt="{esc(next_ep['title'])}" />
        <div>
          <div style="font-size:12px;font-weight:900;color:#059669;">다음 정주행 추천 · {next_ep['episodeNo']}화</div>
          <div style="font-size:15.5px;font-weight:900;color:#111827;margin:4px 0;">{esc(next_ep['title'])}</div>
          <div style="font-size:13px;color:#475569;">{esc(next_ep['hook'])}</div>
        </div>
        <a class="btn-nv" href="/episodes/{esc(next_ep['id'])}/">다음화 보기 ▶</a>
      </div>

      <div class="ad-box"
           data-gh-ad-slot="ep-mid"
           data-ad-kind="contextual"
           data-ad-layout="in-article"
           data-widget-id="{esc(coup['widgetId'])}"
           data-badge="{esc(coup['badge'])}"
           data-title="{esc(coup['title'])}"
           data-reason="{esc(coup['reason'])}"
           data-cta="{esc(coup['cta'])}"
           data-url="{esc(coup['url'])}"
           data-guide-url="{esc(coup['guideUrl'])}"
           data-guide-label="{esc(coup['guideLabel'])}"
           aria-label="상황 맞춤 생활·상품 추천 배너"></div>

      <div class="nv-box">
        <h3 style="margin:0 0 10px;font-size:17px;font-weight:900;">💬 독자 BEST 댓글 ({len(ep['bestComments'])})</h3>
        <div id="comment-list">
{comments_html}
        </div>
        <form id="reader-comment-form" class="comment-form">
          <input id="reader-comment-input" type="text" maxlength="140" placeholder="이번 화 가장 통쾌했던 장면을 댓글로 남겨보세요..." aria-label="댓글 입력" />
          <button type="submit">등록</button>
        </form>
      </div>

      <div class="nv-box">
        <h3 style="margin:0 0 8px;font-size:17px;font-weight:900;">🛡️ {esc(ep['guideTitle'])}</h3>
        <p style="margin:0 0 12px;font-size:14px;color:#334155;">{esc(ep['guideBody'])}</p>
        <div style="font-size:14px;font-weight:900;margin-bottom:6px;color:#059669;">실전 확인 체크리스트</div>
        <ul style="margin:0;padding-left:18px;font-size:13.5px;color:#1e293b;">
{checklist_html}
        </ul>
      </div>
    </section>
  </main>

  <nav class="bottom-dock" aria-label="하단 빠른 이동">
    <a href="/">🏠 웹툰 홈</a>
    <a href="/episodes/{esc(prev_ep['id'])}/">◀ 이전화</a>
    <button type="button" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">⬆ 맨 위로</button>
    <a class="go-next" href="/episodes/{esc(next_ep['id'])}/">다음화 ▶</a>
  </nav>
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
        json.dumps({"episodes": EPISODES}, ensure_ascii=False, indent=2) + "\n",
    )

    svg_count = 0
    sitemap_urls = [f"{SITE_URL}/", f"{SITE_URL}/studio/", f"{SITE_URL}/about/"]
    for idx, ep in enumerate(EPISODES):
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
        write_text(DIST / "episodes" / eid / "index.html", build_episode_html(idx, ep))
        sitemap_urls.append(f"{SITE_URL}/episodes/{eid}/")

    write_text(DIST / "index.html", build_home_html())
    write_text(DIST / "studio" / "index.html", build_studio_archive_html())
    write_text(
        DIST / "about" / "index.html",
        build_policy_page(
            "about",
            "연재·편집 원칙",
            "GuideHollow 웹툰 연재·편집 원칙",
            "<p>전 에피소드는 직장·계약·중고거래·이웃 분쟁 등 일상에서 벌어지는 실제 고민을 5막 18컷 장편 세로 웹툰으로 각색하고, 하단에 법적 대응과 생활 체크리스트를 함께 수록합니다.</p>"
            "<p>독자가 모바일과 PC 모두에서 끊김 없는 정주행을 즐길 수 있도록 모든 회차를 세로 풀스토리 웹툰 포맷으로 제공합니다.</p>",
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
    return {"episodes": len(EPISODES), "svgs": svg_count, "urls": len(sitemap_urls)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ad-mode", choices=["coupang", "adsense"], default="coupang")
    args = parser.parse_args()
    stats = build_site(ad_mode=args.ad_mode)
    print(f"BUILT_WEBTOON_PORTAL episodes={stats['episodes']} svgs={stats['svgs']} urls={stats['urls']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
