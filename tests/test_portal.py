"""Tests for comic.naver.com style static webtoon portal toon.guidehollow.com."""
from __future__ import annotations

from pathlib import Path
import sys
import xml.etree.ElementTree as ET

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


def test_build_portal_matches_comic_naver_and_no_fake_server() -> None:
    stats = build_site(ad_mode="coupang")
    episodes = prepare_episodes()
    expected_cuts = sum(EPISODE_CUT_COUNTS[ep["id"]] for ep in episodes)
    assert stats["episodes"] == 10
    assert stats["cuts"] == expected_cuts
    assert stats["svgs"] == len(episodes) + expected_cuts

    home_html = (DIST / "index.html").read_text(encoding="utf-8")
    assert "이달의 신규 웹툰" in home_html
    assert "장르별 전체 웹툰" in home_html
    assert "첫 화 보기" in home_html
    assert "G-QP5Q67GE5B" in home_html
    assert AI_IMAGE_NOTICE in home_html
    assert COUPANG_DISCLOSURE in home_html
    assert "wing-ad-left" in home_html
    assert "wing-ad-right" in home_html
    assert "coupang-strip-box" in home_html
    for marker in DISALLOWED_EDITOR_MARKERS + DISALLOWED_FAKE_SERVER_MARKERS + ["★", "조회 482만"]:
        assert marker not in home_html

    seen_cut_counts = set()
    for ep in episodes:
        eid = ep["id"]
        target_n = EPISODE_CUT_COUNTS[eid]
        assert len(ep["panels"]) == target_n
        seen_cut_counts.add(target_n)

        cover_path = DIST / "assets" / "toons" / eid / "cover.svg"
        assert cover_path.exists()
        cover_xml = cover_path.read_text(encoding="utf-8")
        assert 'viewBox="0 0 480 620"' in cover_xml
        assert "data:image/jpeg;base64," in cover_xml
        ET.fromstring(cover_xml)

        ep_html = (DIST / "episodes" / eid / "index.html").read_text(encoding="utf-8")
        assert "act-gutter" not in ep_html
        assert AI_IMAGE_NOTICE in ep_html
        assert COUPANG_DISCLOSURE in ep_html
        assert "wing-ad-left" in ep_html
        assert "wing-ad-right" in ep_html
        assert "mobile-top-coupang" in ep_html
        assert "ep-mid-cut4" in ep_html
        assert "ep-mid-cut9" in ep_html
        assert "ep-bottom" in ep_html
        assert ep["coupang"]["url"] in ep_html
        assert "G-QP5Q67GE5B" in ep_html
        for marker in DISALLOWED_EDITOR_MARKERS + DISALLOWED_FAKE_SERVER_MARKERS + ["★", "베스트 댓글", "+ 관심"]:
            assert marker not in ep_html

        for c_idx in range(1, target_n + 1):
            cut_rel = f"/assets/toons/{eid}/cut-{c_idx:02d}.svg"
            assert cut_rel in ep_html
            cut_file = DIST / "assets" / "toons" / eid / f"cut-{c_idx:02d}.svg"
            assert cut_file.exists()
            cut_xml = cut_file.read_text(encoding="utf-8")
            assert 'viewBox="0 0 690 1120"' in cut_xml
            assert 'fill="#ffffff"' in cut_xml
            assert "data:image/jpeg;base64," in cut_xml
            root = ET.fromstring(cut_xml)
            svg_texts = " ".join("".join(el.itertext()).strip() for el in root.iter("{http://www.w3.org/2000/svg}text"))
            panel = ep["panels"][c_idx - 1]
            for expected_phrase in (panel["line"], panel["subline"]):
                norm_exp = " ".join(expected_phrase.split())
                norm_svg = " ".join(svg_texts.split())
                if "…" not in expected_phrase:
                    assert "…" not in svg_texts or expected_phrase in norm_svg
                assert norm_exp in norm_svg, f"{eid} cut-{c_idx:02d} truncated: {norm_exp!r} not in {norm_svg!r}"
            if eid == "ep02-love-wedding" and c_idx == 13:
                for token in ("영구 퇴출", "답례 선물", "돌렸어요"):
                    assert token in svg_texts, f"EP02 cut-13 missing {token}"
            if eid == "ep05-finance-jeonse" and c_idx == 9:
                for token in ("채권최고액", "120,000,000원", "접수일", "어제 16시 12분", "저당권 설정"):
                    assert token in svg_texts, f"EP05 cut-09 missing {token}"
        assert not (DIST / "assets" / "toons" / eid / f"cut-{target_n + 1:02d}.svg").exists()

    assert len(seen_cut_counts) >= 5
