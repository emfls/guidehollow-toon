"""Tests for the comic.naver.com style AI-illustrated portal toon.guidehollow.com."""
from __future__ import annotations

from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from content.episodes import EPISODES  # noqa: E402
from tools.build import AI_IMAGE_NOTICE, DISALLOWED_EDITOR_MARKERS, DIST, build_site  # noqa: E402


def test_build_portal_matches_comic_naver_layout() -> None:
    stats = build_site(ad_mode="coupang")
    assert stats["episodes"] == 10
    assert stats["svgs"] == 190  # 10 covers + 180 cuts

    home_html = (DIST / "index.html").read_text(encoding="utf-8")
    assert "이달의 신규 웹툰" in home_html
    assert "요일별 전체 웹툰" in home_html
    assert "첫 화 보기" in home_html
    assert "G-QP5Q67GE5B" in home_html
    assert AI_IMAGE_NOTICE in home_html
    for marker in DISALLOWED_EDITOR_MARKERS:
        assert marker not in home_html

    for ep in EPISODES:
        eid = ep["id"]
        assert len(ep["panels"]) == 18
        assert len(ep["bestComments"]) == 3

        cover_path = DIST / "assets" / "toons" / eid / "cover.svg"
        assert cover_path.exists()
        cover_xml = cover_path.read_text(encoding="utf-8")
        assert 'viewBox="0 0 480 620"' in cover_xml
        assert "data:image/jpeg;base64," in cover_xml
        ET.fromstring(cover_xml)

        ep_html = (DIST / "episodes" / eid / "index.html").read_text(encoding="utf-8")
        assert "act-gutter" not in ep_html
        assert AI_IMAGE_NOTICE in ep_html
        assert ep["coupang"]["url"] in ep_html
        assert "G-QP5Q67GE5B" in ep_html
        for marker in DISALLOWED_EDITOR_MARKERS:
            assert marker not in ep_html

        for c_idx in range(1, 19):
            cut_rel = f"/assets/toons/{eid}/cut-{c_idx:02d}.svg"
            assert cut_rel in ep_html
            cut_file = DIST / "assets" / "toons" / eid / f"cut-{c_idx:02d}.svg"
            assert cut_file.exists()
            cut_xml = cut_file.read_text(encoding="utf-8")
            assert 'viewBox="0 0 690 1120"' in cut_xml
            assert 'fill="#ffffff"' in cut_xml
            assert "data:image/jpeg;base64," in cut_xml
            ET.fromstring(cut_xml)
