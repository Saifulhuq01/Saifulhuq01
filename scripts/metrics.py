"""Live data for the profile dashboard, fetched without any personal token.

Every fetcher returns None on failure so the caller can fall back to the
last good snapshot instead of publishing an empty chart.
"""
import json
import os
import re
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone

from graphics import MONO, SANS, THEMES, esc

GITHUB_USER = "Saifulhuq01"
LEETCODE_USER = "saiful_huq"
UA = "Saifulhuq01-profile-readme"

# Websites and side apps, left out of the Languages panel so it reflects
# backend and open-source work. Edit freely; the panel says it excludes them.
EXCLUDE_FROM_LANGUAGES = {
    "rd-biz-spark", "rdbizaisolution", "rdbizFoodproduct", "azar-vibes", "saifulhuq-dev",
    "DSA-Tracker", "linkedin-apply-nav", "veto",
}

LANG_COLORS = {
    "Java": "#b07219", "TypeScript": "#3178c6", "Kotlin": "#A97BFF", "HTML": "#e34c26",
    "JavaScript": "#f1e05a", "Python": "#3572A5", "C++": "#f34b7d", "C": "#8b949e",
    "CSS": "#663399", "Dart": "#00B4AB", "SCSS": "#c6538c", "Shell": "#89e051",
}


def _get(url, data=None, headers=None):
    h = {"User-Agent": UA, **(headers or {})}
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com"):
        h["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=h)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode()


def fetch_contributions():
    """Daily contribution counts for the last year, from the public calendar page."""
    try:
        html = _get(f"https://github.com/users/{GITHUB_USER}/contributions")
    except Exception as e:
        print("contributions: fetch failed:", e)
        return None
    cells = dict(re.findall(r'data-date="(\d{4}-\d{2}-\d{2})" id="(contribution-day-component-\d+-\d+)"', html))
    by_id = {v: k for k, v in cells.items()}
    days = {}
    for cid, text in re.findall(r'<tool-tip[^>]*for="(contribution-day-component-\d+-\d+)"[^>]*>([^<]*)</tool-tip>', html):
        m = re.match(r"(\d+) contributions?", text)
        if cid in by_id:
            days[by_id[cid]] = int(m.group(1)) if m else 0
    levels = {d: int(l) for d, l in re.findall(r'data-date="(\d{4}-\d{2}-\d{2})"[^>]*data-level="(\d)"', html)}
    if not days:
        return None
    return [{"date": d, "count": days[d], "level": levels.get(d, 0)} for d in sorted(days)]


def fetch_leetcode():
    query = ("query($u:String!){matchedUser(username:$u){submitStatsGlobal{acSubmissionNum{difficulty count}}"
             " userCalendar{streak totalActiveDays}}}")
    try:
        raw = _get("https://leetcode.com/graphql",
                   data=json.dumps({"query": query, "variables": {"u": LEETCODE_USER}}).encode(),
                   headers={"Content-Type": "application/json", "Referer": "https://leetcode.com"})
        u = json.loads(raw)["data"]["matchedUser"]
        solved = {s["difficulty"]: s["count"] for s in u["submitStatsGlobal"]["acSubmissionNum"]}
        return {"total": solved["All"], "easy": solved["Easy"], "medium": solved["Medium"], "hard": solved["Hard"],
                "active_days": u["userCalendar"]["totalActiveDays"], "best_streak": u["userCalendar"]["streak"]}
    except Exception as e:
        print("leetcode: fetch failed:", e)
        return None


def fetch_fineract_prs():
    q = f"repo:apache/fineract+author:{GITHUB_USER}+is:pr+is:merged"
    try:
        d = json.loads(_get(f"https://api.github.com/search/issues?q={q}&sort=created&order=desc&per_page=20"))
        return [{"number": i["number"], "title": re.sub(r"^FINERACT-\d+:\s*", "", i["title"]),
                 "merged": (i.get("pull_request") or {}).get("merged_at") or i["closed_at"]} for i in d["items"]]
    except Exception as e:
        print("fineract: fetch failed:", e)
        return None


def fetch_repos():
    """Language byte counts per own (non-fork, non-archived) repo, plus stars."""
    try:
        repos = json.loads(_get(f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100&type=owner"))
        per_repo = {r["name"]: json.loads(_get(r["languages_url"]))
                    for r in repos if not r["fork"] and not r["archived"]}
        stars = {r["name"]: r["stargazers_count"] for r in repos}
        return {"repo_languages": per_repo, "stars": stars}
    except Exception as e:
        print("repos: fetch failed:", e)
        return None


# ─── Derived numbers ───
def language_totals(data):
    if "repo_languages" not in data:      # older snapshot: already aggregated
        return data["languages"], False
    totals = Counter()
    for repo, langs in data["repo_languages"].items():
        if repo not in EXCLUDE_FROM_LANGUAGES:
            totals.update(langs)
    return dict(totals), True


def streaks(days):
    counts = [d["count"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    # Today may not have activity yet, so a streak ending yesterday still counts.
    tail = counts[:-1] if counts and counts[-1] == 0 else counts
    for c in reversed(tail):
        if not c:
            break
        current += 1
    return current, longest


def fmt_day(iso):
    d = date.fromisoformat(iso[:10])
    return f"{d:%b} {d.day}, {d.year}"


# ─── Dashboard SVG ───
def dashboard(t, data):
    W, H = 1200, 780
    out = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Live metrics: GitHub contributions, LeetCode progress, Apache Fineract pull requests and languages.">
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="{t['bg']}" stroke="{t['line']}"/>''']

    def panel(x, y, w, h, title, right=""):
        out.append(f'''
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{t['card']}" stroke="{t['line']}"/>
  <text x="{x + 22}" y="{y + 32}" font-family="{MONO}" font-size="12.5" letter-spacing="1.4" fill="{t['muted']}">{esc(title)}</text>
  <text x="{x + w - 22}" y="{y + 32}" text-anchor="end" font-family="{MONO}" font-size="12.5" fill="{t['accent']}">{esc(right)}</text>''')

    def grow(attr, final, begin, dur, start="0"):
        # Starts at load and holds `start` until `begin`. The element's own
        # attribute is the final value, so renderers that skip SMIL (or
        # load the image late) still show the finished chart.
        total = begin + dur
        return (f'<animate attributeName="{attr}" values="{start};{start};{final}" '
                f'keyTimes="0;{begin / total:.3f};1" dur="{total:.2f}s" fill="freeze"/>')

    def fade(begin, dur=0.5):
        return grow("opacity", "1", begin, dur)

    # Header: status line in the style of a service health check
    out.append(f'''
  <circle cx="44" cy="40" r="5" fill="{t['green']}"><animate attributeName="opacity" values="1;0.35;1" dur="2.4s" repeatCount="indefinite"/></circle>
  <text x="60" y="45" font-family="{MONO}" font-size="15" fill="{t['fg']}">saifulhuq01 · telemetry</text>
  <text x="{W - 40}" y="45" text-anchor="end" font-family="{MONO}" font-size="13" fill="{t['faint']}">updated {esc(data['updated'])} · refreshed daily</text>''')

    # ── Contributions heatmap ──
    days = data["contributions"]
    _, longest = streaks(days)
    total = sum(d["count"] for d in days)
    busiest = max(days, key=lambda d: d["count"])
    px, py, pw, ph = 32, 70, 1136, 318
    panel(px, py, pw, ph, "CONTRIBUTIONS · LAST 12 MONTHS", f"{total} total")
    step, cell = 19, 15
    first = date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7          # GitHub weeks start on Sunday
    cols = (offset + len(days) + 6) // 7
    gx = px + (pw - cols * step) // 2 + 14
    gy = py + 76
    for label, row in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        out.append(f'<text x="{gx - 12}" y="{gy + row * step + 12}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{t["faint"]}">{label}</text>')
    last_month = None
    for i, d in enumerate(days):
        k = offset + i
        col, row = divmod(k, 7)
        dt = date.fromisoformat(d["date"])
        if row == 0 or i == 0:
            if dt.month != last_month and col < cols - 1:
                out.append(f'<text x="{gx + col * step}" y="{gy - 10}" font-family="{MONO}" font-size="11" fill="{t["faint"]}">{dt:%b}</text>')
                last_month = dt.month
        out.append(f'<rect x="{gx + col * step}" y="{gy + row * step}" width="{cell}" height="{cell}" rx="3.5" fill="{t["heat"][d["level"]]}">'
                   f'<title>{d["count"]} on {fmt_day(d["date"])}</title>{fade(0.15 + col * 0.022, 0.35)}</rect>')

    active = sum(1 for d in days if d["count"])
    tiles = [(str(total), "contributions"), (str(active), "active days"),
             (f"{longest}d", "longest streak"), (f"{busiest['count']}", f"best day · {fmt_day(busiest['date'])}")]
    tw = (pw - 44 - 3 * 14) / 4
    ty = py + ph - 74
    for i, (v, label) in enumerate(tiles):
        tx = px + 22 + i * (tw + 14)
        out.append(f'''<g>{fade(1.3 + i * 0.1)}
    <rect x="{tx:.0f}" y="{ty}" width="{tw:.0f}" height="56" rx="8" fill="{t['bg']}" stroke="{t['line']}"/>
    <text x="{tx + 16:.0f}" y="{ty + 35}" font-family="{SANS}" font-size="22" font-weight="700" fill="{t['fg']}">{esc(v)}</text>
    <text x="{tx + tw - 16:.0f}" y="{ty + 34}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{t['muted']}">{esc(label)}</text>
  </g>''')

    # ── Bottom row ──
    by, bh = 404, 344
    bw = (pw - 2 * 16) // 3
    xs = [px, px + bw + 16, px + 2 * (bw + 16)]

    # LeetCode: solved split by difficulty
    lc = data["leetcode"]
    x = xs[0]
    panel(x, by, bw, bh, "LEETCODE", f"@{LEETCODE_USER}")
    cx, cy, r = x + 96, by + 158, 60
    circ = 2 * 3.14159 * r
    acc = 0
    segs = [("Easy", lc["easy"], t["green"]), ("Medium", lc["medium"], t["amber"]), ("Hard", lc["hard"], t["red"])]
    out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{t["line"]}" stroke-width="14"/>')
    for i, (_, n, color) in enumerate(segs):
        seg = circ * n / max(lc["total"], 1)
        gap = 3 if seg > 6 else 0
        dash = f"{max(seg - gap, 0):.1f} {circ:.1f}"
        out.append(f'''<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="14" stroke-dasharray="{dash}"
      stroke-dashoffset="{-acc:.1f}" transform="rotate(-90 {cx} {cy})">
      {grow("stroke-dasharray", dash, 0.4 + i * 0.35, 0.6, start=f"0 {circ:.1f}")}
    </circle>''')
        acc += seg
    out.append(f'''<text x="{cx}" y="{cy + 6}" text-anchor="middle" font-family="{SANS}" font-size="32" font-weight="700" fill="{t['fg']}">{lc['total']}</text>
  <text x="{cx}" y="{cy + 28}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{t['muted']}">solved</text>''')
    bx, bwid = x + 186, bw - 186 - 22
    peak = max(n for _, n, _ in segs) or 1
    for i, (name, n, color) in enumerate(segs):
        yy = by + 104 + i * 50
        w = bwid * n / peak
        out.append(f'''<text x="{bx}" y="{yy}" font-family="{MONO}" font-size="12.5" fill="{t['muted']}">{name}</text>
  <text x="{bx + bwid}" y="{yy}" text-anchor="end" font-family="{SANS}" font-size="15" font-weight="600" fill="{t['fg']}">{n}</text>
  <rect x="{bx}" y="{yy + 10}" width="{bwid}" height="8" rx="4" fill="{t['bg']}"/>
  <rect x="{bx}" y="{yy + 10}" width="{w:.1f}" height="8" rx="4" fill="{color}">{grow("width", f"{w:.1f}", 0.5 + i * 0.2, 0.7)}</rect>''')
    out.append(f'''<line x1="{x + 22}" y1="{by + bh - 62}" x2="{x + bw - 22}" y2="{by + bh - 62}" stroke="{t['line']}"/>
  <text x="{x + 22}" y="{by + bh - 30}" font-family="{MONO}" font-size="13" fill="{t['muted']}">{lc['active_days']} active days</text>
  <text x="{x + bw - 22}" y="{by + bh - 30}" text-anchor="end" font-family="{MONO}" font-size="13" fill="{t['accent']}">best streak {lc['best_streak']}d</text>''')

    # Apache Fineract: merged PRs as a commit log
    prs = data["fineract"]
    x = xs[1]
    panel(x, by, bw, bh, "APACHE/FINERACT", f"{len(prs)} merged")
    lx = x + 34
    shown = prs[:4]
    if shown:
        out.append(f'<line x1="{lx}" y1="{by + 72}" x2="{lx}" y2="{by + 72 + (len(shown) - 1) * 56}" stroke="{t["line"]}" stroke-width="2"/>')
    for i, pr in enumerate(shown):
        yy = by + 72 + i * 56
        title = pr["title"] if len(pr["title"]) <= 38 else pr["title"][:37].rstrip() + "…"
        out.append(f'''<g>{fade(0.5 + i * 0.18)}
    <circle cx="{lx}" cy="{yy}" r="6" fill="{t['card']}" stroke="{t['accent']}" stroke-width="2.5"/>
    <text x="{lx + 20}" y="{yy + 5}" font-family="{SANS}" font-size="14" fill="{t['fg']}">{esc(title)}</text>
    <text x="{lx + 20}" y="{yy + 25}" font-family="{MONO}" font-size="12" fill="{t['faint']}">#{pr['number']} · merged {fmt_day(pr['merged'])}</text>
  </g>''')
    out.append(f'''<line x1="{x + 22}" y1="{by + bh - 62}" x2="{x + bw - 22}" y2="{by + bh - 62}" stroke="{t['line']}"/>
  <text x="{x + 22}" y="{by + bh - 30}" font-family="{MONO}" font-size="13" fill="{t['muted']}">CI: MariaDB · PostgreSQL · MySQL</text>''')

    # Languages across own repos
    lang_map, filtered = language_totals(data)
    langs = sorted(lang_map.items(), key=lambda kv: -kv[1])
    lang_total = sum(v for _, v in langs) or 1
    top = langs[:6]
    other = lang_total - sum(v for _, v in top)
    x = xs[2]
    panel(x, by, bw, bh, "LANGUAGES", "excl. web & app repos" if filtered else "by code size")
    sx, sw, sy = x + 22, bw - 44, by + 66
    out.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="12" rx="6" fill="{t["bg"]}"/>')
    acc = 0
    rows = top + ([("Other", other)] if other > 0 else [])
    for i, (name, v) in enumerate(rows):
        w = sw * v / lang_total
        color = LANG_COLORS.get(name, t["faint"])
        seg_w = f"{max(w - 1.5, 0):.1f}"
        out.append(f'<rect x="{sx + acc:.1f}" y="{sy}" width="{seg_w}" height="12" fill="{color}">{grow("width", seg_w, 0.4 + i * 0.12, 0.4)}</rect>')
        acc += w
        yy = sy + 52 + i * 30
        out.append(f'''<g>{fade(0.6 + i * 0.1)}
    <circle cx="{sx + 6}" cy="{yy - 5}" r="5" fill="{color}"/>
    <text x="{sx + 20}" y="{yy}" font-family="{SANS}" font-size="14.5" fill="{t['fg']}">{esc(name)}</text>
    <text x="{sx + sw}" y="{yy}" text-anchor="end" font-family="{MONO}" font-size="13" fill="{t['muted']}">{100 * v / lang_total:.1f}%</text>
  </g>''')
    # Mask the bar ends so the stacked segments read as one rounded bar
    out.append(f'<rect x="{sx}" y="{sy}" width="{sw}" height="12" rx="6" fill="none" stroke="{t["card"]}" stroke-width="2"/>')

    out.append("</svg>\n")
    return "\n".join(out)


def render_dashboard(out_dir, data):
    for name, t in THEMES.items():
        (out_dir / f"telemetry-{name}.svg").write_text(dashboard(t, data))


def now_label():
    return datetime.now(timezone.utc).strftime("%b %-d, %Y")
