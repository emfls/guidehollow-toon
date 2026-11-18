"""Tests for comic.naver.com style static webtoon portal toon.guidehollow.com."""
from __future__ import annotations

from pathlib import Path
import sys
import xml.etree.ElementTree as ET

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.build import (  # noqa: E402
    AI_IMAGE_NOTICE,
    COUPANG_DISCLOSURE,
    DISALLOWED_EDITOR_MARKERS,
    DISALLOWED_FAKE_SERVER_MARKERS,
    DIST,
    EPISODE_CUT_COUNTS,
    build_site,
    prepare_episodes,
)

FORBIDDEN_UX_MARKERS = [
    "확대 포착",
    "#b91c1c",
    "#ef4444",
    "#dc2626",
    "#ff3b30",
    "#fef2f2",
    "01화",
    "02화",
    "18컷",
    "14컷",
    "이전화",
    "다음화",
]


def test_build_portal_matches_comic_naver_and_no_fake_server() -> None:
    stats = build_site(ad_mode="coupang")
    episodes = prepare_episodes()
    expected_cuts = sum(EPISODE_CUT_COUNTS.get(ep["id"], len(ep["panels"])) for ep in episodes)
    assert stats["episodes"] >= 10
    assert stats["cuts"] == expected_cuts
    assert stats["svgs"] == len(episodes) + expected_cuts

    home_html = (DIST / "index.html").read_text(encoding="utf-8")
    studio_html = (DIST / "studio" / "index.html").read_text(encoding="utf-8")
    about_html = (DIST / "about" / "index.html").read_text(encoding="utf-8")
    assert "이달의 신규 웹툰" in home_html
    assert "장르별 전체 웹툰" in home_html
    assert "대표 웹툰 보기" in home_html
    assert "G-QP5Q67GE5B" in home_html
    assert AI_IMAGE_NOTICE in home_html
    assert COUPANG_DISCLOSURE in home_html
    assert home_html.count(COUPANG_DISCLOSURE) == 1
    assert studio_html.count(COUPANG_DISCLOSURE) == 1
    assert "top-coupang-disclosure" in home_html
    assert "top-coupang-disclosure" in studio_html
    assert "wing-ad-left" in home_html
    assert "wing-ad-right" in home_html
    assert "coupang-strip-box" in home_html
    assert "promo-event-banner" in home_html
    assert "https://ads-partners.coupang.com/widgets.html" in home_html
    assert "https://ads-partners.coupang.com/banners/" in home_html
    assert "pick-goldbox.webp" not in home_html
    assert "ad-thumb-img" not in home_html
    assert "pick-goldbox.webp" not in studio_html
    assert "ad-thumb-img" not in studio_html
    for marker in DISALLOWED_EDITOR_MARKERS + DISALLOWED_FAKE_SERVER_MARKERS + FORBIDDEN_UX_MARKERS + ["★", "조회 482만"]:
        assert marker not in home_html
        assert marker not in studio_html
        assert marker not in about_html

    seen_cut_counts = set()
    for ep in episodes:
        eid = ep["id"]
        target_n = EPISODE_CUT_COUNTS.get(eid, len(ep["panels"]))
        assert 12 <= target_n <= 18
        assert len(ep["panels"]) == target_n
        seen_cut_counts.add(target_n)

        cover_webp = DIST / "assets" / "toons" / eid / "cover.webp"
        assert cover_webp.exists()
        with Image.open(cover_webp) as cov_im:
            assert cov_im.size == (720, 930)

        cover_path = DIST / "assets" / "toons" / eid / "cover.svg"
        assert cover_path.exists()
        cover_xml = cover_path.read_text(encoding="utf-8")
        assert 'viewBox="0 0 720 930"' in cover_xml
        assert "data:image/webp;base64," in cover_xml
        for marker in FORBIDDEN_UX_MARKERS:
            assert marker not in cover_xml
        cov_root = ET.fromstring(cover_xml)
        cov_desc = "".join(el.text or "" for el in cov_root.iter("{http://www.w3.org/2000/svg}desc"))
        if "…" not in ep["title"]:
            assert "…" not in cov_desc
        assert " ".join(ep["title"].split()) in " ".join(cov_desc.split())

        ep_html = (DIST / "episodes" / eid / "index.html").read_text(encoding="utf-8")
        assert "act-gutter" not in ep_html
        assert AI_IMAGE_NOTICE in ep_html
        assert ep_html.count(COUPANG_DISCLOSURE) == 1
        assert "top-coupang-disclosure" in ep_html
        assert "wing-ad-left" in ep_html
        assert "wing-ad-right" in ep_html
        assert "mobile-top-coupang" in ep_html
        assert "ep-mid-cut4" in ep_html
        assert "ep-mid-cut9" in ep_html
        assert "ep-bottom" in ep_html
        assert "promo-event-banner" in ep_html
        assert "https://ads-partners.coupang.com/widgets.html" in ep_html
        assert "https://ads-partners.coupang.com/banners/" in ep_html
        assert "comic-cut cut" in ep_html
        assert "letter caption" in ep_html
        assert "pick-goldbox.webp" not in ep_html
        assert "ad-thumb-img" not in ep_html
        assert "G-QP5Q67GE5B" in ep_html
        for marker in DISALLOWED_EDITOR_MARKERS + DISALLOWED_FAKE_SERVER_MARKERS + FORBIDDEN_UX_MARKERS + ["★", "베스트 댓글", "+ 관심"]:
            assert marker not in ep_html

        for c_idx in range(1, target_n + 1):
            cut_webp_rel = f"/assets/toons/{eid}/cut-{c_idx:02d}.webp"
            assert cut_webp_rel in ep_html
            cut_webp_file = DIST / "assets" / "toons" / eid / f"cut-{c_idx:02d}.webp"
            assert cut_webp_file.exists()
            assert cut_webp_file.stat().st_size > 25_000
            with Image.open(cut_webp_file) as panel_im:
                assert panel_im.size == (1080, 1080)

            cut_file = DIST / "assets" / "toons" / eid / f"cut-{c_idx:02d}.svg"
            assert cut_file.exists()
            cut_xml = cut_file.read_text(encoding="utf-8")
            assert 'viewBox="0 0 1080 1080"' in cut_xml
            assert "data:image/webp;base64," in cut_xml
            for marker in FORBIDDEN_UX_MARKERS:
                assert marker not in cut_xml
            root = ET.fromstring(cut_xml)
            desc_text = "".join(el.text or "" for el in root.iter("{http://www.w3.org/2000/svg}desc"))
            panel = ep["panels"][c_idx - 1]
            for expected_phrase in (panel["line"], panel["subline"]):
                norm_exp = " ".join(expected_phrase.split())
                norm_desc = " ".join(desc_text.split())
                assert norm_exp in norm_desc, f"{eid} cut-{c_idx:02d} missing {norm_exp!r}"
            if eid == "ep02-love-wedding" and c_idx == 13:
                for token in ("영구 퇴출", "답례 선물", "돌렸어요"):
                    assert token in desc_text, f"EP02 cut-13 missing {token}"
            if eid == "ep05-finance-jeonse" and c_idx == 9:
                for token in ("채권최고액", "120,000,000원", "접수일", "어제 16시 12분", "저당권 설정"):
                    assert token in desc_text, f"EP05 cut-09 missing {token}"
        assert not (DIST / "assets" / "toons" / eid / f"cut-{target_n + 1:02d}.webp").exists()
        assert not (DIST / "assets" / "toons" / eid / f"cut-{target_n + 1:02d}.svg").exists()

    assert len(seen_cut_counts) >= 5
