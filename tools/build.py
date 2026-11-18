#!/usr/bin/env python3
"""Static site builder & ZIP packager for GuideHollow 썰툰 포털 (toon.guidehollow.com)."""
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

STYLE_CSS = """
:root {
  --bg: #f8fafc;
  --surface: #ffffff;
  --surface-alt: #f1f5f9;
  --ink: #0f172a;
  --muted: #475569;
  --line: #cbd5e1;
  --accent: #0f766e;
  --accent-soft: #ccfbf1;
  --highlight: #facc15;
  --coupang-red: #e60023;
  --max: 1120px;
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
  line-height: 1.65;
  overflow-wrap: anywhere;
}
a { color: inherit; }
button, input, select, textarea { font: inherit; }
:focus-visible { outline: 3px solid var(--accent); outline-offset: 2px; }
.wrap { width: min(var(--max), calc(100% - 1.5rem)); margin: 0 auto; }

.site-header {
  background: var(--surface);
  border-bottom: 2px solid var(--ink);
  position: sticky;
  top: 0;
  z-index: 40;
}
.header-inner {
  min-height: 62px;
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
  gap: 0.4rem;
  font-weight: 900;
  font-size: 1.15rem;
  text-decoration: none;
  letter-spacing: -0.02em;
}
.brand-badge {
  background: var(--ink);
  color: #fff;
  padding: 0.14rem 0.5rem;
  border-radius: 6px;
  font-size: 0.78rem;
}
.nav { display: flex; gap: 0.45rem; flex-wrap: wrap; }
.nav a {
  text-decoration: none;
  padding: 0.36rem 0.72rem;
  border-radius: 999px;
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--muted);
  border: 1px solid transparent;
}
.nav a:hover, .nav a.active {
  background: var(--ink);
  color: #fff;
}

.hero {
  background: linear-gradient(135deg, #0f172a 0%, #134e4a 100%);
  color: #fff;
  border-radius: 18px;
  padding: 1.85rem 1.5rem;
  margin: 1.1rem 0;
  border: 2px solid var(--ink);
}
.hero-kicker {
  display: inline-block;
  background: var(--highlight);
  color: var(--ink);
  font-weight: 900;
  font-size: 0.76rem;
  padding: 0.2rem 0.65rem;
  border-radius: 999px;
}
.hero h1 {
  margin: 0.75rem 0 0.55rem;
  font-size: clamp(1.5rem, 3.8vw, 2.35rem);
  line-height: 1.24;
  letter-spacing: -0.02em;
}
.hero p { margin: 0; color: #e2e8f0; max-width: 48rem; font-size: 0.96rem; }
.hero-actions { display: flex; flex-wrap: wrap; gap: 0.65rem; margin-top: 1.1rem; }

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.7rem 1.05rem;
  border-radius: 10px;
  border: 2px solid var(--ink);
  background: var(--surface);
  color: var(--ink);
  font-weight: 800;
  font-size: 0.9rem;
  cursor: pointer;
  text-decoration: none;
}
.btn-primary { background: var(--highlight); color: var(--ink); }
.btn-teal { background: var(--accent); color: #fff; border-color: var(--accent); }
.btn-coupang { background: var(--coupang-red); color: #fff; border-color: #b91c1c; }

.ad-box {
  margin: 1.5rem 0;
  padding: 0.9rem;
  background: var(--surface);
  border: 1.5px solid var(--line);
  border-radius: 14px;
}
.ad-disclosure {
  font-size: 0.76rem;
  color: var(--muted);
  margin: 0 0 0.5rem;
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
.coupang-search-wrap iframe, .coupang-carousel-slot iframe {
  max-width: 100%;
  border: 0;
}
.carousel-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.9rem;
}
@media (max-width: 980px) {
  .carousel-grid { grid-template-columns: 1fr; }
}
.coupang-banner-card {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.85rem;
  padding: 1rem 1.1rem;
  border-radius: 12px;
  background: linear-gradient(135deg, #fff7ed 0%, #fef2f2 100%);
  border: 2px solid #fdba74;
}
.coupang-banner-card strong { display: block; font-size: 1rem; color: #9a3412; margin-bottom: 0.2rem; }
.coupang-banner-card span { display: block; font-size: 0.86rem; color: #475569; }
.coupang-card-actions { display: flex; flex-wrap: wrap; gap: 0.5rem; }

.genre-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin: 1.1rem 0;
}
.genre-pill {
  padding: 0.44rem 0.82rem;
  border-radius: 999px;
  border: 1.5px solid var(--line);
  background: var(--surface);
  color: var(--ink);
  font-size: 0.84rem;
  font-weight: 700;
  cursor: pointer;
}
.genre-pill.is-active {
  background: var(--ink);
  color: #fff;
  border-color: var(--ink);
}

.episode-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  margin-bottom: 1.6rem;
}
@media (max-width: 760px) {
  .episode-grid { grid-template-columns: 1fr; }
}
.ep-card {
  background: var(--surface);
  border: 2px solid var(--ink);
  border-radius: 14px;
  padding: 1.05rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 0.7rem;
  box-shadow: 0 4px 0 #0f172a;
}
.ep-meta { display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; font-size: 0.8rem; font-weight: 800; color: var(--accent); }
.ep-card h2, .ep-card h3 { margin: 0.2rem 0; font-size: 1.08rem; line-height: 1.38; }
.ep-hook {
  background: #fef9c3;
  border-left: 4px solid #ca8a04;
  padding: 0.42rem 0.6rem;
  border-radius: 4px;
  font-size: 0.84rem;
  font-weight: 700;
}
.ep-summary { margin: 0; font-size: 0.88rem; color: var(--muted); }
.ep-links { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.35rem; }

.comic-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
  margin: 1.2rem 0;
}
@media (max-width: 700px) {
  .comic-grid { grid-template-columns: 1fr; }
}
.panel-card {
  background: #fff;
  border: 2.5px solid var(--ink);
  border-radius: 14px;
  padding: 0.9rem;
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
  box-shadow: 0 4px 0 var(--ink);
}
.panel-top { display: flex; justify-content: space-between; align-items: center; gap: 0.4rem; }
.panel-stage { background: var(--ink); color: #fff; font-size: 0.76rem; font-weight: 800; padding: 0.2rem 0.55rem; border-radius: 999px; }
.panel-sfx { background: #fef08a; color: #b91c1c; border: 1.5px solid #d97706; font-size: 0.76rem; font-weight: 900; padding: 0.14rem 0.45rem; border-radius: 6px; }
.panel-narr { background: var(--surface-alt); border-left: 4px solid var(--accent); padding: 0.45rem 0.65rem; font-size: 0.85rem; font-weight: 700; border-radius: 4px; }
.panel-dialog { background: #fffbeb; border: 2px solid var(--ink); border-radius: 12px; padding: 0.65rem 0.75rem; font-size: 0.92rem; }
.panel-speaker { display: block; font-size: 0.76rem; font-weight: 800; color: var(--accent); margin-bottom: 0.18rem; }

.guide-article {
  background: var(--surface);
  border: 1.5px solid var(--line);
  border-radius: 14px;
  padding: 1.3rem;
  margin: 1.4rem 0;
}
.guide-article h2 { margin-top: 0; font-size: 1.25rem; color: var(--ink); }
.guide-article ul { padding-left: 1.2rem; }
.guide-article li { margin-bottom: 0.4rem; }

/* Studio Workspace */
.studio-grid { display: grid; grid-template-columns: minmax(0, 1.03fr) minmax(0, 0.97fr); gap: 1.15rem; align-items: start; }
@media (max-width: 920px) { .studio-grid { grid-template-columns: 1fr; } }
.box { background: var(--surface); border: 2px solid var(--ink); border-radius: 14px; padding: 1.05rem; min-width: 0; }
.preset-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0.45rem; margin-bottom: 0.9rem; }
.preset-btn { padding: 0.55rem 0.65rem; border-radius: 9px; border: 1.5px solid var(--line); background: var(--surface-alt); text-align: left; font-size: 0.82rem; font-weight: 700; cursor: pointer; }
.preset-btn.is-selected { border-color: var(--accent); background: var(--accent-soft); }
.fgrid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.65rem; margin-bottom: 0.8rem; }
@media (max-width: 560px) { .fgrid { grid-template-columns: 1fr; } }
.field { display: flex; flex-direction: column; gap: 0.25rem; min-width: 0; }
.field.full { grid-column: 1 / -1; }
.field label { font-size: 0.8rem; font-weight: 800; color: var(--accent); }
.field input, .field select, .field textarea { width: 100%; max-width: 100%; padding: 0.55rem 0.65rem; border-radius: 8px; border: 1.5px solid var(--line); background: #fff; color: var(--ink); font-size: 0.9rem; }
.field textarea { min-height: 60px; resize: vertical; }
.ptabs { display: flex; flex-wrap: wrap; gap: 0.35rem; margin-bottom: 0.8rem; }
.ptab { padding: 0.36rem 0.68rem; border-radius: 8px; border: 1.5px solid var(--line); background: var(--surface-alt); font-size: 0.8rem; font-weight: 700; cursor: pointer; }
.ptab.is-active { background: var(--ink); color: #fff; border-color: var(--ink); }
.aspect-row { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 0.75rem; }
.abtn { flex: 1 1 115px; padding: 0.48rem 0.55rem; border-radius: 8px; border: 1.5px solid var(--line); background: var(--surface-alt); font-size: 0.78rem; font-weight: 800; cursor: pointer; }
.abtn.is-active { background: var(--ink); color: #fff; border-color: var(--ink); }
.canvas-wrap { background: #0f172a; border-radius: 12px; padding: 0.65rem; text-align: center; overflow: hidden; }
#ssultoonCanvas { display: block; max-width: 100%; height: auto; margin: 0 auto; border-radius: 8px; background: #fff; }
.shorts-pager { display: none; justify-content: center; align-items: center; gap: 0.5rem; margin-top: 0.6rem; color: #fff; }
.shorts-pager.is-visible { display: flex; }
.toast { min-height: 1.35rem; margin-top: 0.55rem; font-size: 0.84rem; font-weight: 700; color: var(--accent); }

.site-footer {
  margin-top: 2.2rem;
  border-top: 2px solid var(--ink);
  background: var(--surface);
  padding: 1.5rem 0 2.2rem;
  font-size: 0.85rem;
  color: var(--muted);
}
.footer-row { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 0.8rem; }
.footer-nav { display: flex; flex-wrap: wrap; gap: 0.85rem; }
.footer-nav a { text-decoration: none; font-weight: 700; }
"""


def build_ad_manager_js(ad_mode: str) -> str:
    return f"""// Dual-Mode Ad Manager for GuideHollow 썰툰 (toon.guidehollow.com)
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
      const reason = container.dataset.reason || "썰툰 주제와 관련된 실용 상품을 바로 비교해 보세요.";
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


STUDIO_JS = """(function () {
  const SCENE_PALETTES = {
    "오피스": { bgTop: "#e2e8f0", bgBot: "#cbd5e1", accent: "#0f766e", shirt: "#1e3a8a", hair: "#1e293b", skin: "#fde6d8" },
    "톡방·메신저": { bgTop: "#fef08a", bgBot: "#fde047", accent: "#0369a1", shirt: "#0f766e", hair: "#0f172a", skin: "#fee5d6" },
    "주차장·도로": { bgTop: "#1e293b", bgBot: "#334155", accent: "#f59e0b", shirt: "#475569", hair: "#0f172a", skin: "#fbd9c7" },
    "예식장·카페": { bgTop: "#fce7f3", bgBot: "#fbcfe8", accent: "#be185d", shirt: "#9d174d", hair: "#312e81", skin: "#fdece2" },
    "미스터리야간": { bgTop: "#0f172a", bgBot: "#1e1b4b", accent: "#c084fc", shirt: "#312e81", hair: "#020617", skin: "#e2e8f0" },
    "법원·계약서": { bgTop: "#ecfeff", bgBot: "#cffafe", accent: "#0e7490", shirt: "#111827", hair: "#1f2937", skin: "#fde5d7" }
  };

  let episodes = [];
  const state = {
    activeIdx: 0,
    aspect: "grid4",
    shortsIdx: 0,
    title: "퇴근 5분 전 주말 출근 강요한 팀장님, 노동청 진정서 한 장에 태세 전환한 썰",
    watermark: "toon.guidehollow.com",
    showAiLabel: true,
    hashtags: ["#썰툰", "#사이다썰", "#GuideHollow썰툰"],
    panels: []
  };

  const els = {};
  function q(id) { return document.getElementById(id); }
  function toast(msg) { if (els.toast) els.toast.textContent = msg; }
  function esc(v) {
    return String(v || "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  function wrapLines(ctx, text, maxW, maxLines) {
    const words = String(text || "").split(/\\s+/);
    const lines = [];
    let cur = "";
    for (const w of words) {
      const cand = cur ? cur + " " + w : w;
      if (ctx.measureText(cand).width <= maxW) {
        cur = cand;
      } else {
        if (cur) lines.push(cur);
        if (ctx.measureText(w).width > maxW) {
          let chunk = "";
          for (const ch of w) {
            if (ctx.measureText(chunk + ch).width > maxW && chunk) {
              lines.push(chunk);
              chunk = ch;
            } else {
              chunk += ch;
            }
          }
          cur = chunk;
        } else {
          cur = w;
        }
      }
    }
    if (cur) lines.push(cur);
    if (maxLines && lines.length > maxLines) {
      const cut = lines.slice(0, maxLines);
      cut[maxLines - 1] = cut[maxLines - 1].slice(0, Math.max(2, cut[maxLines - 1].length - 1)) + "…";
      return cut;
    }
    return lines;
  }

  function rrect(ctx, x, y, w, h, r) {
    const rad = Math.min(r, w / 2, h / 2);
    ctx.beginPath();
    ctx.moveTo(x + rad, y);
    ctx.arcTo(x + w, y, x + w, y + h, rad);
    ctx.arcTo(x + w, y + h, x, y + h, rad);
    ctx.arcTo(x, y + h, x, y, rad);
    ctx.arcTo(x, y, x + w, y, rad);
    ctx.closePath();
  }

  function drawChar(ctx, cx, cy, scale, expr, pal) {
    ctx.save();
    ctx.translate(cx, cy);
    ctx.scale(scale, scale);
    ctx.fillStyle = pal.shirt;
    rrect(ctx, -46, 28, 92, 62, 24);
    ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = "#0f172a"; ctx.stroke();
    ctx.fillStyle = pal.skin; ctx.fillRect(-10, 14, 20, 18);
    ctx.fillStyle = pal.hair; ctx.beginPath(); ctx.arc(0, -14, 34, Math.PI * 0.9, Math.PI * 2.1); ctx.fill();
    ctx.fillStyle = pal.skin; ctx.beginPath(); ctx.ellipse(0, -8, 29, 32, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
    ctx.fillStyle = pal.hair;
    ctx.beginPath();
    ctx.moveTo(-30, -16); ctx.quadraticCurveTo(-10, -44, 0, -40); ctx.quadraticCurveTo(18, -44, 30, -16);
    ctx.quadraticCurveTo(14, -28, 0, -20); ctx.quadraticCurveTo(-14, -28, -30, -16); ctx.fill();
    ctx.strokeStyle = "#0f172a"; ctx.fillStyle = "#0f172a"; ctx.lineWidth = 2.8;
    if (expr === "사이다미소") {
      ctx.beginPath(); ctx.arc(-11, -9, 5, Math.PI, 0); ctx.stroke();
      ctx.beginPath(); ctx.arc(11, -9, 5, Math.PI, 0); ctx.stroke();
      ctx.beginPath(); ctx.arc(0, 3, 9, 0.1 * Math.PI, 0.9 * Math.PI); ctx.stroke();
    } else if (expr === "분노") {
      ctx.beginPath(); ctx.moveTo(-18, -20); ctx.lineTo(-5, -14); ctx.moveTo(18, -20); ctx.lineTo(5, -14); ctx.stroke();
      ctx.beginPath(); ctx.arc(-11, -10, 3.2, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(11, -10, 3.2, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.ellipse(0, 8, 9, 6, 0, 0, Math.PI * 2); ctx.stroke();
    } else if (expr === "각성") {
      ctx.fillStyle = "#fff"; ctx.fillRect(-19, -15, 15, 9); ctx.fillRect(4, -15, 15, 9);
      ctx.strokeRect(-19, -15, 15, 9); ctx.strokeRect(4, -15, 15, 9);
      ctx.beginPath(); ctx.moveTo(-7, 7); ctx.quadraticCurveTo(3, 12, 11, 4); ctx.stroke();
    } else {
      ctx.beginPath(); ctx.arc(-11, -10, 3.2, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(11, -10, 3.2, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.moveTo(-8, 7); ctx.lineTo(8, 7); ctx.stroke();
    }
    ctx.restore();
  }

  function drawPanel(ctx, x, y, w, h, p, sc) {
    const pal = SCENE_PALETTES[p.scene] || SCENE_PALETTES["오피스"];
    ctx.save();
    rrect(ctx, x, y, w, h, 14);
    const g = ctx.createLinearGradient(x, y, x, y + h);
    g.addColorStop(0, pal.bgTop); g.addColorStop(1, pal.bgBot);
    ctx.fillStyle = g; ctx.fill();
    ctx.lineWidth = 4; ctx.strokeStyle = "#0f172a"; ctx.stroke(); ctx.clip();

    const narH = Math.round(52 * sc);
    ctx.fillStyle = "#0f172a"; ctx.fillRect(x, y, w, narH);
    ctx.fillStyle = "#64d8d0"; ctx.font = "800 " + Math.round(13 * sc) + 'px "Noto Sans KR",sans-serif';
    ctx.textBaseline = "middle";
    ctx.fillText("#" + p.panelNumber + " " + (p.stage || ""), x + 12 * sc, y + 17 * sc);
    ctx.fillStyle = "#fff"; ctx.font = "700 " + Math.round(13.5 * sc) + 'px "Noto Sans KR",sans-serif';
    const nLines = wrapLines(ctx, p.narration, w - 24 * sc, 1);
    ctx.fillText(nLines[0] || "", x + 12 * sc, y + 38 * sc);

    if (p.sfx) {
      ctx.save(); ctx.translate(x + w - 48 * sc, y + narH + 28 * sc); ctx.rotate(-0.1);
      ctx.fillStyle = "#fef08a"; ctx.strokeStyle = "#b45309"; ctx.lineWidth = 2.4;
      rrect(ctx, -38 * sc, -14 * sc, 76 * sc, 28 * sc, 7); ctx.fill(); ctx.stroke();
      ctx.fillStyle = "#b91c1c"; ctx.font = "900 " + Math.round(14 * sc) + 'px "Noto Sans KR",sans-serif';
      ctx.textAlign = "center"; ctx.fillText(p.sfx, 0, 1); ctx.restore();
    }

    drawChar(ctx, x + w * 0.24, y + h * 0.72, sc * 0.96, p.expression, pal);
    const bx = x + w * 0.37, bw = w * 0.59, by = y + narH + 38 * sc, bh = h - (by - y) - 18 * sc;
    ctx.fillStyle = p.bubbleType === "외침(사이다)" ? "#fffbeb" : "#fff";
    ctx.strokeStyle = p.bubbleType === "외침(사이다)" ? "#b91c1c" : "#0f172a";
    ctx.lineWidth = 3; rrect(ctx, bx, by, bw, bh, 16); ctx.fill(); ctx.stroke();

    ctx.fillStyle = pal.accent; ctx.font = "800 " + Math.round(13 * sc) + 'px "Noto Sans KR",sans-serif';
    ctx.textBaseline = "top"; ctx.fillText(p.speaker || "화자", bx + 14 * sc, by + 11 * sc);
    ctx.fillStyle = "#0f172a"; ctx.font = "700 " + Math.round(16 * sc) + 'px "Noto Sans KR",sans-serif';
    wrapLines(ctx, p.dialogue, bw - 26 * sc, 5).forEach((ln, idx) => {
      ctx.fillText(ln, bx + 14 * sc, by + (33 + idx * 23) * sc);
    });
    ctx.restore();
  }

  function renderCanvas() {
    if (!els.canvas || !state.panels.length) return;
    const ctx = els.canvas.getContext("2d");
    const panels = state.panels;
    if (state.aspect === "grid4") {
      els.canvas.width = 1080; els.canvas.height = 1080;
      els.pager.classList.remove("is-visible");
      ctx.fillStyle = "#f8fafc"; ctx.fillRect(0, 0, 1080, 1080);
      ctx.fillStyle = "#0f172a"; ctx.fillRect(0, 0, 1080, 118);
      ctx.fillStyle = "#64d8d0"; ctx.font = '800 20px "Noto Sans KR",sans-serif'; ctx.textBaseline = "top";
      ctx.fillText("GuideHollow 4컷 썰툰 · " + state.watermark, 34, 18);
      ctx.fillStyle = "#fff"; ctx.font = '800 28px "Noto Sans KR",sans-serif';
      wrapLines(ctx, state.title, 1010, 2).forEach((ln, i) => ctx.fillText(ln, 34, 48 + i * 32));
      const idx4 = panels.length >= 6 ? [0, 1, 3, 5] : [0, 1, 2, 3];
      const pos = [[28, 136], [550, 136], [28, 586], [550, 586]];
      idx4.forEach((pIdx, s) => { if (panels[pIdx]) drawPanel(ctx, pos[s][0], pos[s][1], 502, 430, panels[pIdx], 1.12); });
      if (state.showAiLabel) {
        ctx.fillStyle = "#334155"; ctx.font = '600 17px "Noto Sans KR",sans-serif';
        ctx.fillText("AI 연출·브라우저 제작(toon.guidehollow.com)", 28, 1040);
      }
    } else if (state.aspect === "webtoon6") {
      els.canvas.width = 800; els.canvas.height = 2400;
      els.pager.classList.remove("is-visible");
      ctx.fillStyle = "#f8fafc"; ctx.fillRect(0, 0, 800, 2400);
      ctx.fillStyle = "#0f172a"; ctx.fillRect(0, 0, 800, 150);
      ctx.fillStyle = "#64d8d0"; ctx.font = '800 20px "Noto Sans KR",sans-serif'; ctx.textBaseline = "top";
      ctx.fillText("6컷 세로 웹툰 · " + state.watermark, 28, 20);
      ctx.fillStyle = "#fff"; ctx.font = '800 28px "Noto Sans KR",sans-serif';
      wrapLines(ctx, state.title, 744, 2).forEach((ln, i) => ctx.fillText(ln, 28, 54 + i * 36));
      panels.slice(0, 6).forEach((p, idx) => drawPanel(ctx, 28, 174 + idx * 360, 744, 340, p, 1.05));
      if (state.showAiLabel) {
        ctx.fillStyle = "#334155"; ctx.font = '600 18px "Noto Sans KR",sans-serif';
        ctx.fillText("AI 연출·브라우저 제작(toon.guidehollow.com)", 28, 2354);
      }
    } else {
      els.canvas.width = 1080; els.canvas.height = 1920;
      els.pager.classList.add("is-visible");
      const s = Math.max(0, Math.min(state.shortsIdx, panels.length - 1));
      els.counter.textContent = (s + 1) + " / " + panels.length + " 컷";
      ctx.fillStyle = "#0f172a"; ctx.fillRect(0, 0, 1080, 1920);
      ctx.fillStyle = "#facc15"; rrect(ctx, 48, 120, 984, 210, 24); ctx.fill();
      ctx.fillStyle = "#0f172a"; ctx.font = '900 38px "Noto Sans KR",sans-serif'; ctx.textBaseline = "top";
      wrapLines(ctx, state.title, 920, 3).forEach((ln, i) => ctx.fillText(ln, 80, 150 + i * 54));
      drawPanel(ctx, 48, 370, 984, 1180, panels[s], 1.9);
      ctx.fillStyle = "#64d8d0"; ctx.font = '800 30px "Noto Sans KR",sans-serif';
      ctx.fillText(state.watermark + " · " + (s + 1) + "/" + panels.length + "컷", 60, 1610);
      if (state.showAiLabel) {
        ctx.fillStyle = "#cbd5e1"; ctx.font = '600 24px "Noto Sans KR",sans-serif';
        ctx.fillText("AI 연출·브라우저 제작(toon.guidehollow.com)", 60, 1665);
      }
    }
  }

  function syncInputs() {
    const p = state.panels[state.activeIdx] || state.panels[0];
    if (!p) return;
    els.epTitle.value = state.title;
    els.watermark.value = state.watermark;
    els.aiCheck.checked = state.showAiLabel;
    els.pStage.value = p.stage || "";
    els.pSpeaker.value = p.speaker || "";
    els.pScene.value = p.scene || "오피스";
    els.pExpr.value = p.expression || "사이다미소";
    els.pBubble.value = p.bubbleType || "일반";
    els.pSfx.value = p.sfx || "두둥!";
    els.pNarr.value = p.narration || "";
    els.pDial.value = p.dialogue || "";
    els.ptabs.innerHTML = state.panels.map((item, idx) =>
      '<button type="button" class="ptab ' + (idx === state.activeIdx ? 'is-active' : '') + '" data-idx="' + idx + '">' + (idx + 1) + '컷</button>'
    ).join("");
    els.ptabs.querySelectorAll(".ptab").forEach((b) => {
      b.addEventListener("click", () => {
        state.activeIdx = Number(b.dataset.idx);
        state.shortsIdx = state.activeIdx;
        syncInputs();
        renderCanvas();
      });
    });
  }

  function loadEp(ep) {
    state.title = ep.title;
    state.panels = JSON.parse(JSON.stringify(ep.panels));
    state.hashtags = ep.hashtags ? [...ep.hashtags] : ["#썰툰", "#GuideHollow"];
    state.activeIdx = 0;
    state.shortsIdx = 0;
    document.querySelectorAll(".preset-btn").forEach((b) => b.classList.toggle("is-selected", b.dataset.ep === ep.id));
    syncInputs();
    renderCanvas();
  }

  function buildFromIdea(ideaRaw) {
    const idea = (ideaRaw || "").trim();
    if (!idea) { toast("한 줄 사연을 먼저 입력해 주세요!"); return; }
    const sIdea = idea.length > 42 ? idea.slice(0, 42) + "…" : idea;
    state.title = sIdea + " — 증거 하나로 통쾌하게 역전한 썰";
    state.panels = [
      { panelNumber: 1, stage: "기(3초 훅)", scene: "오피스", expression: "사이다미소", bubbleType: "외침(사이다)", sfx: "두둥!", speaker: "주인공(나)", narration: "3초 훅 · " + sIdea, dialogue: "마지막 증거 한 장에 상대 태도가 180도 바뀌었습니다." },
      { panelNumber: 2, stage: "승(고구마)", scene: "톡방·메신저", expression: "억울", bubbleType: "일반", sfx: "실화냐?!", speaker: "상대방", narration: "발단 · 처음엔 웃어넘기려던 선 넘은 행동.", dialogue: "증거도 없으면서 괜히 예민하게 구시네 ㅋㅋ" },
      { panelNumber: 3, stage: "승(고구마 심화)", scene: "오피스", expression: "분노", bubbleType: "속마음", sfx: "삐빅-", speaker: "주인공(나)", narration: "감정 싸움 대신 기록을 남기기로 결심한 순간.", dialogue: "'말로 해선 안 통한다. 시간대별 영수증과 대화 원본을 다 모은다.'" },
      { panelNumber: 4, stage: "전(결정적 증거)", scene: "법원·계약서", expression: "각성", bubbleType: "나레이션박스", sfx: "두둥!", speaker: "증거 정리", narration: "반전의 시작 · CCTV·원본 영수증·접수번호 완비.", dialogue: "날짜, 시간, 금액 오차 없이 공식 자료 정리 완료!" },
      { panelNumber: 5, stage: "전(반격)", scene: "오피스", expression: "당황", bubbleType: "외침(사이다)", sfx: "참교육!", speaker: "상대방", narration: "공식 증거를 보여주자 순식간에 바뀐 목소리.", dialogue: "어?! 그걸 다 저장해 뒀어요?? 좋게 해결해요 제발!!" },
      { panelNumber: 6, stage: "결(사이다)", scene: "오피스", expression: "사이다미소", bubbleType: "외침(사이다)", sfx: "사이다!", speaker: "주인공(나)", narration: "완벽한 마무리 · 손해 0원 & 깔끔한 정산 완료.", dialogue: "억울할 땐 화내기보다 '기록 남기기'가 제일 강합니다!" }
    ];
    state.activeIdx = 0; state.shortsIdx = 0;
    syncInputs(); renderCanvas();
    toast("입력한 사연으로 6컷 대본과 이미지를 생성했습니다!");
  }

  async function init() {
    els.canvas = q("ssultoonCanvas");
    els.pager = q("shortsPager");
    els.counter = q("slideCounter");
    els.toast = q("statusToast");
    els.epTitle = q("episodeTitleInput");
    els.watermark = q("watermarkInput");
    els.aiCheck = q("aiLabelCheck");
    els.ptabs = q("panelTabs");
    els.pStage = q("panelStage");
    els.pSpeaker = q("panelSpeaker");
    els.pScene = q("panelScene");
    els.pExpr = q("panelExpression");
    els.pBubble = q("panelBubble");
    els.pSfx = q("panelSfx");
    els.pNarr = q("panelNarration");
    els.pDial = q("panelDialogue");

    const strip = q("presetStrip");
    try {
      const r = await fetch("/assets/episodes.json");
      if (r.ok) episodes = await r.json();
    } catch (e) {}
    if (!episodes.length && window.__FALLBACK_EPISODES__) episodes = window.__FALLBACK_EPISODES__;

    if (strip && episodes.length) {
      strip.innerHTML = episodes.slice(0, 6).map((ep) =>
        '<button type="button" class="preset-btn" data-ep="' + esc(ep.id) + '">' + esc(ep.emoji) + " " + esc(ep.genre) + "</button>"
      ).join("");
      strip.querySelectorAll(".preset-btn").forEach((b) => {
        b.addEventListener("click", () => {
          const found = episodes.find((x) => x.id === b.dataset.ep);
          if (found) loadEp(found);
        });
      });
    }

    const reqEp = new URLSearchParams(window.location.search).get("ep");
    const first = episodes.find((x) => x.id === reqEp) || episodes[0];
    if (first) loadEp(first);

    q("autoBuildBtn").addEventListener("click", () => buildFromIdea(q("storyIdeaInput").value));
    els.epTitle.addEventListener("input", () => { state.title = els.epTitle.value; renderCanvas(); });
    els.watermark.addEventListener("input", () => { state.watermark = els.watermark.value; renderCanvas(); });
    els.aiCheck.addEventListener("change", () => { state.showAiLabel = els.aiCheck.checked; renderCanvas(); });

    const upd = () => {
      const p = state.panels[state.activeIdx];
      if (!p) return;
      p.stage = els.pStage.value; p.speaker = els.pSpeaker.value;
      p.scene = els.pScene.value; p.expression = els.pExpr.value;
      p.bubbleType = els.pBubble.value; p.sfx = els.pSfx.value;
      p.narration = els.pNarr.value; p.dialogue = els.pDial.value;
      syncInputs(); renderCanvas();
    };
    [els.pStage, els.pSpeaker, els.pScene, els.pExpr, els.pBubble, els.pSfx, els.pNarr, els.pDial].forEach((n) => {
      n.addEventListener("input", upd); n.addEventListener("change", upd);
    });

    document.querySelectorAll(".abtn").forEach((b) => {
      b.addEventListener("click", () => {
        state.aspect = b.dataset.aspect;
        document.querySelectorAll(".abtn").forEach((x) => x.classList.toggle("is-active", x === b));
        renderCanvas();
      });
    });

    q("prevSlideBtn").addEventListener("click", () => {
      state.shortsIdx = (state.shortsIdx - 1 + state.panels.length) % state.panels.length;
      state.activeIdx = state.shortsIdx;
      syncInputs(); renderCanvas();
    });
    q("nextSlideBtn").addEventListener("click", () => {
      state.shortsIdx = (state.shortsIdx + 1) % state.panels.length;
      state.activeIdx = state.shortsIdx;
      syncInputs(); renderCanvas();
    });

    q("downloadPngBtn").addEventListener("click", () => {
      renderCanvas();
      const a = document.createElement("a");
      a.download = "guidehollow-ssultoon-" + state.aspect + ".png";
      a.href = els.canvas.toDataURL("image/png");
      a.click();
      toast("고화질 PNG 썰툰 이미지를 기기에 저장했습니다.");
    });

    q("copyScriptBtn").addEventListener("click", () => {
      const txt = [state.title, "", ...state.panels.map((p) => `[${p.panelNumber}컷] ${p.narration} | ${p.speaker}: ${p.dialogue}`), "", state.hashtags.join(" ")].join("\\n");
      navigator.clipboard?.writeText(txt);
      toast("쇼츠·블로그 대본과 해시태그가 복사되었습니다!");
    });
  }

  document.addEventListener("DOMContentLoaded", init);
})();
"""


def shell_html(title: str, description: str, canonical: str, active_nav: str, body: str, extra_scripts: str = "") -> str:
    nav_items = [
        ("home", "/", "📖 썰툰 연재관"),
        ("studio", "/studio/", "🎨 썰툰 직접 만들기"),
        ("about", "/about/", "소개·기준"),
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
  <meta property="og:site_name" content="GuideHollow 썰툰" />
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
      <a class="brand" href="/"><span>GuideHollow</span><span class="brand-badge">썰툰</span></a>
      <nav class="nav" aria-label="주요 메뉴">{nav_html}</nav>
    </div>
  </header>
  <main class="wrap">
    {body}
  </main>
  <footer class="site-footer">
    <div class="wrap footer-row">
      <div>© 2026 GuideHollow 썰툰 (toon.guidehollow.com) · 공감 스토리툰 &amp; 무료 4컷 스튜디오</div>
      <nav class="footer-nav" aria-label="정책 메뉴">
        <a href="/about/">서비스 소개</a>
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
        ("all", "전체 10편"),
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
    for ep in EPISODES:
        cards.append(
            f"""<article class="ep-card" data-genre="{ep['genreKey']}">
  <div>
    <div class="ep-meta"><span>{ep['emoji']} {escape(ep['genre'])}</span><span>6컷 완결 · 약 {ep['readSeconds']}초</span></div>
    <h2><a href="/episodes/{ep['id']}/" style="text-decoration:none;">{escape(ep['title'])}</a></h2>
    <div class="ep-hook">{escape(ep['hook'])}</div>
    <p class="ep-summary" style="margin-top:0.55rem;">{escape(ep['summary'])}</p>
  </div>
  <div class="ep-links">
    <a class="btn btn-primary" href="/episodes/{ep['id']}/">6컷 바로 보기 →</a>
    <a class="btn" href="/studio/?ep={ep['id']}">🎨 스튜디오 수정</a>
  </div>
</article>"""
        )
    cards_html = "\n".join(cards)
    body = f"""
    <section class="hero">
      <span class="hero-kicker">GUIDEHOLLOW TOON · 무료 썰툰 &amp; 4컷 제작</span>
      <h1>읽으면 속 시원해지는 사이다 썰툰 10선 &amp; 무료 4컷 스튜디오</h1>
      <p>직장·전세 계약·이중주차·중고거래 분쟁까지 실생활에서 그대로 써먹을 수 있는 합법 역전 사이다 썰툰을 감상하고, 한 줄 사연으로 나만의 4컷·쇼츠 웹툰 PNG까지 직접 만들어 보세요.</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="/studio/">🎨 내 사연으로 썰툰 만들기</a>
        <a class="btn" href="#episodes">📖 사이다 썰툰 10편 정주행 ↓</a>
      </div>
    </section>

    <section class="ad-box" data-gh-ad-slot="top" data-ad-kind="search" data-ad-layout="auto" aria-label="스폰서 검색 배너"></section>

    <section id="episodes" aria-label="인기 썰툰 목록">
      <div class="genre-bar" role="group" aria-label="장르 필터">{genre_btns}</div>
      <div class="episode-grid" id="episodeGrid">{cards_html}</div>
    </section>

    <section class="ad-box" data-gh-ad-slot="mid" data-ad-kind="carousels" data-ad-layout="in-article" aria-label="쿠팡 파트너스 인기 상품 배너"></section>

    <article class="guide-article">
      <h2>GuideHollow 썰툰 운영 원칙 · 현실 해결책과 투명한 제작 고지</h2>
      <p>본 사이트의 모든 에피소드는 온라인 공감 사례를 바탕으로 인물·상호·위치 등 특정 가능 정보를 완전히 배제한 채 재구성한 각색 썰툰이며, 각 편 하단에는 감정적 복수가 아닌 <strong>법적·공적 해결 절차와 실제 비용 손실을 줄이는 생활 체크리스트</strong>를 함께 제공합니다.</p>
      <p>또한 무료 <a href="/studio/" style="color:var(--accent);font-weight:700;">썰툰 제작 스튜디오</a>를 통해 누구나 가입 없이 4컷 정방형·6컷 세로 웹툰·9:16 쇼츠 PNG 이미지를 브라우저 안에서 즉시 제작해 저장할 수 있습니다.</p>
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
        "GuideHollow 썰툰 — 사이다 공감 썰툰 연재관 & 무료 4컷만화 제작 스튜디오",
        "직장·결혼·이중주차·전세 계약·중고거래 사이다 썰툰 10편과 브라우저 무료 4컷·쇼츠 스토리툰 제작 스튜디오입니다.",
        f"{ORIGIN}/",
        "home",
        body,
    )


def build_studio_html() -> str:
    fallback_json = json.dumps(EPISODES[:1], ensure_ascii=False)
    body = f"""
    <section class="hero">
      <span class="hero-kicker">FREE BROWSER CANVAS ENGINE</span>
      <h1>AI 썰툰·4컷만화·9:16 쇼츠 스토리툰 무료 제작 스튜디오</h1>
      <p>인기 썰툰 템플릿을 고르거나 내 사연을 한 줄로 입력하면 기승전결 6컷을 즉시 캔버스에 그려줍니다. 가입·서버 전송 없이 100% 브라우저에서 PNG로 저장됩니다.</p>
    </section>

    <section class="ad-box" data-gh-ad-slot="studio-top" data-ad-kind="search" data-ad-layout="auto" aria-label="스폰서 검색 배너"></section>

    <div class="studio-grid">
      <div class="box">
        <h2 style="margin-top:0;">1단계 · 템플릿 선택 또는 한 줄 사연 자동 생성</h2>
        <div class="preset-grid" id="presetStrip"></div>
        <div class="fgrid">
          <div class="field full">
            <label for="storyIdeaInput">한 줄 썰 사연 입력</label>
            <input id="storyIdeaInput" type="text" placeholder="예: 카페 진상 손님이 영수증 던졌는데 사장님이 CCTV로 해결한 썰" />
          </div>
          <div class="field">
            <label for="episodeTitleInput">웹툰 제목 (어그로·훅)</label>
            <input id="episodeTitleInput" type="text" />
          </div>
          <div class="field">
            <label for="watermarkInput">채널/워터마크</label>
            <input id="watermarkInput" type="text" value="toon.guidehollow.com" />
          </div>
        </div>
        <button type="button" class="btn btn-primary" id="autoBuildBtn" style="width:100%;margin-bottom:1rem;">⚡ 한 줄 사연으로 6컷 대본 자동 생성</button>

        <h3 style="margin:0 0 0.5rem;">2단계 · 컷별 대사·장면·표정 편집</h3>
        <div class="ptabs" id="panelTabs"></div>
        <div class="fgrid">
          <div class="field"><label for="panelStage">서사 구간</label><input id="panelStage" type="text" /></div>
          <div class="field"><label for="panelSpeaker">화자 이름</label><input id="panelSpeaker" type="text" /></div>
          <div class="field"><label for="panelScene">배경 장소</label><select id="panelScene"><option value="오피스">오피스</option><option value="톡방·메신저">톡방·메신저</option><option value="주차장·도로">주차장·도로</option><option value="예식장·카페">예식장·카페</option><option value="미스터리야간">미스터리야간</option><option value="법원·계약서">법원·계약서</option></select></div>
          <div class="field"><label for="panelExpression">표정</label><select id="panelExpression"><option value="사이다미소">사이다미소</option><option value="분노">분노</option><option value="억울">억울</option><option value="당황">당황</option><option value="충격">충격</option><option value="무표정">무표정</option><option value="눈물">눈물</option><option value="각성">각성</option></select></div>
          <div class="field"><label for="panelBubble">말풍선</label><select id="panelBubble"><option value="일반">일반</option><option value="외침(사이다)">외침(사이다)</option><option value="속마음">속마음</option><option value="나레이션박스">나레이션박스</option></select></div>
          <div class="field"><label for="panelSfx">효과음</label><select id="panelSfx"><option value="두둥!">두둥!</option><option value="사이다!">사이다!</option><option value="참교육!">참교육!</option><option value="실화냐?!">실화냐?!</option><option value="삐빅-">삐빅-</option></select></div>
          <div class="field full"><label for="panelNarration">상단 나레이션</label><input id="panelNarration" type="text" /></div>
          <div class="field full"><label for="panelDialogue">말풍선 대사</label><textarea id="panelDialogue"></textarea></div>
        </div>
        <label style="display:flex;align-items:center;gap:0.45rem;font-size:0.84rem;color:var(--muted);cursor:pointer;">
          <input type="checkbox" id="aiLabelCheck" checked />
          <span>하단 'AI 연출·브라우저 제작' 투명 안내 라벨 표시</span>
        </label>
      </div>

      <div class="box">
        <h2 style="margin-top:0;">3단계 · 비율 전환 &amp; 고화질 PNG 저장</h2>
        <div class="aspect-row">
          <button type="button" class="abtn is-active" data-aspect="grid4">4컷 정방형 (1080×1080)</button>
          <button type="button" class="abtn" data-aspect="webtoon6">6컷 웹툰 (800×2400)</button>
          <button type="button" class="abtn" data-aspect="shorts916">9:16 쇼츠 (1080×1920)</button>
        </div>
        <div class="canvas-wrap">
          <canvas id="ssultoonCanvas" width="1080" height="1080" aria-label="썰툰 실시간 캔버스"></canvas>
          <div class="shorts-pager" id="shortsPager">
            <button type="button" class="btn" id="prevSlideBtn">◀ 이전</button>
            <span id="slideCounter">1 / 6</span>
            <button type="button" class="btn" id="nextSlideBtn">다음 ▶</button>
          </div>
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:0.55rem;margin-top:0.85rem;">
          <button type="button" class="btn btn-teal" id="downloadPngBtn" style="flex:1 1 200px;">📥 PNG 이미지 저장</button>
          <button type="button" class="btn" id="copyScriptBtn" style="flex:1 1 180px;">📋 쇼츠 대본 복사</button>
        </div>
        <div class="toast" id="statusToast" role="status" aria-live="polite"></div>
      </div>
    </div>

    <div style="margin-top:2rem;"></div>
    <section class="ad-box" data-gh-ad-slot="studio-bottom" data-ad-kind="carousels" data-ad-layout="auto" aria-label="쿠팡 파트너스 인기 상품 배너"></section>
    <script>window.__FALLBACK_EPISODES__ = {fallback_json};</script>
    """
    return shell_html(
        "무료 AI 썰툰·4컷만화·쇼츠 제작 스튜디오 | GuideHollow 썰툰",
        "한 줄 사연으로 4컷 정방형·6컷 웹툰·9:16 쇼츠 스토리툰 PNG 이미지와 대본을 즉시 만드는 무료 웹 스튜디오입니다.",
        f"{ORIGIN}/studio/",
        "studio",
        body,
        extra_scripts='<script src="/assets/studio.js" defer></script>',
    )


def build_episode_html(idx: int, ep: dict) -> str:
    prev_ep = EPISODES[idx - 1] if idx > 0 else None
    next_ep = EPISODES[idx + 1] if idx + 1 < len(EPISODES) else None
    cp = ep["coupang"]

    panels_html = []
    for p in ep["panels"]:
        panels_html.append(
            f"""<article class="panel-card">
  <div class="panel-top">
    <span class="panel-stage">{p['panelNumber']}컷 · {escape(p['stage'])}</span>
    <span class="panel-sfx">{escape(p['sfx'])}</span>
  </div>
  <div class="panel-narr">{escape(p['narration'])}</div>
  <div class="panel-dialog">
    <span class="panel-speaker">{escape(p['speaker'])} ({escape(p['scene'])} · {escape(p['expression'])})</span>
    <div>{escape(p['dialogue'])}</div>
  </div>
</article>"""
        )

    paragraphs = "".join(f"<p>{escape(para)}</p>" for para in ep["guideBody"])
    checklist_items = "".join(f"<li>{escape(item)}</li>" for item in ep["checklist"])
    nav_btns = []
    if prev_ep:
        nav_btns.append(f'<a class="btn" href="/episodes/{prev_ep["id"]}/">← 이전 편: {escape(prev_ep["genre"])}</a>')
    nav_btns.append(f'<a class="btn btn-primary" href="/studio/?ep={ep["id"]}">🎨 이 에피소드 스튜디오에서 수정하기</a>')
    if next_ep:
        nav_btns.append(f'<a class="btn btn-teal" href="/episodes/{next_ep["id"]}/">다음 편 보기: {escape(next_ep["genre"])} →</a>')

    body = f"""
    <section class="hero">
      <span class="hero-kicker">{ep['emoji']} {escape(ep['genre'])} · 6컷 완결</span>
      <h1>{escape(ep['title'])}</h1>
      <p>{escape(ep['summary'])}</p>
      <div class="hero-actions">
        <a class="btn btn-primary" href="/studio/?ep={ep['id']}">🎨 스튜디오에서 컷 수정·PNG 저장</a>
        <a class="btn" href="/">전체 목록으로</a>
      </div>
    </section>

    <section class="ad-box" data-gh-ad-slot="ep-top" data-ad-kind="search" data-ad-layout="auto" aria-label="스폰서 검색 배너"></section>

    <section aria-label="6컷 썰툰 본문">
      <div class="comic-grid">
        {''.join(panels_html)}
      </div>
      <p style="font-size:0.82rem;color:var(--muted);text-align:center;">※ 본 썰툰은 공감 사례를 바탕으로 특정인·상호 식별 요소를 제거해 재구성한 각색 창작물입니다.</p>
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
        f"{ep['title']} | GuideHollow 썰툰",
        ep["summary"],
        f"{ORIGIN}/episodes/{ep['id']}/",
        "home",
        body,
    )


def build_policy_pages() -> dict[str, str]:
    pages = {
        "about": (
            "서비스 소개 · 편집 원칙 | GuideHollow 썰툰",
            "GuideHollow 썰툰 포털의 콘텐츠 제작 원칙과 4컷 스튜디오 안내입니다.",
            f"""
            <article class="guide-article" style="margin-top:1.5rem;">
              <h1>GuideHollow 썰툰 (toon.guidehollow.com) 소개 및 편집 원칙</h1>
              <p><strong>GuideHollow 썰툰</strong>은 직장·계약·주차·소비자 분쟁 등 일상에서 흔히 겪는 억울한 상황을 기승전결 6컷 스토리툰으로 풀어내고, 각 에피소드 하단에 감정적 대응 대신 실생활에 바로 활용할 수 있는 법적·소비자 해결 체크리스트를 함께 제공하는 독립 생활 스토리 포털입니다.</p>
              <h2>1. 익명 각색 및 비식별 준수 원칙</h2>
              <p>모든 에피소드는 온라인·오프라인 공감 사례를 기반으로 특정 인물, 기업, 차량 번호, 실제 거주지, 연락처를 완전히 익명화하여 창작·각색합니다. 특정 개인이나 업체를 비방할 목적의 실화 폭로는 게재하지 않습니다.</p>
              <h2>2. 브라우저 기반 무료 4컷 스튜디오</h2>
              <p><a href="/studio/">무료 썰툰 스튜디오</a>에서는 사용자가 입력한 대사와 사연을 서버에 저장하지 않고 브라우저 내 HTML5 캔버스로만 렌더링해 PNG 이미지와 쇼츠 대본으로 내려받을 수 있습니다.</p>
              <h2>3. 제휴·광고 투명 표시</h2>
              <p>본 사이트는 운영 유지를 위해 쿠팡 파트너스 위젯·추천 링크 또는 Google 애드센스 광고를 게재할 수 있으며, 제휴 광고 영역에는 관련 법령 및 플랫폼 규정에 따른 안내 문구를 명확히 표기합니다.</p>
            </article>""",
        ),
        "privacy": (
            "개인정보처리방침 | GuideHollow 썰툰",
            "GuideHollow 썰툰 포털의 개인정보 처리 및 쿠키·광고 안내입니다.",
            """
            <article class="guide-article" style="margin-top:1.5rem;">
              <h1>개인정보처리방침 (GuideHollow 썰툰)</h1>
              <p>본 사이트(https://toon.guidehollow.com/)는 별도의 회원가입, 로그인, 결제 기능을 운영하지 않으며 이용자의 이름·전화번호·계좌번호 등 개인식별정보를 직접 수집하거나 서버 데이터베이스에 저장하지 않습니다.</p>
              <h2>1. 썰툰 스튜디오 입력 데이터 처리</h2>
              <p>이용자가 4컷·쇼츠 썰툰 스튜디오에서 입력하는 사연·대사·제목과 생성된 PNG 이미지는 전량 이용자의 기기 브라우저 내부 메모리에서만 처리되며 외부 서버로 전송되지 않습니다.</p>
              <h2>2. 웹 로그 분석 및 광고 쿠키</h2>
              <p>서비스 이용 통계 분석을 위해 Google Analytics(GA4)가 익명 방문 통계 쿠키를 사용할 수 있으며, 향후 Google AdSense 또는 제3자 제휴 배너(쿠팡 파트너스)가 브라우저 쿠키를 사용할 수 있습니다. 이용자는 브라우저 설정 또는 Google 광고 설정(https://adssettings.google.com)에서 맞춤형 광고 쿠키 사용을 언제든 거부할 수 있습니다.</p>
              <h2>3. 문의처</h2>
              <p>개인정보 및 콘텐츠 삭제 요청 관련 문의는 <a href="/contact/">문의하기</a> 페이지에 안내된 공식 이메일로 접수할 수 있습니다.</p>
            </article>""",
        ),
        "terms": (
            "이용약관 | GuideHollow 썰툰",
            "GuideHollow 썰툰 포털 및 4컷 제작 스튜디오 이용약관입니다.",
            """
            <article class="guide-article" style="margin-top:1.5rem;">
              <h1>이용약관 (GuideHollow 썰툰)</h1>
              <p>본 약관은 GuideHollow 썰툰(https://toon.guidehollow.com/)이 제공하는 썰툰 열람 서비스 및 무료 브라우저 제작 스튜디오의 이용 조건을 규정합니다.</p>
              <h2>1. 정보성 안내의 한계</h2>
              <p>각 에피소드 하단에 수록된 노동법·임대차·소비자분쟁 관련 해설은 일반 독자의 이해를 돕기 위한 정보성 참고 자료이며, 개별 사건에 대한 정식 법률 자문을 대체하지 않습니다. 구체적인 소송·행정 절차가 필요한 경우 대한법률구조공단(132), 고용노동부(1350), 한국소비자원(1372) 등 공식 기관의 안내를 확인하시기 바랍니다.</p>
              <h2>2. 스튜디오 생성물 이용 책임</h2>
              <p>이용자가 제작 스튜디오를 통해 생성한 썰툰 이미지는 개인·상업 콘텐츠 제작에 자유롭게 활용할 수 있으나, 실존 인물 명예훼손, 허위사실 유포, 타인의 저작물 도용 등 불법 행위에 사용하는 것은 금지되며 관련 법적 책임은 제작자 본인에게 있습니다.</p>
            </article>""",
        ),
        "contact": (
            "문의하기 | GuideHollow 썰툰",
            "GuideHollow 썰툰 포털 운영팀 문의 및 권리침해 신고 안내입니다.",
            """
            <article class="guide-article" style="margin-top:1.5rem;">
              <h1>문의하기 · 제보 및 정정 요청</h1>
              <p>GuideHollow 썰툰 포털 콘텐츠 오류 제보, 저작권·명예훼손 관련 검토 요청, 서비스 개선 제안은 아래 공식 연락처로 보내주시기 바랍니다.</p>
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
    (DIST / "assets" / "studio.js").write_text(STUDIO_JS.strip() + "\n", encoding="utf-8")
    (DIST / "assets" / "episodes.json").write_text(json.dumps(EPISODES, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    (DIST / "index.html").write_text(build_home_html(), encoding="utf-8")
    (DIST / "studio" / "index.html").write_text(build_studio_html(), encoding="utf-8")

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

    print(f"BUILT {len(urls)} HTML routes into {DIST} (ad_mode={ad_mode})")
    print(f"PACKAGED {ZIP_PATH} ({ZIP_PATH.stat().st_size} bytes)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ad-mode", choices=("coupang", "adsense"), default="coupang")
    args = parser.parse_args()
    build_site(args.ad_mode)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
