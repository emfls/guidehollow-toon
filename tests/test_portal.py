import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ZIP = ROOT / "artifacts/guidehollow-toon-release.zip"


def test_build_outputs_all_routes_and_dual_ad_mode():
    subprocess.run([sys.executable, str(ROOT / "tools/build.py")], cwd=ROOT, check=True)
    assert (DIST / "index.html").is_file()
    assert (DIST / "studio/index.html").is_file()
    assert (DIST / "ads.txt").read_text(encoding="utf-8").strip() == "google.com, pub-8830524482034754, DIRECT, f08c47fec0942fa0"
    assert (DIST / "CNAME").read_text(encoding="utf-8").strip() == "toon.guidehollow.com"
    for slug in ("about", "privacy", "terms", "contact"):
        assert (DIST / slug / "index.html").is_file()

    episodes = json.loads((DIST / "assets/episodes.json").read_text(encoding="utf-8"))
    assert len(episodes) == 10
    for ep in episodes:
        ep_html = (DIST / "episodes" / ep["id"] / "index.html").read_text(encoding="utf-8")
        assert ep["coupang"]["affiliateUrl"] in ep_html
        assert "shopping.guidehollow.com" in ep_html
        assert len(ep["panels"]) == 6

    ad_js = (DIST / "assets/ad-manager.js").read_text(encoding="utf-8")
    subprocess.run(["node", "--check", str(DIST / "assets/ad-manager.js")], check=True)
    subprocess.run(["node", "--check", str(DIST / "assets/studio.js")], check=True)
    assert 'AD_MODE = (override === "adsense" || override === "coupang") ? override : "coupang"' in ad_js
    assert "api-gateway.coupang.com" not in ad_js
    assert "https://coupa.ng/cqZC1w" in ad_js
    assert "https://ads-partners.coupang.com/widgets.html" in ad_js
    assert "ca-pub-8830524482034754" in ad_js
    assert "이 포스팅은 쿠팡 파트너스 활동의 일환으로" in ad_js

    sitemap = ET.parse(DIST / "sitemap.xml")
    locs = {node.text for node in sitemap.iter() if node.tag.endswith("loc")}
    assert len(locs) == 16
    assert ZIP.is_file()
    with zipfile.ZipFile(ZIP) as zf:
        names = set(zf.namelist())
        assert "index.html" in names
        assert "studio/index.html" in names
        assert "assets/ad-manager.js" in names
