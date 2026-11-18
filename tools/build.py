#!/usr/bin/env python3
"""Static site builder, Webtoon SVG illustrator & ZIP packager for GuideHollow 웹툰 (toon.guidehollow.com)."""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import shutil
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from content.episodes import EPISODES

DIST = ROOT / "dist"
ARTIFACTS = ROOT / "artifacts"
ZIP_PATH = ARTIFACTS / "guidehollow-toon-release.zip"
ORIGIN = "https://toon.guidehollow.com"
ADSENSE_PUB = "ca-pub-8830524482034754"
GA4_ID = "G-QP5Q67GE5B"
COUPANG_FTC = "이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."

SCENE_THEMES = {
    "오피스": {
        "sky1": "#1e293b", "sky2": "#475569", "wall": "#e2e8f0", "floor": "#94a3b8",
        "accent": "#00b853", "coat": "#1e3a8a", "shirt": "#f8fafc", "hair": "#0f172a", "skin": "#fde2cf",
        "tagBg": "#0f172a", "tagFg": "#00dc64",
    },
    "톡방·메신저": {
        "sky1": "#fef08a", "sky2": "#fde047", "wall": "#fef9c3", "floor": "#ca8a04",
        "accent": "#0284c7", "coat": "#0f766e", "shirt": "#ffffff", "hair": "#1e293b", "skin": "#fee4d3",
        "tagBg": "#1e293b", "tagFg": "#fde047",
    },
    "주차장·도로": {
        "sky1": "#0f172a", "sky2": "#1e293b", "wall": "#334155", "floor": "#1e293b",
        "accent": "#f59e0b", "coat": "#334155", "shirt": "#f1f5f9", "hair": "#090d16", "skin": "#fbd8c5",
        "tagBg": "#0f172a", "tagFg": "#fbbf24",
    },
    "예식장·카페": {
        "sky1": "#fdf2f8", "sky2": "#fbcfe8", "wall": "#fce7f3", "floor": "#f9a8d4",
        "accent": "#be185d", "coat": "#9d174d", "shirt": "#fff1f2", "hair": "#312e81", "skin": "#fdece2",
        "tagBg": "#831843", "tagFg": "#fbcfe8",
    },
    "미스터리야간": {
        "sky1": "#020617", "sky2": "#1e1b4b", "wall": "#0f172a", "floor": "#090d1f",
        "accent": "#a855f7", "coat": "#312e81", "shirt": "#c7d2fe", "hair": "#020617", "skin": "#e2e8f0",
        "tagBg": "#1e1b4b", "tagFg": "#c084fc",
    },
    "법원·계약서": {
        "sky1": "#ecfeff", "sky2": "#cffafe", "wall": "#f0fdfa", "floor": "#99f6e4",
        "accent": "#0f766e", "coat": "#0f172a", "shirt": "#ffffff", "hair": "#1f2937", "skin": "#fde5d7",
        "tagBg": "#0f766e", "tagFg": "#ccfbf1",
    },
}

STYLE_CSS = """
:root {
  --bg: #f6f7f9;
  --surface: #ffffff;
  --surface-alt: #f1f4f6;
  --ink: #111827;
  --muted: #64748b;
  --line: #e2e8f0;
  --naver: #00dc64;
  --naver-dark: #00b853;
  --naver-ink: #052e16;
  --highlight: #fef08a;
  --coupang-red: #e60023;
  --max: 1080px;
}
*, *::before, *::after { box-sizing: border-box; }
html { scroll-behavior: smooth; overflow-x: clip; max-width: 100%; }
body {
  margin: 0;
  overflow-x: clip;
  max-width: 100%;
  background: var(--bg);
  color: var(--ink);
  font-family: "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", system-ui, sans-serif;
  line-height: 1.62;
  overflow-wrap: anywhere;
}
a { color: inherit; }
button { font: inherit; }
:focus-visible { outline: 3px solid var(--naver-dark); outline-offset: 2px; }
.wrap { width: min(var(--max), calc(100% - 1.5rem)); margin: 0 auto; }

/* Naver Webtoon-inspired Header */
.site-header {
  background: #ffffff;
  border-bottom: 1px solid var(--line);
  position: sticky;
  top: 0;
  z-index: 50;
  box-shadow: 0 1px 6px rgba(15, 23, 42, 0.05);
}
.header-inner {
  min-height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
  padding: 0.45rem 0;
}
.brand {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-weight: 900;
  font-size: 1.12rem;
  text-decoration: none;
  letter-spacing: -0.02em;
}
.brand-n {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 7px;
  background: var(--naver);
  color: #052e16;
  font-weight: 900;
  font-size: 0.95rem;
}
.brand-sub {
  font-size: 0.76rem;
  font-weight: 800;
  color: var(--naver-dark);
  background: #ecfdf5;
  padding: 0.14rem 0.48rem;
  border-radius: 999px;
}
.nav { display: flex; gap: 0.35rem; flex-wrap: wrap; }
.nav a {
  text-decoration: none;
  padding: 0.42rem 0.78rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 800;
  color: #475569;
  transition: background 0.15s, color 0.15s;
}
.nav a:hover { background: #f1f5f9; color: var(--ink); }
.nav a.active {
  background: var(--naver);
  color: #052e16;
}

/* Top Spotlight Banner */
.hero {
  background: linear-gradient(135deg, #0b1220 0%, #112a22 100%);
  color: #ffffff;
  border-radius: 16px;
  padding: 1.65rem 1.4rem;
  margin: 1rem 0 1.2rem;
  border: 1px solid #1f3d30;
}
.hero-kicker {
  display: inline-block;
  background: var(--naver);
  color: #052e16;
  font-weight: 900;
  font-size: 0.76rem;
  padding: 0.18rem 0.62rem;
  border-radius: 6px;
}
.hero h1 {
  margin: 0.68rem 0 0.48rem;
  font-size: clamp(1.42rem, 3.6vw, 2.15rem);
  line-height: 1.25;
  letter-spacing: -0.02em;
}
.hero p { margin: 0; color: #cbd5e1; max-width: 48rem; font-size: 0.95rem; }
.hero-actions { display: flex; flex-wrap: wrap; gap: 0.6rem; margin-top: 1.05rem; }

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  padding: 0.62rem 1rem;
  border-radius: 9px;
  border: 1.5px solid var(--line);
  background: var(--surface);
  color: var(--ink);
  font-weight: 800;
  font-size: 0.88rem;
  cursor: pointer;
  text-decoration: none;
}
.btn-naver { background: var(--naver); color: #052e16; border-color: var(--naver-dark); }
.btn-dark { background: #111827; color: #ffffff; border-color: #111827; }
.btn-coupang { background: var(--coupang-red); color: #ffffff; border-color: #b91c1c; }

/* Naver Webtoon Genre Filter Strip */
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 1.2rem 0 0.65rem;
}
.section-head h2 { margin: 0; font-size: 1.22rem; letter-spacing: -0.02em; }
.genre-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin: 0.85rem 0 1.15rem;
  border-bottom: 2px solid var(--line);
  padding-bottom: 0.7rem;
}
.genre-pill {
  padding: 0.44rem 0.85rem;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: var(--surface);
  color: #475569;
  font-size: 0.84rem;
  font-weight: 800;
  cursor: pointer;
}
.genre-pill.is-active {
  background: var(--naver);
  color: #052e16;
  border-color: var(--naver-dark);
}

/* Illustrated Webtoon Thumbnail Cards */
.episode-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin-bottom: 1.6rem;
}
@media (max-width: 920px) { .episode-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 600px) { .episode-grid { grid-template-columns: 1fr; } }
.ep-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  text-decoration: none;
  transition: transform 0.16s ease, box-shadow 0.16s ease;
}
.ep-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 22px rgba(15, 23, 42, 0.08);
}
.toon-thumb-box {
  position: relative;
  width: 100%;
  aspect-ratio: 10 / 7;
  background: #0f172a;
  overflow: hidden;
  border-bottom: 1px solid var(--line);
}
.toon-thumb-img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.ep-num-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(17, 24, 39, 0.88);
  color: var(--naver);
  font-size: 0.74rem;
  font-weight: 900;
  padding: 0.18rem 0.52rem;
  border-radius: 6px;
}
.ep-up-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: var(--naver);
  color: #052e16;
  font-size: 0.72rem;
  font-weight: 900;
  padding: 0.14rem 0.44rem;
  border-radius: 5px;
}
.ep-card-body {
  padding: 0.88rem 0.95rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  flex: 1 1 auto;
}
.ep-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  font-weight: 800;
  color: var(--muted);
}
.ep-star { color: #ef4444; font-weight: 900; }
.ep-card h2, .ep-card h3 {
  margin: 0;
  font-size: 1rem;
  line-height: 1.38;
  color: var(--ink);
}
.ep-hook {
  background: #f0fdf4;
  border-left: 3px solid var(--naver-dark);
  padding: 0.36rem 0.55rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 700;
  color: #166534;
}
.ep-read-cta {
  margin-top: auto;
  padding-top: 0.45rem;
  font-size: 0.84rem;
  font-weight: 900;
  color: var(--naver-dark);
}

/* Naver Webtoon Vertical Comic Viewer */
.viewer-bar {
  background: #111827;
  color: #f8fafc;
  border-radius: 12px;
  padding: 0.72rem 0.95rem;
  margin: 0.9rem 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.6rem;
}
.viewer-title-wrap { min-width: 0; flex: 1 1 260px; }
.viewer-ep-tag { font-size: 0.76rem; font-weight: 800; color: var(--naver); }
.viewer-title-wrap h1 { margin: 0.12rem 0 0; font-size: clamp(1.02rem, 2.5vw, 1.35rem); line-height: 1.35; }
.viewer-controls { display: flex; flex-wrap: wrap; gap: 0.4rem; align-items: center; }
.vbtn {
  padding: 0.42rem 0.72rem;
  border-radius: 7px;
  border: 1px solid #334155;
  background: #1e293b;
  color: #f8fafc;
  font-size: 0.8rem;
  font-weight: 800;
  text-decoration: none;
  cursor: pointer;
}
.vbtn-green { background: var(--naver); color: #052e16; border-color: var(--naver-dark); }

.webtoon-stage {
  background: #0b0f19;
  border-radius: 14px;
  padding: 1rem 0.65rem 1.4rem;
  margin: 0.75rem 0 1.3rem;
  transition: background 0.2s ease;
}
.webtoon-stage.is-light {
  background: #ffffff;
  border: 1px solid var(--line);
}
.webtoon-strip {
  width: min(720px, 100%);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.webtoon-cut {
  margin: 0;
  border-radius: 10px;
  overflow: hidden;
  background: #ffffff;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.28);
}
.webtoon-cut-img {
  display: block;
  width: 100%;
  height: auto;
}
.viewer-react-bar {
  width: min(720px, 100%);
  margin: 1.1rem auto 0;
  background: #111827;
  border: 1px solid #1f2937;
  border-radius: 12px;
  padding: 0.85rem 1rem;
  color: #f8fafc;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}
.webtoon-stage.is-light .viewer-react-bar {
  background: #f8fafc;
  border-color: var(--line);
  color: var(--ink);
}
.rating-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: #fef08a;
  color: #854d0e;
  border: 1px solid #facc15;
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  font-size: 0.84rem;
  font-weight: 900;
  cursor: pointer;
}

/* Ads & Practical Guide */
.ad-box {
  margin: 1.35rem 0;
  padding: 0.88rem;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
}
.ad-disclosure {
  font-size: 0.75rem;
  color: var(--muted);
  margin: 0 0 0.45rem;
  text-align: center;
  font-weight: 600;
}
.coupang-search-wrap, .coupang-carousel-slot {
  width: 100%;
  max-width: 100%;
  overflow: hidden;
  display: flex;
  justify-content: center;
  border-radius: 10px;
}
.coupang-search-wrap iframe, .coupang-carousel-slot iframe { max-width: 100%; border: 0; }
.carousel-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0.9rem; }
@media (max-width: 980px) { .carousel-grid { grid-template-columns: 1fr; } }
.coupang-banner-card {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.85rem;
  padding: 1rem 1.1rem;
  border-radius: 12px;
  background: linear-gradient(135deg, #fff7ed 0%, #fef2f2 100%);
  border: 1.5px solid #fdba74;
}
.coupang-banner-card strong { display: block; font-size: 1rem; color: #9a3412; margin-bottom: 0.2rem; }
.coupang-banner-card span { display: block; font-size: 0.86rem; color: #475569; }
.coupang-card-actions { display: flex; flex-wrap: wrap; gap: 0.5rem; }

.guide-article {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 1.3rem;
  margin: 1.25rem 0;
}
.guide-article h2 { margin-top: 0; font-size: 1.2rem; color: var(--ink); }
.guide-article ul { padding-left: 1.2rem; }
.guide-article li { margin-bottom: 0.42rem; }

/* Binge Reader Stack (/studio/) */
.binge-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 1.1rem;
  margin-bottom: 1.2rem;
}
.binge-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.65rem;
  margin-top: 0.8rem;
}
@media (max-width: 720px) { .binge-strip { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.binge-strip img {
  display: block;
  width: 100%;
  height: auto;
  border-radius: 8px;
  border: 1px solid var(--line);
}

.site-footer {
  margin-top: 2rem;
  border-top: 1px solid var(--line);
  background: var(--surface);
  padding: 1.4rem 0 2.1rem;
  font-size: 0.84rem;
  color: var(--muted);
}
.footer-row { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 0.8rem; }
.footer-nav { display: flex; flex-wrap: wrap; gap: 0.85rem; }
.footer-nav a { text-decoration: none; font-weight: 700; }
"""

VIEWER_JS = """(function () {
  function initViewer() {
    var stage = document.getElementById("webtoonStage");
    var toggle = document.getElementById("themeToggleBtn");
    if (stage && toggle) {
      toggle.addEventListener("click", function () {
        var isLight = stage.classList.toggle("is-light");
        toggle.textContent = isLight ? "🌙 다크 뷰어" : "☀️ 라이트 뷰어";
      });
    }
    var rateBtn = document.getElementById("rateUpBtn");
    var starScore = document.getElementById("starScoreVal");
    if (rateBtn && starScore) {
      rateBtn.addEventListener("click", function () {
        if (rateBtn.dataset.voted === "1") return;
        rateBtn.dataset.voted = "1";
        starScore.textContent = "9.98 (별점 참여 완료!)";
        rateBtn.textContent = "⭐ 별점 반영됨";
      });
    }
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initViewer);
  } else {
    initViewer();
  }
})();
"""


def _wrap_svg_lines(text: str, max_units: float, max_lines: int) -> list[str]:
    words = str(text or "").split()
    lines: list[str] = []

    def _w(s: str) -> float:
        total = 0.0
        for ch in s:
            if ord(ch) > 127:
                total += 1.0
            elif ch == " ":
                total += 0.34
            else:
                total += 0.56
        return total

    cur = ""
    for w in words:
        cand = (cur + " " + w) if cur else w
        if _w(cand) <= max_units:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            if _w(w) > max_units:
                chunk = ""
                for ch in w:
                    if _w(chunk + ch) > max_units and chunk:
                        lines.append(chunk)
                        chunk = ch
                    else:
                        chunk += ch
                cur = chunk
            else:
                cur = w
    if cur:
        lines.append(cur)
    if max_lines and len(lines) > max_lines:
        cut = lines[:max_lines]
        cut[-1] = cut[-1][: max(2, len(cut[-1]) - 1)] + "…"
        return cut
    return lines or [""]


def _render_scene_backdrop(scene: str, x: int, y: int, w: int, h: int, theme: dict[str, str], dramatic: bool) -> str:
    parts: list[str] = [
        f'<defs>'
        f'<linearGradient id="bgGrad" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{theme["sky1"]}"/><stop offset="68%" stop-color="{theme["wall"]}"/><stop offset="100%" stop-color="{theme["floor"]}"/>'
        f'</linearGradient>'
        f'<radialGradient id="spotGrad" cx="50%" cy="45%" r="55%">'
        f'<stop offset="0%" stop-color="#ffffff" stop-opacity="0.45"/><stop offset="100%" stop-color="#0f172a" stop-opacity="0.18"/>'
        f'</radialGradient>'
        f'</defs>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#bgGrad)"/>',
        f'<rect x="{x}" y="{y + int(h*0.72)}" width="{w}" height="{int(h*0.28)}" fill="{theme["floor"]}" opacity="0.68"/>',
    ]

    if scene == "오피스":
        parts.extend([
            f'<rect x="{x+30}" y="{y+26}" width="210" height="165" rx="6" fill="#0f172a" stroke="#334155" stroke-width="4"/>',
            f'<rect x="{x+40}" y="{y+36}" width="92" height="145" fill="#1e3a5f"/>',
            f'<rect x="{x+140}" y="{y+36}" width="90" height="145" fill="#1e293b"/>',
            f'<rect x="{x+52}" y="{y+78}" width="18" height="90" fill="#334155"/><rect x="{x+76}" y="{y+58}" width="22" height="110" fill="#475569"/>',
            f'<rect x="{x+152}" y="{y+64}" width="24" height="104" fill="#334155"/><rect x="{x+184}" y="{y+90}" width="20" height="78" fill="#475569"/>',
            f'<rect x="{x+60}" y="{y+92}" width="6" height="6" fill="#fde047"/><rect x="{x+82}" y="{y+72}" width="7" height="7" fill="#fde047"/>',
            f'<rect x="{x+160}" y="{y+80}" width="7" height="7" fill="#fde047"/><rect x="{x+190}" y="{y+105}" width="6" height="6" fill="#38bdf8"/>',
            f'<circle cx="{x+w-195}" cy="{y+70}" r="32" fill="#ffffff" stroke="#0f172a" stroke-width="4"/>',
            f'<line x1="{x+w-195}" y1="{y+70}" x2="{x+w-195}" y2="{y+48}" stroke="#0f172a" stroke-width="4" stroke-linecap="round"/>',
            f'<line x1="{x+w-195}" y1="{y+70}" x2="{x+w-175}" y2="{y+75}" stroke="#e11d48" stroke-width="3" stroke-linecap="round"/>',
            f'<text x="{x+w-195}" y="{y+118}" text-anchor="middle" font-size="14" font-weight="800" fill="#0f172a">17:55 PM</text>',
            f'<rect x="{x+w-220}" y="{y+int(h*0.58)}" width="145" height="92" rx="8" fill="#cbd5e1" stroke="#0f172a" stroke-width="3"/>',
            f'<rect x="{x+w-220}" y="{y+int(h*0.58)+10}" width="130" height="70" fill="#0ea5e9" opacity="0.85"/>',
        ])
    elif scene == "톡방·메신저":
        parts.extend([
            f'<rect x="{x+w-270}" y="{y+22}" width="235" height="360" rx="26" fill="#0f172a" stroke="#334155" stroke-width="5"/>',
            f'<rect x="{x+w-256}" y="{y+44}" width="207" height="316" rx="14" fill="#b2c7d9"/>',
            f'<rect x="{x+w-256}" y="{y+44}" width="207" height="38" rx="8" fill="#1e293b"/>',
            f'<text x="{x+w-152}" y="{y+68}" text-anchor="middle" font-size="14" font-weight="800" fill="#f8fafc">단톡방 (99+)</text>',
            f'<rect x="{x+w-242}" y="{y+98}" width="138" height="44" rx="10" fill="#ffffff" stroke="#94a3b8" stroke-width="1.5"/>',
            f'<rect x="{x+w-200}" y="{y+158}" width="138" height="48" rx="10" fill="#fee500" stroke="#ca8a04" stroke-width="1.5"/>',
            f'<rect x="{x+w-242}" y="{y+224}" width="146" height="44" rx="10" fill="#ffffff" stroke="#ef4444" stroke-width="2"/>',
            f'<circle cx="{x+w-50}" cy="{y+36}" r="18" fill="#ef4444"/><text x="{x+w-50}" y="{y+42}" text-anchor="middle" font-size="13" font-weight="900" fill="#ffffff">!</text>',
        ])
    elif scene == "주차장·도로":
        parts.extend([
            f'<rect x="{x+40}" y="{y+24}" width="54" height="{h-60}" fill="#475569" stroke="#0f172a" stroke-width="3"/>',
            f'<rect x="{x+40}" y="{y+150}" width="54" height="54" fill="#facc15"/><text x="{x+67}" y="{y+184}" text-anchor="middle" font-size="22" font-weight="900" fill="#0f172a">B2</text>',
            f'<rect x="{x+180}" y="{y+22}" width="140" height="12" rx="6" fill="#e0f2fe"/><rect x="{x+420}" y="{y+22}" width="140" height="12" rx="6" fill="#e0f2fe"/>',
            f'<rect x="{x+w-280}" y="{y+int(h*0.44)}" width="245" height="118" rx="22" fill="#1e293b" stroke="#020617" stroke-width="4"/>',
            f'<path d="M {x+w-250} {y+int(h*0.44)} L {x+w-210} {y+int(h*0.32)} L {x+w-95} {y+int(h*0.32)} L {x+w-65} {y+int(h*0.44)} Z" fill="#334155" stroke="#020617" stroke-width="4"/>',
            f'<circle cx="{x+w-235}" cy="{y+int(h*0.56)}" r="20" fill="#fbbf24" opacity="0.9"/><circle cx="{x+w-85}" cy="{y+int(h*0.56)}" r="20" fill="#fbbf24" opacity="0.9"/>',
            f'<rect x="{x+w-192}" y="{y+int(h*0.56)}" width="64" height="22" rx="4" fill="#ffffff" stroke="#0f172a" stroke-width="2"/>',
            f'<text x="{x+w-160}" y="{y+int(h*0.56)+16}" text-anchor="middle" font-size="12" font-weight="900" fill="#0f172a">P+SIDE</text>',
        ])
    elif scene == "예식장·카페":
        parts.extend([
            f'<line x1="{x+160}" y1="{y}" x2="{x+160}" y2="{y+44}" stroke="#9d174d" stroke-width="3"/>',
            f'<ellipse cx="{x+160}" cy="{y+56}" rx="48" ry="18" fill="#fef08a" stroke="#be185d" stroke-width="3"/>',
            f'<line x1="{x+w-150}" y1="{y}" x2="{x+w-150}" y2="{y+48}" stroke="#9d174d" stroke-width="3"/>',
            f'<ellipse cx="{x+w-150}" cy="{y+60}" rx="42" ry="16" fill="#fef08a" stroke="#be185d" stroke-width="3"/>',
            f'<rect x="{x+w-250}" y="{y+int(h*0.58)}" width="215" height="84" rx="10" fill="#fff1f2" stroke="#be185d" stroke-width="3"/>',
            f'<rect x="{x+w-225}" y="{y+int(h*0.54)}" width="72" height="44" rx="5" fill="#ffffff" stroke="#0f172a" stroke-width="2.5"/>',
            f'<rect x="{x+w-135}" y="{y+int(h*0.55)}" width="76" height="40" rx="5" fill="#fef08a" stroke="#b45309" stroke-width="2"/>',
        ])
    elif scene == "미스터리야간":
        parts.extend([
            f'<rect x="{x+w-245}" y="{y+32}" width="180" height="250" rx="8" fill="#0f172a" stroke="#7c3aed" stroke-width="5"/>',
            f'<polygon points="{x+w-235},{y+42} {x+w-75},{y+42} {x+w-115},{y+272} {x+w-235},{y+272}" fill="#1e1b4b"/>',
            f'<circle cx="{x+w-120}" cy="{y+88}" r="28" fill="#e2e8f0" opacity="0.22"/>',
            f'<rect x="{x+40}" y="{y+44}" width="110" height="42" rx="8" fill="#020617" stroke="#ef4444" stroke-width="2.5"/>',
            f'<text x="{x+95}" y="{y+71}" text-anchor="middle" font-size="20" font-weight="900" fill="#f87171">01:58</text>',
        ])
    else:  # 법원·계약서
        parts.extend([
            f'<rect x="{x+w-245}" y="{y+42}" width="195" height="245" rx="10" fill="#ffffff" stroke="#0f172a" stroke-width="4"/>',
            f'<line x1="{x+w-220}" y1="{y+82}" x2="{x+w-75}" y2="{y+82}" stroke="#0f172a" stroke-width="5"/>',
            f'<line x1="{x+w-220}" y1="{y+112}" x2="{x+w-90}" y2="{y+112}" stroke="#64748b" stroke-width="3"/>',
            f'<line x1="{x+w-220}" y1="{y+138}" x2="{x+w-85}" y2="{y+138}" stroke="#64748b" stroke-width="3"/>',
            f'<rect x="{x+w-222}" y="{y+162}" width="150" height="36" rx="6" fill="#fef08a" stroke="#ca8a04" stroke-width="2"/>',
            f'<text x="{x+w-147}" y="{y+185}" text-anchor="middle" font-size="14" font-weight="900" fill="#854d0e">증거·특약 확정</text>',
            f'<circle cx="{x+w-95}" cy="{y+236}" r="28" fill="none" stroke="#dc2626" stroke-width="4"/>',
            f'<text x="{x+w-95}" y="{y+242}" text-anchor="middle" font-size="14" font-weight="900" fill="#dc2626">합법완료</text>',
        ])

    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#spotGrad)"/>')
    if dramatic:
        # Webtoon radial speed / concentration lines
        cx, cy = x + int(w * 0.36), y + int(h * 0.56)
        for deg in range(0, 360, 15):
            import math
            rad = math.radians(deg)
            x1 = int(cx + math.cos(rad) * 165)
            y1 = int(cy + math.sin(rad) * 165)
            x2 = int(cx + math.cos(rad) * 520)
            y2 = int(cy + math.sin(rad) * 520)
            parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#0f172a" stroke-width="2" opacity="0.26"/>')
    return "\n  ".join(parts)


def _render_webtoon_character(cx: int, cy: int, scale: float, expr: str, speaker: str, theme: dict[str, str]) -> str:
    is_villain = any(k in speaker for k in ("팀장", "빌런", "임대인", "총대", "판매자", "손님", "동기", "세대주"))
    coat = "#3f3f46" if is_villain else theme["coat"]
    hair = "#27272a" if is_villain else theme["hair"]
    tie = "#dc2626" if is_villain else theme["accent"]

    # Hair back + torso + lapel + tie + neck + ears + jaw/face + hair fringe
    parts: list[str] = [
        f'<g transform="translate({cx},{cy}) scale({scale:.2f})">',
        # Shoulders & jacket
        f'<path d="M -112 185 C -106 78, -68 58, -32 54 L 32 54 C 68 58, 106 78, 112 185 Z" fill="{coat}" stroke="#0f172a" stroke-width="5"/>',
        # Shirt V-neck
        f'<polygon points="-28,54 28,54 0,136" fill="{theme["shirt"]}" stroke="#0f172a" stroke-width="3.5"/>',
        f'<polygon points="-7,62 7,62 9,122 0,138 -9,122" fill="{tie}" stroke="#0f172a" stroke-width="2.5"/>',
        # Neck + collar shadow
        f'<rect x="-20" y="18" width="40" height="44" rx="10" fill="{theme["skin"]}" stroke="#0f172a" stroke-width="4"/>',
        f'<path d="M -20 34 Q 0 48 20 34 L 20 22 L -20 22 Z" fill="#0f172a" opacity="0.16"/>',
        # Ears
        f'<ellipse cx="-54" cy="-24" rx="10" ry="15" fill="{theme["skin"]}" stroke="#0f172a" stroke-width="3.5"/>',
        f'<ellipse cx="54" cy="-24" rx="10" ry="15" fill="{theme["skin"]}" stroke="#0f172a" stroke-width="3.5"/>',
        # Back hair silhouette
        f'<path d="M -64 -24 C -68 -96, 68 -96, 64 -24 Z" fill="{hair}"/>',
        # Face contour (manhwa oval/chin)
        f'<path d="M -52 -46 C -54 8, -30 34, 0 36 C 30 34, 54 8, 52 -46 C 52 -84, -52 -84, -52 -46 Z" fill="{theme["skin"]}" stroke="#0f172a" stroke-width="4.5"/>',
        # Front spiky/layered hair
        f'<path d="M -56 -36 C -58 -92, 58 -94, 56 -36 C 42 -60, 26 -42, 16 -58 C 4 -40, -12 -58, -24 -40 C -36 -56, -46 -44, -56 -36 Z" fill="{hair}" stroke="#0f172a" stroke-width="3.5"/>',
        f'<path d="M -28 -68 Q 0 -80 28 -68" fill="none" stroke="#ffffff" stroke-width="3" opacity="0.32" stroke-linecap="round"/>',
    ]

    # Eyes, eyebrows, mouth & webtoon emotion markers by expression
    if expr == "사이다미소":
        parts.extend([
            '<path d="M -36 -40 Q -20 -48 -8 -40" fill="none" stroke="#0f172a" stroke-width="4" stroke-linecap="round"/>',
            '<path d="M 8 -40 Q 20 -48 36 -40" fill="none" stroke="#0f172a" stroke-width="4" stroke-linecap="round"/>',
            '<path d="M -32 -22 Q -20 -34 -8 -22" fill="none" stroke="#0f172a" stroke-width="5" stroke-linecap="round"/>',
            '<path d="M 8 -22 Q 20 -34 32 -22" fill="none" stroke="#0f172a" stroke-width="5" stroke-linecap="round"/>',
            '<path d="M -18 4 Q 0 22 18 4 Z" fill="#ffffff" stroke="#0f172a" stroke-width="3.5"/>',
            '<circle cx="-32" cy="-6" r="7" fill="#fb7185" opacity="0.45"/><circle cx="32" cy="-6" r="7" fill="#fb7185" opacity="0.45"/>',
            '<text x="68" y="-66" font-size="30">✨</text>',
        ])
    elif expr == "분노":
        parts.extend([
            '<line x1="-38" y1="-46" x2="-8" y2="-32" stroke="#0f172a" stroke-width="5.5" stroke-linecap="round"/>',
            '<line x1="38" y1="-46" x2="8" y2="-32" stroke="#0f172a" stroke-width="5.5" stroke-linecap="round"/>',
            '<ellipse cx="-20" cy="-22" rx="8" ry="6" fill="#ffffff" stroke="#0f172a" stroke-width="3"/>',
            '<ellipse cx="20" cy="-22" rx="8" ry="6" fill="#ffffff" stroke="#0f172a" stroke-width="3"/>',
            '<circle cx="-20" cy="-22" r="3.5" fill="#dc2626"/><circle cx="20" cy="-22" r="3.5" fill="#dc2626"/>',
            '<ellipse cx="0" cy="10" rx="18" ry="12" fill="#991b1b" stroke="#0f172a" stroke-width="3.5"/>',
            '<rect x="-12" y="2" width="24" height="5" fill="#ffffff"/>',
            '<text x="64" y="-62" font-size="28">💢</text>',
        ])
    elif expr == "각성":
        parts.extend([
            '<rect x="-38" y="-34" width="32" height="18" rx="4" fill="#ffffff" stroke="#0f172a" stroke-width="4"/>',
            '<rect x="6" y="-34" width="32" height="18" rx="4" fill="#ffffff" stroke="#0f172a" stroke-width="4"/>',
            '<line x1="-6" y1="-25" x2="6" y2="-25" stroke="#0f172a" stroke-width="4"/>',
            '<line x1="-33" y1="-29" x2="-15" y2="-20" stroke="#38bdf8" stroke-width="4" opacity="0.8"/>',
            '<line x1="11" y1="-29" x2="29" y2="-20" stroke="#38bdf8" stroke-width="4" opacity="0.8"/>',
            '<path d="M -14 10 Q 4 16 20 2" fill="none" stroke="#0f172a" stroke-width="4.5" stroke-linecap="round"/>',
            '<text x="68" y="-68" font-size="30">⚡</text>',
        ])
    elif expr in ("당황", "충격"):
        parts.extend([
            '<path d="M -36 -44 Q -22 -52 -10 -42" fill="none" stroke="#0f172a" stroke-width="4"/>',
            '<path d="M 10 -42 Q 22 -52 36 -44" fill="none" stroke="#0f172a" stroke-width="4"/>',
            '<circle cx="-20" cy="-22" r="10" fill="#ffffff" stroke="#0f172a" stroke-width="3.5"/>',
            '<circle cx="20" cy="-22" r="10" fill="#ffffff" stroke="#0f172a" stroke-width="3.5"/>',
            '<circle cx="-20" cy="-22" r="3" fill="#0f172a"/><circle cx="20" cy="-22" r="3" fill="#0f172a"/>',
            '<ellipse cx="0" cy="12" rx="14" ry="13" fill="#7f1d1d" stroke="#0f172a" stroke-width="3.5"/>',
            '<text x="64" y="-58" font-size="28">💧</text>',
        ])
    elif expr in ("억울", "눈물"):
        parts.extend([
            '<line x1="-36" y1="-34" x2="-10" y2="-44" stroke="#0f172a" stroke-width="4" stroke-linecap="round"/>',
            '<line x1="36" y1="-34" x2="10" y2="-44" stroke="#0f172a" stroke-width="4" stroke-linecap="round"/>',
            '<ellipse cx="-20" cy="-20" rx="8" ry="8" fill="#0f172a"/><circle cx="-18" cy="-23" r="3" fill="#ffffff"/>',
            '<ellipse cx="20" cy="-20" rx="8" ry="8" fill="#0f172a"/><circle cx="22" cy="-23" r="3" fill="#ffffff"/>',
            '<ellipse cx="-22" cy="-6" rx="4" ry="8" fill="#60a5fa" opacity="0.85"/><ellipse cx="22" cy="-6" rx="4" ry="8" fill="#60a5fa" opacity="0.85"/>',
            '<path d="M -14 14 Q 0 4 14 14" fill="none" stroke="#0f172a" stroke-width="4" stroke-linecap="round"/>',
        ])
    else:  # 무표정
        parts.extend([
            '<line x1="-34" y1="-38" x2="-10" y2="-38" stroke="#0f172a" stroke-width="4"/>',
            '<line x1="10" y1="-38" x2="34" y2="-38" stroke="#0f172a" stroke-width="4"/>',
            '<ellipse cx="-20" cy="-22" rx="7" ry="6" fill="#0f172a"/><circle cx="-18" cy="-24" r="2.2" fill="#ffffff"/>',
            '<ellipse cx="20" cy="-22" rx="7" ry="6" fill="#0f172a"/><circle cx="22" cy="-24" r="2.2" fill="#ffffff"/>',
            '<line x1="-12" y1="10" x2="12" y2="10" stroke="#0f172a" stroke-width="4" stroke-linecap="round"/>',
        ])

    # Action hand holding smartphone/document for realism
    parts.extend([
        f'<rect x="64" y="64" width="46" height="72" rx="8" fill="#0f172a" stroke="#ffffff" stroke-width="2.5" transform="rotate(-10 86 100)"/>',
        f'<rect x="69" y="72" width="36" height="54" rx="4" fill="#38bdf8" opacity="0.9" transform="rotate(-10 86 100)"/>',
        f'<circle cx="62" cy="112" r="14" fill="{theme["skin"]}" stroke="#0f172a" stroke-width="3.5"/>',
        '</g>',
    ])
    return "\n  ".join(parts)


def render_cover_svg(idx: int, ep: dict) -> str:
    p1 = ep["panels"][0]
    theme = SCENE_THEMES.get(p1.get("scene", "오피스"), SCENE_THEMES["오피스"])
    sfx = p1.get("sfx", "사이다!")
    dlg_lines = _wrap_svg_lines(p1.get("dialogue", ep["hook"]), 14.0, 2)
    dlg_svg = "\n  ".join(
        f'<text x="195" y="{318 + i * 26}" text-anchor="middle" font-size="19" font-weight="900" fill="#0f172a" font-family="Noto Sans KR, Apple SD Gothic Neo, Malgun Gothic, sans-serif">{escape(ln)}</text>'
        for i, ln in enumerate(dlg_lines)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 420" width="600" height="420" role="img" aria-label="{escape(ep["title"])}">
  {_render_scene_backdrop(p1.get("scene", "오피스"), 0, 0, 600, 420, theme, True)}
  {_render_webtoon_character(452, 260, 1.18, p1.get("expression", "사이다미소"), p1.get("speaker", "나"), theme)}
  <!-- Bottom comic dialogue punchline card (distinct from HTML title below) -->
  <rect x="26" y="282" width="338" height="106" rx="16" fill="#ffffff" stroke="#0f172a" stroke-width="4.5"/>
  <rect x="42" y="266" width="120" height="28" rx="999" fill="#0f172a"/>
  <text x="102" y="285" text-anchor="middle" font-size="13" font-weight="900" fill="#00dc64" font-family="Noto Sans KR, sans-serif">{escape(p1.get("speaker", "주인공"))}</text>
  {dlg_svg}
  <g transform="translate(115, 118) rotate(-8)">
    <rect x="-74" y="-24" width="148" height="48" rx="12" fill="#fef08a" stroke="#b91c1c" stroke-width="4"/>
    <text x="0" y="9" text-anchor="middle" font-size="24" font-weight="900" fill="#b91c1c" font-family="Noto Sans KR, sans-serif">{escape(sfx)}</text>
  </g>
</svg>
'''


def render_panel_svg(idx: int, ep: dict, panel: dict) -> str:
    scene = panel.get("scene", "오피스")
    expr = panel.get("expression", "사이다미소")
    btype = panel.get("bubbleType", "일반")
    sfx = panel.get("sfx", "두둥!")
    speaker = panel.get("speaker", "화자")
    theme = SCENE_THEMES.get(scene, SCENE_THEMES["오피스"])
    dramatic = btype == "외침(사이다)" or expr in ("분노", "각성", "충격")

    narr_lines = _wrap_svg_lines(panel.get("narration", ""), 29.0, 2)
    narr_svg = "\n  ".join(
        f'<text x="38" y="{78 + i * 28}" font-size="21" font-weight="800" fill="#0f172a" font-family="Noto Sans KR, Apple SD Gothic Neo, sans-serif">{escape(ln)}</text>'
        for i, ln in enumerate(narr_lines)
    )

    dlg_lines = _wrap_svg_lines(panel.get("dialogue", ""), 23.0, 3)
    dlg_svg = "\n  ".join(
        f'<text x="360" y="{790 + i * 31}" text-anchor="middle" font-size="22" font-weight="800" fill="#0f172a" font-family="Noto Sans KR, Apple SD Gothic Neo, sans-serif">{escape(ln)}</text>'
        for i, ln in enumerate(dlg_lines)
    )

    # Speech balloon styling matching Naver Webtoon comic conventions
    if btype == "외침(사이다)":
        balloon_svg = (
            '<polygon points="36,722 150,730 190,710 245,730 350,714 440,730 530,710 684,724 '
            '672,796 692,838 666,892 490,884 410,900 320,886 190,898 54,886 30,822" '
            'fill="#fffbeb" stroke="#dc2626" stroke-width="5"/>'
        )
    elif btype == "속마음":
        balloon_svg = (
            '<rect x="44" y="724" width="632" height="164" rx="46" fill="#f8fafc" stroke="#334155" stroke-width="4" stroke-dasharray="12 7"/>'
            '<circle cx="242" cy="706" r="10" fill="#f8fafc" stroke="#334155" stroke-width="3"/>'
            '<circle cx="256" cy="686" r="6" fill="#f8fafc" stroke="#334155" stroke-width="2.5"/>'
        )
    else:
        balloon_svg = (
            '<rect x="42" y="724" width="636" height="164" rx="28" fill="#ffffff" stroke="#0f172a" stroke-width="4.5"/>'
            '<polygon points="240,726 266,690 294,726" fill="#ffffff" stroke="#0f172a" stroke-width="4.5"/>'
            '<line x1="244" y1="726" x2="290" y2="726" stroke="#ffffff" stroke-width="6"/>'
        )

    stage_label = f"{idx + 1}화 · {panel['panelNumber']}컷 ({panel['stage']})"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 920" width="720" height="920" role="img" aria-label="{escape(stage_label)} - {escape(panel.get('dialogue', ''))}">
  <rect x="0" y="0" width="720" height="920" fill="#ffffff"/>
  <!-- Top Narration Bar -->
  <rect x="20" y="16" width="680" height="106" rx="12" fill="#f8fafc" stroke="#0f172a" stroke-width="4"/>
  <rect x="34" y="26" width="210" height="28" rx="6" fill="#00dc64"/>
  <text x="139" y="45" text-anchor="middle" font-size="14" font-weight="900" fill="#052e16" font-family="Noto Sans KR, sans-serif">{escape(stage_label)}</text>
  <text x="684" y="45" text-anchor="end" font-size="13" font-weight="800" fill="#64748b" font-family="Noto Sans KR, sans-serif">{escape(scene)} · {escape(expr)}</text>
  {narr_svg}

  <!-- Central Illustrated Artwork Stage -->
  <g>
    <clipPath id="stageClip"><rect x="20" y="136" width="680" height="572" rx="14"/></clipPath>
    <g clip-path="url(#stageClip)">
      {_render_scene_backdrop(scene, 20, 136, 680, 572, theme, dramatic)}
      {_render_webtoon_character(250, 498, 1.55, expr, speaker, theme)}
    </g>
    <rect x="20" y="136" width="680" height="572" rx="14" fill="none" stroke="#0f172a" stroke-width="5"/>
  </g>

  <!-- Tilted Comic SFX Badge -->
  <g transform="translate(592, 188) rotate(-8)">
    <rect x="-78" y="-26" width="156" height="52" rx="12" fill="#fef08a" stroke="#b91c1c" stroke-width="4"/>
    <text x="0" y="9" text-anchor="middle" font-size="25" font-weight="900" fill="#b91c1c" font-family="Noto Sans KR, sans-serif">{escape(sfx)}</text>
  </g>

  <!-- Speech Balloon & Dialogue -->
  {balloon_svg}
  <rect x="260" y="698" width="200" height="32" rx="999" fill="#0f172a"/>
  <text x="360" y="719" text-anchor="middle" font-size="15" font-weight="900" fill="#00dc64" font-family="Noto Sans KR, sans-serif">{escape(speaker)}</text>
  {dlg_svg}
  <text x="700" y="908" text-anchor="end" font-size="12" font-weight="700" fill="#94a3b8" font-family="Noto Sans KR, sans-serif">GuideHollow 웹툰 · toon.guidehollow.com</text>
</svg>
'''


def build_ad_manager_js(ad_mode: str) -> str:
    return f"""// Dual-Mode Ad Manager for GuideHollow 웹툰 (toon.guidehollow.com)
// Switch permanently via `python3 tools/build.py --ad-mode adsense` after AdSense approval,
// or preview live by appending `?ad_mode=adsense` to any URL.
(function () {{
  const params = new URLSearchParams(window.location.search);
  const override = params.get("ad_mode");
  const AD_MODE = (override === "adsense" || override === "coupang") ? override : "{ad_mode}";
  window.GH_TOON_AD_MODE = AD_MODE;

  const COUPANG_FTC = "{COUPANG_FTC}";
  const ADSENSE_PUB = "{ADSENSE_PUB}";

  const CAROUSELS = {{
    digital: {{ id: 1050468, label: "가전·디지털 인기 베스트" }},
    living: {{ id: 1050469, label: "생활·수납 인기 베스트" }},
    kitchen: {{ id: 1050470, label: "주방·새출발 인기 베스트" }}
  }};

  function esc(v) {{
    return String(v || "").replace(/[&<>"']/g, function (c) {{
      return {{ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\\"": "&quot;", "'": "&#39;" }}[c];
    }});
  }}

  function renderAdSenseSlot(container, layout) {{
    const isArticle = layout === "in-article";
    container.innerHTML =
      '<div class="ad-disclosure">Advertisement</div>' +
      '<ins class="adsbygoogle" style="display:block;min-height:90px;text-align:center;" ' +
      'data-ad-client="' + ADSENSE_PUB + '" data-ad-slot="auto" ' +
      (isArticle ? 'data-ad-layout="in-article" data-ad-format="fluid" ' : 'data-ad-format="auto" data-full-width-responsive="true" ') +
      '></ins>';
    try {{
      if (window.adsbygoogle) window.adsbygoogle.push({{}});
    }} catch (e) {{}}
  }}

  function ensureAdSenseScript() {{
    if (document.querySelector('script[src*="adsbygoogle.js"]')) return;
    const s = document.createElement("script");
    s.async = true;
    s.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + ADSENSE_PUB;
    s.crossOrigin = "anonymous";
    document.head.appendChild(s);
  }}

  function renderCoupangSlot(container) {{
    const kind = container.dataset.adKind || "search";
    if (kind === "search") {{
      container.innerHTML =
        '<p class="ad-disclosure">' + COUPANG_FTC + '</p>' +
        '<div class="coupang-search-wrap">' +
        '<iframe src="https://coupa.ng/cqZC1w" width="100%" height="75" frameborder="0" scrolling="no" referrerpolicy="unsafe-url" title="쿠팡 파트너스 상품 검색 위젯"></iframe>' +
        '</div>';
      return;
    }}
    if (kind === "carousels") {{
      container.innerHTML =
        '<p class="ad-disclosure">' + COUPANG_FTC + ' (고단가·생활 실속 비교 배너)</p>' +
        '<div class="carousel-grid">' +
        Object.values(CAROUSELS).map(function (c) {{
          return '<div class="coupang-carousel-slot">' +
            '<iframe src="https://ads-partners.coupang.com/widgets.html?id=' + c.id + '&template=carousel&trackingCode=AF2560572&subId=ghshopping&width=320&height=320&tsource=" width="320" height="320" frameborder="0" scrolling="no" referrerpolicy="unsafe-url" loading="lazy" title="' + esc(c.label) + '"></iframe>' +
            '</div>';
        }}).join("") +
        '</div>';
      return;
    }}
    if (kind === "contextual") {{
      const badge = container.dataset.badge || "생활 실속 추천 배너";
      const title = container.dataset.title || "쿠팡 파트너스 인기 추천 상품 보기";
      const reason = container.dataset.reason || "웹툰 주제와 관련된 실용 상품을 바로 비교해 보세요.";
      const url = container.dataset.url || "https://link.coupang.com/a/iG9mTjBUg8";
      const cta = container.dataset.cta || "쿠팡에서 가격 확인하기";
      const guideUrl = container.dataset.guideUrl || "https://shopping.guidehollow.com/";
      const guideLabel = container.dataset.guideLabel || "GuideHollow 구매 기준 보기";
      const wid = container.dataset.widgetId || "1050469";
      container.innerHTML =
        '<p class="ad-disclosure">' + COUPANG_FTC + '</p>' +
        '<div class="coupang-banner-card">' +
          '<div style="flex:1 1 280px;">' +
            '<small style="font-weight:800;color:#b45309;">' + esc(badge) + '</small>' +
            '<strong>' + esc(title) + '</strong>' +
            '<span>' + esc(reason) + '</span>' +
            '<div class="coupang-card-actions" style="margin-top:0.7rem;">' +
              '<a class="btn btn-coupang" href="' + esc(url) + '" target="_blank" rel="noopener noreferrer sponsored">' + esc(cta) + ' →</a>' +
              '<a class="btn" href="' + esc(guideUrl) + '" target="_blank" rel="noopener noreferrer">' + esc(guideLabel) + '</a>' +
            '</div>' +
          '</div>' +
          '<div class="coupang-carousel-slot" style="flex:0 0 320px;max-width:100%;">' +
            '<iframe src="https://ads-partners.coupang.com/widgets.html?id=' + esc(wid) + '&template=carousel&trackingCode=AF2560572&subId=ghshopping&width=320&height=320&tsource=" width="320" height="320" frameborder="0" scrolling="no" referrerpolicy="unsafe-url" loading="lazy" title="쿠팡 추천 캐러셀 배너"></iframe>' +
          '</div>' +
        '</div>';
    }}
  }}

  function mountAllAds() {{
    const slots = document.querySelectorAll("[data-gh-ad-slot]");
    if (!slots.length) return;
    if (AD_MODE === "adsense") {{
      ensureAdSenseScript();
      slots.forEach(function (el) {{
        renderAdSenseSlot(el, el.dataset.adLayout || "auto");
      }});
    }} else {{
      slots.forEach(renderCoupangSlot);
    }}
  }}

  if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", mountAllAds);
  }} else {{
    mountAllAds();
  }}
}})();
"""


def shell_html(title: str, description: str, canonical: str, active_nav: str, body: str, extra_scripts: str = "") -> str:
    nav_items = [
        ("home", "/", "📖 썰툰 연재관"),
        ("studio", "/studio/", "🔥 전체 정주행"),
        ("about", "/about/", "연재·편집 원칙"),
        ("shop", "https://shopping.guidehollow.com/", "🛒 쇼핑 가이드"),
    ]
    nav_links = []
    for key, href, label in nav_items:
        cls = "active" if key == active_nav else ""
        ext = ' target="_blank" rel="noopener noreferrer"' if href.startswith("http") else ""
        nav_links.append(f'<a href="{href}" class="{cls}"{ext}>{label}</a>')
    nav_html = "".join(nav_links)
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(description)}" />
  <link rel="canonical" href="{escape(canonical)}" />
  <meta property="og:type" content="website" />
  <meta property="og:locale" content="ko_KR" />
  <meta property="og:site_name" content="GuideHollow 웹툰" />
  <meta property="og:url" content="{escape(canonical)}" />
  <meta property="og:title" content="{escape(title)}" />
  <meta property="og:description" content="{escape(description)}" />
  <link rel="stylesheet" href="/assets/style.css" />
  <script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag("js", new Date());
    gtag("config", "{GA4_ID}");
  </script>
</head>
<body>
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="/">
        <span class="brand-n">웹툰</span>
        <span>GuideHollow 썰툰</span>
        <span class="brand-sub">세로 정주행</span>
      </a>
      <nav class="nav" aria-label="주요 메뉴">{nav_html}</nav>
    </div>
  </header>
  <main class="wrap">
    {body}
  </main>
  <footer class="site-footer">
    <div class="wrap footer-row">
      <div>© 2026 GuideHollow 웹툰 (toon.guidehollow.com) · 전담 편집팀 자체 연재 사이다 썰툰</div>
      <nav class="footer-nav" aria-label="정책 메뉴">
        <a href="/about/">연재·편집 원칙</a>
        <a href="/privacy/">개인정보처리방침</a>
        <a href="/terms/">이용약관</a>
        <a href="/contact/">문의하기</a>
      </nav>
    </div>
  </footer>
  <script src="/assets/ad-manager.js" defer></script>
  {extra_scripts}
</body>
</html>
"""


def build_home_html() -> str:
    genres = [
        ("all", "전체 10화"),
        ("office", "💼 직장·알바"),
        ("love", "💔 연애·결혼"),
        ("car", "🚗 주차·소비자"),
        ("mystery", "🕯️ 괴담·주거"),
        ("finance", "💸 전세·중고거래"),
    ]
    genre_btns = "".join(
        f'<button type="button" class="genre-pill {"is-active" if k == "all" else ""}" data-genre="{k}">{label}</button>'
        for k, label in genres
    )
    cards = []
    for idx, ep in enumerate(EPISODES):
        ep_num = f"{idx + 1}화"
        cards.append(
            f"""<a class="ep-card" data-genre="{ep['genreKey']}" href="/episodes/{ep['id']}/">
  <div class="toon-thumb-box">
    <img class="toon-thumb-img" src="/assets/toons/{ep['id']}/cover.svg" width="600" height="420" alt="{escape(ep['title'])} 웹툰 표지" loading="eager" />
    <span class="ep-num-badge">{ep_num} 완결</span>
    <span class="ep-up-badge">UP</span>
  </div>
  <div class="ep-card-body">
    <div class="ep-meta"><span>{ep['emoji']} {escape(ep['genre'])}</span><span class="ep-star">★ 9.96</span></div>
    <h3>{escape(ep['title'])}</h3>
    <div class="ep-hook">{escape(ep['hook'])}</div>
    <span class="ep-read-cta">6컷 웹툰 바로 보기 →</span>
  </div>
</a>"""
        )
    cards_html = "\n".join(cards)
    body = f"""
    <section class="hero">
      <span class="hero-kicker">GUIDEHOLLOW WEBTOON · 오리지널 세로 스크롤 연재</span>
      <h1>스크롤만 내리면 바로 감상하는 사이다 썰툰 웹툰 10화</h1>
      <p>직장·전세 계약·이중주차·중고거래 분쟁까지 편집팀이 직접 그려 연재하는 6컷 세로 웹툰을 클릭 한 번으로 바로 정주행하세요.</p>
      <div class="hero-actions">
        <a class="btn btn-naver" href="/episodes/{EPISODES[0]['id']}/">▶ 1화부터 바로 감상하기</a>
        <a class="btn btn-dark" href="/studio/">📚 전체 10화 미리보기·정주행</a>
      </div>
    </section>

    <section class="ad-box" data-gh-ad-slot="top" data-ad-kind="search" data-ad-layout="auto" aria-label="스폰서 검색 배너"></section>

    <section id="episodes" aria-label="오리지널 썰툰 연재 목록">
      <div class="section-head">
        <h2>오늘의 사이다 웹툰 전체 회차 (10화 완결)</h2>
        <span style="font-size:0.84rem;color:var(--muted);font-weight:700;">세로 스크롤 6컷 풀 일러스트</span>
      </div>
      <div class="genre-bar" role="group" aria-label="장르 필터">{genre_btns}</div>
      <div class="episode-grid" id="episodeGrid">{cards_html}</div>
    </section>

    <section class="ad-box" data-gh-ad-slot="mid" data-ad-kind="carousels" data-ad-layout="in-article" aria-label="쿠팡 파트너스 인기 상품 배너"></section>

    <article class="guide-article">
      <h2>GuideHollow 웹툰 연재 원칙</h2>
      <p>본 사이트의 모든 웹툰 에피소드는 전담 편집팀이 실제 생활 공감 사례에서 특정인·상호·위치 식별 요소를 완전히 제거해 각색·작화한 오리지널 연재물입니다.</p>
      <p>각 회차 마지막에는 사이다 결말에서 그치지 않고 <strong>실제로 법적·금전적 손실을 예방하는 현실 대응 체크리스트</strong>를 함께 제공합니다.</p>
    </article>

    <script>
      document.querySelectorAll(".genre-pill").forEach(function (btn) {{
        btn.addEventListener("click", function () {{
          var g = btn.dataset.genre;
          document.querySelectorAll(".genre-pill").forEach(function (b) {{ b.classList.toggle("is-active", b === btn); }});
          document.querySelectorAll(".ep-card").forEach(function (card) {{
            card.style.display = (g === "all" || card.dataset.genre === g) ? "flex" : "none";
          }});
        }});
      }});
    </script>
    """
    return shell_html(
        "GuideHollow 썰툰 — 세로 스크롤 사이다 웹툰 연재관",
        "직장·결혼·이중주차·전세 계약·중고거래 사이다 썰툰을 네이버 웹툰 스타일 세로 컷 그림으로 감상하는 무료 웹툰 연재관입니다.",
        f"{ORIGIN}/",
        "home",
        body,
    )


def build_binge_archive_html() -> str:
    sections = []
    for idx, ep in enumerate(EPISODES):
        thumbs = "".join(
            f'<a href="/episodes/{ep["id"]}/"><img src="/assets/toons/{ep["id"]}/cut-0{p["panelNumber"]}.svg" width="360" height="460" alt="{idx+1}화 {p["panelNumber"]}컷 미리보기" loading="eager" /></a>'
            for p in ep["panels"]
        )
        sections.append(
            f"""<article class="binge-card">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.6rem;">
    <div>
      <span class="brand-sub">{idx + 1}화 · {escape(ep['genre'])}</span>
      <h2 style="margin:0.35rem 0 0.25rem;font-size:1.12rem;"><a href="/episodes/{ep['id']}/" style="text-decoration:none;">{escape(ep['title'])}</a></h2>
      <p style="margin:0;color:var(--muted);font-size:0.88rem;">{escape(ep['hook'])}</p>
    </div>
    <a class="btn btn-naver" href="/episodes/{ep['id']}/">큰 세로 화면으로 보기 →</a>
  </div>
  <div class="binge-strip">{thumbs}</div>
</article>"""
        )
    body = f"""
    <section class="hero">
      <span class="hero-kicker">ALL EPISODES ARCHIVE</span>
      <h1>전체 10화 웹툰 한눈에 몰아보기</h1>
      <p>전담 팀이 제작한 전 회차 60컷 일러스트를 한 페이지에서 미리 확인하고, 마음에 드는 회차를 눌러 큰 세로 웹툰 뷰어로 바로 감상하세요.</p>
    </section>
    <section class="ad-box" data-gh-ad-slot="archive-top" data-ad-kind="search" data-ad-layout="auto" aria-label="스폰서 검색 배너"></section>
    <section aria-label="전체 회차 컷 아카이브">{"".join(sections)}</section>
    <section class="ad-box" data-gh-ad-slot="archive-bottom" data-ad-kind="carousels" data-ad-layout="auto" aria-label="쿠팡 파트너스 인기 상품 배너"></section>
    """
    return shell_html(
        "전체 회차 정주행 모아보기 | GuideHollow 웹툰",
        "GuideHollow 오리지널 썰툰 전체 10화 60컷 일러스트를 한눈에 모아보고 세로 뷰어로 감상하세요.",
        f"{ORIGIN}/studio/",
        "studio",
        body,
    )


def build_episode_html(idx: int, ep: dict) -> str:
    prev_ep = EPISODES[idx - 1] if idx > 0 else None
    next_ep = EPISODES[idx + 1] if idx + 1 < len(EPISODES) else None
    cp = ep["coupang"]

    cuts_html = []
    for p in ep["panels"]:
        n = p["panelNumber"]
        cuts_html.append(
            f"""<figure class="webtoon-cut">
  <img class="webtoon-cut-img" src="/assets/toons/{ep['id']}/cut-0{n}.svg" width="720" height="920" alt="{idx + 1}화 {n}컷 - {escape(p['narration'])} / {escape(p['dialogue'])}" loading="eager" />
</figure>"""
        )

    paragraphs = "".join(f"<p>{escape(para)}</p>" for para in ep["guideBody"])
    checklist_items = "".join(f"<li>{escape(item)}</li>" for item in ep["checklist"])
    nav_btns = ['<a class="btn" href="/">📚 전체 목록</a>']
    if prev_ep:
        nav_btns.append(f'<a class="btn" href="/episodes/{prev_ep["id"]}/">◀ 이전화 ({idx}화)</a>')
    if next_ep:
        nav_btns.append(f'<a class="btn btn-naver" href="/episodes/{next_ep["id"]}/">다음화 ({idx + 2}화) 보기 ▶</a>')

    prev_bar = f'<a class="vbtn" href="/episodes/{prev_ep["id"]}/">◀ 이전화</a>' if prev_ep else ""
    next_bar = f'<a class="vbtn vbtn-green" href="/episodes/{next_ep["id"]}/">다음화 ▶</a>' if next_ep else ""

    body = f"""
    <div class="viewer-bar">
      <div class="viewer-title-wrap">
        <div class="viewer-ep-tag">{idx + 1}화 · {escape(ep['genre'])} · 6컷 세로 웹툰</div>
        <h1>{escape(ep['title'])}</h1>
      </div>
      <div class="viewer-controls">
        <a class="vbtn" href="/">← 목록</a>
        <button type="button" class="vbtn" id="themeToggleBtn">☀️ 라이트 뷰어</button>
        {prev_bar}
        {next_bar}
      </div>
    </div>

    <section class="ad-box" data-gh-ad-slot="ep-top" data-ad-kind="search" data-ad-layout="auto" aria-label="스폰서 검색 배너"></section>

    <section class="webtoon-stage" id="webtoonStage" aria-label="세로 스크롤 웹툰 감상 영역">
      <div class="webtoon-strip">
        {''.join(cuts_html)}
      </div>
      <div class="viewer-react-bar">
        <div>
          <strong style="font-size:0.95rem;">이 화 평점</strong>
          <span style="margin-left:0.5rem;font-weight:900;color:#facc15;">★ <span id="starScoreVal">9.96</span></span>
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:0.45rem;align-items:center;">
          <button type="button" class="rating-pill" id="rateUpBtn">⭐ 별점 10점 주기</button>
          {next_bar}
        </div>
      </div>
      <p style="font-size:0.78rem;color:#94a3b8;text-align:center;margin:0.85rem 0 0;">※ 본 웹툰은 전담 편집팀이 특정인·상호 식별 요소를 제거해 자체 각색·작화한 창작 연재물입니다.</p>
    </section>

    <section class="ad-box"
      data-gh-ad-slot="ep-mid"
      data-ad-kind="contextual"
      data-ad-layout="in-article"
      data-widget-id="{cp['widgetId']}"
      data-badge="{escape(cp['badge'])}"
      data-title="{escape(cp['itemTitle'])}"
      data-reason="{escape(cp['reason'])}"
      data-cta="{escape(cp['ctaText'])}"
      data-url="{escape(cp['affiliateUrl'])}"
      data-guide-url="{escape(cp['guideUrl'])}"
      data-guide-label="{escape(cp['guideLabel'])}"
      aria-label="상황 맞춤 생활·상품 추천 배너"></section>

    <article class="guide-article">
      <h2>{escape(ep['guideTitle'])}</h2>
      {paragraphs}
      <h3>실전 확인 체크리스트</h3>
      <ul>{checklist_items}</ul>
      <div style="display:flex;flex-wrap:wrap;gap:0.6rem;margin-top:1.1rem;">
        {''.join(nav_btns)}
      </div>
    </article>

    <section class="ad-box" data-gh-ad-slot="ep-bottom" data-ad-kind="carousels" data-ad-layout="auto" aria-label="쿠팡 파트너스 인기 상품 배너"></section>
    """
    return shell_html(
        f"{idx + 1}화. {ep['title']} | GuideHollow 웹툰",
        ep["summary"],
        f"{ORIGIN}/episodes/{ep['id']}/",
        "home",
        body,
        extra_scripts='<script src="/assets/viewer.js" defer></script>',
    )


def build_policy_pages() -> dict[str, str]:
    pages = {
        "about": (
            "연재·편집 원칙 | GuideHollow 웹툰",
            "GuideHollow 웹툰 포털의 오리지널 썰툰 제작·각색·생활 정보 안내 원칙입니다.",
            """
            <article class="guide-article" style="margin-top:1.5rem;">
              <h1>GuideHollow 웹툰 (toon.guidehollow.com) 연재 및 편집 원칙</h1>
              <p><strong>GuideHollow 웹툰</strong>은 직장·계약·주차·소비자 분쟁 등 일상에서 흔히 겪는 억울한 상황을 전담 편집팀이 6컷 세로 웹툰으로 직접 각색·작화해 연재하고, 하단에 실용적인 법적·소비자 예방 체크리스트를 함께 제공하는 무료 웹툰 연재관입니다.</p>
              <h2>1. 익명 각색 및 비식별 준수 원칙</h2>
              <p>모든 연재 회차는 공감 생활 사례를 기반으로 특정 인물, 기업, 차량 번호, 실제 거주지, 연락처를 완전히 익명화하여 자체 제작합니다. 특정 개인이나 업체를 비방할 목적의 실명 폭로는 게재하지 않습니다.</p>
              <h2>2. 쾌적한 세로 스크롤 독자 뷰어</h2>
              <p>별도 로그인이나 결제 없이 모바일·PC 어디서나 다크/라이트 뷰어를 전환해 빠르게 정주행할 수 있도록 구성되어 있습니다.</p>
              <h2>3. 제휴·광고 투명 표시</h2>
              <p>본 사이트는 무료 연재 유지를 위해 쿠팡 파트너스 위젯·추천 링크 또는 Google 애드센스 광고를 게재할 수 있으며, 제휴 광고 영역에는 관련 법령 및 플랫폼 규정에 따른 안내 문구를 명확히 표기합니다.</p>
            </article>""",
        ),
        "privacy": (
            "개인정보처리방침 | GuideHollow 웹툰",
            "GuideHollow 웹툰 포털의 개인정보 처리 및 쿠키·광고 안내입니다.",
            """
            <article class="guide-article" style="margin-top:1.5rem;">
              <h1>개인정보처리방침 (GuideHollow 웹툰)</h1>
              <p>본 사이트(https://toon.guidehollow.com/)는 별도의 회원가입, 로그인, 결제 기능을 운영하지 않으며 이용자의 이름·전화번호·계좌번호 등 개인식별정보를 직접 수집하거나 서버 데이터베이스에 저장하지 않습니다.</p>
              <h2>1. 열람 전용 서비스 운영</h2>
              <p>독자가 웹툰 뷰어에서 사용하는 다크/라이트 화면 전환 및 별점 반응은 브라우저 현재 화면에서만 동작하며 개인 계정과 연동되지 않습니다.</p>
              <h2>2. 웹 로그 분석 및 광고 쿠키</h2>
              <p>서비스 이용 통계 분석을 위해 Google Analytics(GA4)가 익명 방문 통계 쿠키를 사용할 수 있으며, 향후 Google AdSense 또는 제3자 제휴 배너(쿠팡 파트너스)가 브라우저 쿠키를 사용할 수 있습니다. 이용자는 브라우저 설정 또는 Google 광고 설정(https://adssettings.google.com)에서 맞춤형 광고 쿠키 사용을 언제든 거부할 수 있습니다.</p>
              <h2>3. 문의처</h2>
              <p>개인정보 및 콘텐츠 검토 요청은 <a href="/contact/">문의하기</a> 페이지에 안내된 공식 이메일로 접수할 수 있습니다.</p>
            </article>""",
        ),
        "terms": (
            "이용약관 | GuideHollow 웹툰",
            "GuideHollow 웹툰 포털 이용약관입니다.",
            """
            <article class="guide-article" style="margin-top:1.5rem;">
              <h1>이용약관 (GuideHollow 웹툰)</h1>
              <p>본 약관은 GuideHollow 웹툰(https://toon.guidehollow.com/)이 제공하는 오리지널 썰툰 열람 서비스의 이용 조건을 규정합니다.</p>
              <h2>1. 정보성 안내의 한계</h2>
              <p>각 회차 하단에 수록된 노동법·임대차·소비자분쟁 관련 해설은 일반 독자의 이해를 돕기 위한 정보성 참고 자료이며, 개별 사건에 대한 정식 법률 자문을 대체하지 않습니다. 구체적인 소송·행정 절차가 필요한 경우 대한법률구조공단(132), 고용노동부(1350), 한국소비자원(1372) 등 공식 기관의 안내를 확인하시기 바랍니다.</p>
              <h2>2. 연재 콘텐츠 저작권</h2>
              <p>본 사이트에 게재된 모든 웹툰 컷 일러스트 및 각색 스토리의 편집 저작권은 GuideHollow에 있으며, 무단 도용·상업적 재배포를 금지합니다.</p>
            </article>""",
        ),
        "contact": (
            "문의하기 | GuideHollow 웹툰",
            "GuideHollow 웹툰 포털 운영팀 문의 및 정정 요청 안내입니다.",
            """
            <article class="guide-article" style="margin-top:1.5rem;">
              <h1>문의하기 · 제보 및 정정 요청</h1>
              <p>GuideHollow 웹툰 포털 콘텐츠 오류 제보, 저작권 검토 요청, 서비스 개선 제안은 아래 공식 연락처로 보내주시기 바랍니다.</p>
              <ul>
                <li><strong>공식 이메일:</strong> emfls24777@daum.net</li>
                <li><strong>운영 도메인:</strong> https://toon.guidehollow.com/</li>
                <li><strong>관련 허브:</strong> <a href="https://shopping.guidehollow.com/" target="_blank" rel="noopener noreferrer">GuideHollow 쇼핑 기준 포털</a></li>
              </ul>
            </article>""",
        ),
    }
    out = {}
    for slug, (title, desc, body) in pages.items():
        out[slug] = shell_html(title, desc, f"{ORIGIN}/{slug}/", slug if slug == "about" else "", body)
    return out


def build_site(ad_mode: str) -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)

    (DIST / "assets").mkdir(parents=True, exist_ok=True)
    (DIST / "studio").mkdir(parents=True, exist_ok=True)

    (DIST / "assets" / "style.css").write_text(STYLE_CSS.strip() + "\n", encoding="utf-8")
    (DIST / "assets" / "ad-manager.js").write_text(build_ad_manager_js(ad_mode).strip() + "\n", encoding="utf-8")
    (DIST / "assets" / "viewer.js").write_text(VIEWER_JS.strip() + "\n", encoding="utf-8")
    (DIST / "assets" / "episodes.json").write_text(json.dumps(EPISODES, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # Generate 70 full-color webtoon SVG illustrations (10 episode covers + 60 cut panels)
    toons_dir = DIST / "assets" / "toons"
    svg_count = 0
    for idx, ep in enumerate(EPISODES):
        ep_art_dir = toons_dir / ep["id"]
        ep_art_dir.mkdir(parents=True, exist_ok=True)
        (ep_art_dir / "cover.svg").write_text(render_cover_svg(idx, ep), encoding="utf-8")
        svg_count += 1
        for p in ep["panels"]:
            n = p["panelNumber"]
            (ep_art_dir / f"cut-0{n}.svg").write_text(render_panel_svg(idx, ep, p), encoding="utf-8")
            svg_count += 1

    (DIST / "index.html").write_text(build_home_html(), encoding="utf-8")
    (DIST / "studio" / "index.html").write_text(build_binge_archive_html(), encoding="utf-8")

    urls = [f"{ORIGIN}/", f"{ORIGIN}/studio/"]
    for idx, ep in enumerate(EPISODES):
        ep_dir = DIST / "episodes" / ep["id"]
        ep_dir.mkdir(parents=True, exist_ok=True)
        (ep_dir / "index.html").write_text(build_episode_html(idx, ep), encoding="utf-8")
        urls.append(f"{ORIGIN}/episodes/{ep['id']}/")

    for slug, html in build_policy_pages().items():
        p_dir = DIST / slug
        p_dir.mkdir(parents=True, exist_ok=True)
        (p_dir / "index.html").write_text(html, encoding="utf-8")
        urls.append(f"{ORIGIN}/{slug}/")

    sitemap_items = "\n".join(
        f"  <url><loc>{u}</loc><lastmod>2026-11-18</lastmod><changefreq>weekly</changefreq></url>"
        for u in urls
    )
    (DIST / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sitemap_items}\n</urlset>\n',
        encoding="utf-8",
    )
    (DIST / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {ORIGIN}/sitemap.xml\n",
        encoding="utf-8",
    )
    (DIST / "ads.txt").write_text(
        "google.com, pub-8830524482034754, DIRECT, f08c47fec0942fa0\n",
        encoding="utf-8",
    )
    (DIST / "_headers").write_text(
        "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: strict-origin-when-cross-origin\n",
        encoding="utf-8",
    )
    (DIST / "CNAME").write_text("toon.guidehollow.com\n", encoding="utf-8")

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(DIST.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(DIST))

    print(f"BUILT {len(urls)} HTML routes + {svg_count} Webtoon SVGs into {DIST} (ad_mode={ad_mode})")
    print(f"PACKAGED {ZIP_PATH} ({ZIP_PATH.stat().st_size} bytes)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ad-mode", choices=("coupang", "adsense"), default="coupang")
    args = parser.parse_args()
    build_site(args.ad_mode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
