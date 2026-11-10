"""Static profile graphics: banner, project cards and stack (dark + light).

GitHub renders repo SVGs through <img>, so: no scripts, no external fonts,
animation via SMIL only.
"""
from pathlib import Path

THEMES = {
    "dark": dict(bg="#0d1117", card="#161b22", line="#30363d", fg="#e6edf3", muted="#8b949e",
                 faint="#6e7681", accent="#a5b4fc", accent_soft="rgba(165,180,252,0.12)",
                 red="#f85149", amber="#d29922", green="#3fb950", glow="rgba(99,102,241,0.35)",
                 heat=["#21262d", "#272b57", "#3b41a0", "#6366f1", "#a5b4fc"]),
    "light": dict(bg="#ffffff", card="#f6f8fa", line="#d0d7de", fg="#1f2328", muted="#59636e",
                  faint="#818b98", accent="#4f46e5", accent_soft="rgba(79,70,229,0.08)",
                  red="#cf222e", amber="#9a6700", green="#1a7f37", glow="rgba(79,70,229,0.14)",
                  heat=["#ebedf0", "#c7d2fe", "#a5b4fc", "#6366f1", "#4338ca"]),
}

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ─── Banner: name + an animated Kafka partition with a dead-letter replay ───
def banner(t):
    W, H = 1200, 430
    x0, x1 = 190, 1140           # lane track extent
    top, dlq = 300, 372          # lane centre lines
    cycle = 8

    # Regular messages streaming along the topic
    stream = []
    for i in range(5):
        begin = -i * cycle / 5
        stream.append(f'''
    <rect x="-13" y="-7" width="26" height="14" rx="4" fill="{t['accent']}" opacity="0.85">
      <animateMotion path="M{x0 + 16},{top} L{x1 - 16},{top}" dur="{cycle}s" begin="{begin}s" repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0;0.85;0.85;0" keyTimes="0;0.04;0.94;1" dur="{cycle}s" begin="{begin}s" repeatCount="indefinite"/>
    </rect>''')

    # The one that fails: topic → DLQ → transform → replayed once → back on the topic
    path = f"M{x0 + 16},{top} L520,{top} L520,{dlq} L620,{dlq} L700,{top} L{x1 - 16},{top}"
    kp = "0;0.328;0.394;0.488;0.488;0.587;1;1"
    kt = "0;0.25;0.325;0.425;0.575;0.65;0.925;1"
    special = f'''
    <g>
      <animateMotion path="{path}" dur="{cycle}s" repeatCount="indefinite" calcMode="linear" keyPoints="{kp}" keyTimes="{kt}"/>
      <rect x="-15" y="-8" width="30" height="16" rx="4" fill="{t['accent']}">
        <animate attributeName="fill" dur="{cycle}s" repeatCount="indefinite"
          values="{t['accent']};{t['accent']};{t['red']};{t['red']};{t['amber']};{t['accent']};{t['accent']}"
          keyTimes="0;0.24;0.26;0.43;0.47;0.58;1"/>
        <animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.04;0.92;0.95;1" dur="{cycle}s" repeatCount="indefinite"/>
      </rect>
    </g>'''

    def status(text, color, on, off):
        return f'''
    <text x="700" y="{dlq + 5}" font-family="{MONO}" font-size="13.5" fill="{color}" opacity="0">{esc(text)}
      <animate attributeName="opacity" calcMode="discrete" values="0;1;0" keyTimes="0;{on:.3f};{off:.3f}" dur="{cycle}s" repeatCount="indefinite"/>
    </text>'''

    statuses = (status("✕ consumer failed · sent to dead-letter topic", t["red"], 0.27, 0.43)
                + status("↻ fixing payload with a JSONata transform", t["amber"], 0.44, 0.58)
                + status("✓ replayed once · UNIQUE(topic, partition, offset)", t["accent"], 0.59, 0.92))

    ticks = "".join(
        f'<line x1="{x}" y1="{y - 17}" x2="{x}" y2="{y + 17}" stroke="{t["line"]}" stroke-width="1"/>'
        for y in (top, dlq) for x in range(x0 + 60, x1, 60))
    offsets = "".join(
        f'<text x="{x0 + 30 + i * 60}" y="{top - 26}" text-anchor="middle" font-family="{MONO}" font-size="11" fill="{t["faint"]}">{4180 + i}</text>'
        for i in range(0, 16))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Mohammed Saifulhuq — Software Engineer. Animation: a Kafka message fails, lands in a dead-letter topic, is fixed, and replayed once.">
  <defs>
    <radialGradient id="g" cx="0.88" cy="0.05" r="0.7">
      <stop offset="0" stop-color="{t['glow']}"/>
      <stop offset="1" stop-color="{t['bg']}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="{t['bg']}" stroke="{t['line']}"/>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="18" fill="url(#g)"/>

  <text x="60" y="78" font-family="{MONO}" font-size="15" letter-spacing="2" fill="{t['accent']}">SOFTWARE ENGINEER · CHENNAI, INDIA</text>
  <text x="58" y="146" font-family="{SANS}" font-size="62" font-weight="700" letter-spacing="-1.5" fill="{t['fg']}">Mohammed Saifulhuq</text>
  <text x="60" y="190" font-family="{SANS}" font-size="23" fill="{t['muted']}">Backend systems that stay correct under real traffic — and recover when they don't.</text>

  <text x="60" y="{top + 5}" font-family="{MONO}" font-size="14" fill="{t['muted']}">orders</text>
  <text x="60" y="{dlq + 5}" font-family="{MONO}" font-size="14" fill="{t['muted']}">orders.dlq</text>
  <rect x="{x0}" y="{top - 17}" width="{x1 - x0}" height="34" rx="8" fill="{t['card']}" stroke="{t['line']}"/>
  <rect x="{x0}" y="{dlq - 17}" width="{x1 - x0}" height="34" rx="8" fill="{t['card']}" stroke="{t['line']}" stroke-dasharray="4 4"/>
  {ticks}
  {offsets}
  {''.join(stream)}
  {special}
  {statuses}
</svg>
'''


# ─── Project cards ───
def card(t, eyebrow, title, desc, points, stack, badge=""):
    W, H = 600, 330
    desc_lines = "".join(
        f'<text x="32" y="{124 + i * 24}" font-family="{SANS}" font-size="17" fill="{t["muted"]}">{esc(l)}</text>'
        for i, l in enumerate(desc))
    y = 124 + len(desc) * 24 + 18
    pts = "".join(
        f'<rect x="32" y="{y + i * 30 - 11}" width="6" height="6" rx="1.5" fill="{t["accent"]}"/>'
        f'<text x="48" y="{y + i * 30 - 3}" font-family="{MONO}" font-size="14.5" fill="{t["fg"]}">{esc(p)}</text>'
        for i, p in enumerate(points))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}: {esc(' '.join(desc))}">
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="{t['bg']}" stroke="{t['line']}"/>
  <text x="32" y="52" font-family="{MONO}" font-size="13" letter-spacing="1.6" fill="{t['accent']}">{esc(eyebrow)}</text>
  <text x="32" y="92" font-family="{SANS}" font-size="30" font-weight="700" letter-spacing="-0.6" fill="{t['fg']}">{esc(title)}</text>
  <text x="{W - 32}" y="92" text-anchor="end" font-family="{SANS}" font-size="24" fill="{t['faint']}">↗</text>
  {desc_lines}
  {pts}
  <line x1="32" y1="{H - 56}" x2="{W - 32}" y2="{H - 56}" stroke="{t['line']}"/>
  <text x="32" y="{H - 26}" font-family="{MONO}" font-size="13.5" fill="{t['muted']}">{esc(stack)}</text>
  <text x="{W - 32}" y="{H - 26}" text-anchor="end" font-family="{MONO}" font-size="13.5" fill="{t['accent']}">{esc(badge)}</text>
</svg>
'''


# ─── Stack ───
def stack_svg(t):
    rows = [
        ("BACKEND", "Java 17 · Spring Boot 3 · Jakarta EE (JAX-RS) · JPA/Hibernate · Apache Kafka"),
        ("DATA", "PostgreSQL · MariaDB · MySQL · Liquibase"),
        ("FRONTEND", "Angular · TypeScript · RxJS · Electron"),
        ("TOOLING", "JUnit 5 · Mockito · EmbeddedKafka · Docker · GitHub Actions · Keycloak"),
    ]
    W, row_h = 1200, 56
    H = 24 + row_h * len(rows)
    body = ""
    for i, (k, v) in enumerate(rows):
        y = 24 + i * row_h
        if i:
            body += f'<line x1="32" y1="{y}" x2="{W - 32}" y2="{y}" stroke="{t["line"]}"/>'
        body += (f'<text x="32" y="{y + 34}" font-family="{MONO}" font-size="14" letter-spacing="1.6" fill="{t["faint"]}">{k}</text>'
                 f'<text x="220" y="{y + 35}" font-family="{SANS}" font-size="19" fill="{t["fg"]}">{esc(v)}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Tech stack">
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="{t['bg']}" stroke="{t['line']}"/>
  {body}
</svg>
'''


def render_static(out: Path, stars: int | None = None, fineract_prs: int = 4):
    for name, t in THEMES.items():
        (out / f"banner-{name}.svg").write_text(banner(t))
        (out / f"dlq-revive-{name}.svg").write_text(card(
            t, "CREATOR & MAINTAINER", "DLQ Revive",
            ["Inspect, fix and replay Kafka dead-letter messages", "without rebalancing live consumer groups."],
            ["assign() + seek() — never joins a group", "UNIQUE(topic, partition, offset) guard", "JSONata transforms — no code execution"],
            "Java 17 · Spring Boot 3 · Kafka · PostgreSQL",
            badge=f"★ {stars}" if stars is not None else "MIT"))
        (out / f"fineract-{name}.svg").write_text(card(
            t, "OPEN SOURCE CONTRIBUTOR", "Apache Fineract",
            ["Core banking platform from the Apache", f"Software Foundation. {fineract_prs} PRs merged."],
            ["Force Debit for savings accounts", "SQL-injection fix in email & SMS reads", "Request-level idempotency proposal"],
            "Java 17 · Spring Boot 3 · Liquibase · Docker",
            badge="ASF"))
        (out / f"stack-{name}.svg").write_text(stack_svg(t))
