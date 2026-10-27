"""Download the two credited biological reference assets (not result charts)."""
import hashlib
import html
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/assets/references"
OUT.mkdir(parents=True, exist_ok=True)


def get(url):
    request = urllib.request.Request(url, headers={"User-Agent": "DeepNeoAGCourse/1.0 (educational reference assets)"})
    with urllib.request.urlopen(request, timeout=60) as r: return r.read()


records = []
assets = [dict(name="R1_neoantigen_vaccine.jpg", landing="https://www.cancer.gov/news-events/cancer-currents-blog/2025/neoantigen-vaccine-pancreatic-kidney-cancer",
    url="https://www.cancer.gov/sites/www/files/styles/cgov_article/public/cgov_image/media_image/2025-03/neoantigen%20vaccine%20manufacture.jpg?itok=p3HFIlKP",
    license="CC BY 4.0", credit="Adapted from Nature (May 2023), doi:10.1038/s41586-023-06063-y, via NCI. No changes."),
    dict(name="R2_antigen_presentation.svg", landing="https://commons.wikimedia.org/wiki/File:Antigen_presentation.svg",
    url="https://upload.wikimedia.org/wikipedia/commons/4/4d/Antigen_presentation.svg",
    license="CC BY-SA 3.0", credit="Sjef and Wikimedia Commons file-history contributors. No changes.")]
for asset in assets:
    try:
        if not asset["url"]:
            page = get(asset["landing"]).decode("utf-8")
            match = re.search(r'class="fullImage".*?<a href="([^"]+)"', page, flags=re.S)
            if not match: raise ValueError("Original SVG URL not found")
            asset["url"] = html.unescape(match[1])
            if asset["url"].startswith("//"): asset["url"] = "https:" + asset["url"]
        content = get(asset["url"])
        if asset["name"].endswith(".jpg") and not content.startswith(b"\xff\xd8"):
            raise ValueError("Expected JPEG, received another response")
        if asset["name"].endswith(".svg") and b"<svg" not in content[:3000]:
            raise ValueError("Expected SVG, received another response")
        (OUT / asset["name"]).write_bytes(content)
        asset.update(status="downloaded", bytes=len(content), sha256=hashlib.sha256(content).hexdigest())
    except Exception as e:
        asset.update(status="reference_only", reason=str(e))
    records.append(asset)
(OUT / "sources.json").write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
for r in records: print(r["name"], r["status"], r.get("reason", ""))
