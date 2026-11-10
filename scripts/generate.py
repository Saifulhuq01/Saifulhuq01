"""Regenerates every graphic in assets/. Run daily by .github/workflows/telemetry.yml.

    python3 scripts/generate.py            # fetch live data, then render
    python3 scripts/generate.py --offline  # render from the last snapshot only

Any source that fails to fetch keeps its value from assets/telemetry.json, so
a flaky API never replaces a chart with zeros.
"""
import json
import sys
from pathlib import Path

from graphics import render_static
from metrics import (fetch_contributions, fetch_fineract_prs, fetch_leetcode,
                     fetch_repos, now_label, render_dashboard)

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SNAPSHOT = ASSETS / "telemetry.json"


def main():
    ASSETS.mkdir(exist_ok=True)
    data = json.loads(SNAPSHOT.read_text()) if SNAPSHOT.exists() else {}

    if "--offline" not in sys.argv:
        fresh = {
            "contributions": fetch_contributions(),
            "leetcode": fetch_leetcode(),
            "fineract": fetch_fineract_prs(),
        }
        repos = fetch_repos()
        if repos:
            fresh["repo_languages"], fresh["stars"] = repos["repo_languages"], repos["stars"]
            data.pop("languages", None)   # superseded by per-repo counts
        changed = {k: v for k, v in fresh.items() if v is not None}
        data.update(changed)
        if changed:
            data["updated"] = now_label()

    missing = [k for k in ("contributions", "leetcode", "fineract") if k not in data]
    if "repo_languages" not in data and "languages" not in data:
        missing.append("repo_languages")
    if missing:
        sys.exit(f"No data yet for: {', '.join(missing)}. Run once with network access.")

    SNAPSHOT.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
    render_static(ASSETS, stars=data.get("stars", {}).get("dlq-revive"), fineract_prs=len(data["fineract"]))
    render_dashboard(ASSETS, data)
    print("rendered", sorted(p.name for p in ASSETS.glob("*.svg")))


if __name__ == "__main__":
    main()
