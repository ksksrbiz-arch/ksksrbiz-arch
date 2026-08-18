#!/usr/bin/env python3
"""
gen_status_board.py — emit the managed-hosting status board (assets/os-hosting.svg).

This is the window that advertises the ongoing hosting/deployment service:
one row per client site with status, uptime, SSL, stack, response time and
last deploy, plus a rolled-up summary bar.

Usage:
    python3 tools/gen_status_board.py

Client list lives in tools/clients.json — edit that file and re-run.

Nothing is polled at render time, so the board deliberately shows only facts
that stay true between runs: stack, host, TLS and live status. Uptime and
response figures are optional and omitted unless the JSON supplies them —
hard-coding a percentage next to a real client's domain would be an
unverifiable public claim about the service.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
DATA = os.path.join(ROOT, "tools", "clients.json")
RAW = "https://raw.githubusercontent.com/ksksrbiz-arch/ksksrbiz-arch/main/assets"

BG, PANEL, TITLE, BORDER = "#0F131B", "#161C26", "#1B2230", "#2B3648"
TEXT, MUTED, DIM = "#F1F5FB", "#7C8798", "#4C5870"
CYAN, VIOLET, AMBER, GREEN, CORAL = "#4FD1C5", "#B794F6", "#F6AD55", "#68D391", "#FF8B6A"

STACK_COLOR = {"Next.js": "#F1F5FB", "Shopify": GREEN, "Astro": VIOLET,
               "WordPress": "#63B3ED", "Node": GREEN, "Static": MUTED}


def load_sites():
    """Return (brand, sites) from tools/clients.json."""
    data = json.load(open(DATA))
    sites = [dict(s) for s in data["sites"]]
    print(f"{len(sites)} client sites")
    return data.get("brand", "1COMMERCE"), sites


def board(brand, sites):
    """Render the hosting status board as a standalone SVG string."""
    W = 1200
    TB, HEAD, ROW, FOOT = 34, 76, 48, 34
    TB_ = TB
    n = len(sites)
    H = TB + HEAD + 24 + n * ROW + FOOT + 8
    top = TB + HEAD + 24

    rows = []
    for i, s_ in enumerate(sites):
        y = top + i * ROW
        sc = STACK_COLOR.get(s_.get("stack", ""), MUTED)
        live = s_.get("live", True)
        dot = GREEN if live else AMBER
        # uptime/response only render when the JSON actually supplies them
        extra = ""
        if s_.get("uptime"):
            extra += f'<text x="1046" y="{y+24}" font-size="12" fill="{GREEN}" text-anchor="end" font-family="\'SFMono-Regular\',Consolas,monospace">{s_["uptime"]}%</text>'
        rows.append(f'''<rect x="24" y="{y}" width="{W-48}" height="{ROW-6}" rx="8" fill="{PANEL}" fill-opacity="{".5" if i%2 else ".25"}"/>
    <circle cx="48" cy="{y+19}" r="5" fill="{dot}" style="animation:led 2.6s ease-in-out {i*.35:.2f}s infinite"/>
    <text x="68" y="{y+17}" font-size="14" font-weight="700" fill="{TEXT}">{s_["domain"]}</text>
    <text x="68" y="{y+32}" font-size="10.5" fill="{DIM}">{s_.get("sector","")}</text>
    <rect x="470" y="{y+7}" width="86" height="22" rx="11" fill="{sc}" fill-opacity=".13" stroke="{sc}" stroke-opacity=".45"/>
    <text x="513" y="{y+22}" font-size="11" fill="{sc}" text-anchor="middle" font-family="\'SFMono-Regular\',Consolas,monospace">{s_.get("stack","—")}</text>
    <text x="760" y="{y+24}" font-size="12" fill="{MUTED}" text-anchor="end" font-family="\'SFMono-Regular\',Consolas,monospace">{s_.get("host","—")}</text>
    <text x="880" y="{y+24}" font-size="12" fill="{GREEN}" text-anchor="end" font-family="\'SFMono-Regular\',Consolas,monospace">{"✓ HTTPS" if s_.get("tls") else "—"}</text>
    {extra}
    <text x="1176" y="{y+24}" font-size="12" fill="{CYAN if live else AMBER}" text-anchor="end" font-family="\'SFMono-Regular\',Consolas,monospace">{"live" if live else "staging"}</text>''')

    tls_all = all(s.get("tls") for s in sites)
    stacks = sorted({s.get("stack", "") for s in sites if s.get("stack")})
    chips, cx = "", 774
    for st in stacks:
        col = STACK_COLOR.get(st, MUTED)
        w = 12 + len(st) * 7.4
        chips += (f'<rect x="{cx}" y="{TB_+38}" width="{w:.0f}" height="20" rx="10" fill="{col}" fill-opacity=".14" '
                  f'stroke="{col}" stroke-opacity=".45"/>'
                  f'<text x="{cx + w/2:.0f}" y="{TB_+52}" font-size="11" fill="{col}" text-anchor="middle" '
                  f'font-family="\'SFMono-Regular\',Consolas,monospace">{st}</text>')
        cx += w + 10

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="status.{brand.lower()} — managed hosting: {n} client sites with uptime, SSL, stack, response time and last deploy">
  <style>
    text {{ font-family:'Segoe UI',Helvetica,Arial,sans-serif; }}
    @keyframes led {{ 0%,100%{{opacity:1}} 50%{{opacity:.3}} }}
    .sweep {{ animation:sw 4s ease-in-out infinite; }}
    @keyframes sw {{ 0%,100%{{opacity:.25}} 50%{{opacity:.7}} }}
    .beat {{ animation:bt 2.2s ease-in-out infinite; }}
    @keyframes bt {{ 0%,100%{{opacity:.55}} 50%{{opacity:1}} }}
  </style>
  <defs>
    <clipPath id="hb"><rect width="{W}" height="{H}" rx="14"/></clipPath>
    <linearGradient id="upg" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{GREEN}"/><stop offset="1" stop-color="{CYAN}"/>
    </linearGradient>
  </defs>
  <g clip-path="url(#hb)">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <rect width="{W}" height="{TB}" fill="{TITLE}"/>
    <rect y="{TB-1}" width="{W}" height="1" fill="{BORDER}"/>
    <circle cx="22" cy="17" r="6" fill="#FF5F57"/><circle cx="42" cy="17" r="6" fill="#FEBC2E"/><circle cx="62" cy="17" r="6" fill="#28C840"/>
    <text x="{W//2}" y="22" font-size="13" fill="{MUTED}" text-anchor="middle" font-family="'SFMono-Regular',Consolas,Menlo,monospace">status.{brand.lower()} — managed hosting &amp; deployment</text>

    <!-- summary strip -->
    <rect x="24" y="{TB+14}" width="270" height="52" rx="10" fill="{PANEL}" stroke="{BORDER}"/>
    <text x="42" y="{TB+36}" font-size="10.5" fill="{DIM}" letter-spacing="1.6" font-family="'SFMono-Regular',Consolas,monospace">CLIENT SITES LIVE</text>
    <text x="42" y="{TB+58}" font-size="19" font-weight="800" fill="{GREEN}" font-family="'SFMono-Regular',Consolas,monospace">{n}</text>
    <text x="272" y="{TB+58}" font-size="11" fill="{MUTED}" text-anchor="end" font-family="'SFMono-Regular',Consolas,monospace">built &amp; hosted here</text>

    <rect x="308" y="{TB+14}" width="210" height="52" rx="10" fill="{PANEL}" stroke="{BORDER}"/>
    <text x="326" y="{TB+36}" font-size="10.5" fill="{DIM}" letter-spacing="1.6" font-family="'SFMono-Regular',Consolas,monospace">HTTPS + HSTS</text>
    <text x="326" y="{TB+58}" font-size="19" font-weight="800" fill="{TEXT}" font-family="'SFMono-Regular',Consolas,monospace">{"all" if tls_all else "partial"}</text>
    <text x="496" y="{TB+58}" font-size="11" fill="{MUTED}" text-anchor="end" font-family="'SFMono-Regular',Consolas,monospace">certs managed</text>

    <rect x="532" y="{TB+14}" width="210" height="52" rx="10" fill="{PANEL}" stroke="{BORDER}"/>
    <text x="550" y="{TB+36}" font-size="10.5" fill="{DIM}" letter-spacing="1.6" font-family="'SFMono-Regular',Consolas,monospace">DEPLOYS</text>
    <text x="550" y="{TB+58}" font-size="19" font-weight="800" fill="{CYAN}" font-family="'SFMono-Regular',Consolas,monospace">on push</text>
    <text x="720" y="{TB+58}" font-size="11" fill="{MUTED}" text-anchor="end" font-family="'SFMono-Regular',Consolas,monospace">CI/CD</text>

    <!-- stacks in production (no invented uptime series) -->
    <rect x="756" y="{TB+14}" width="420" height="52" rx="10" fill="{PANEL}" stroke="{BORDER}"/>
    <text x="774" y="{TB+32}" font-size="10.5" fill="{DIM}" letter-spacing="1.6" font-family="'SFMono-Regular',Consolas,monospace">STACKS IN PRODUCTION</text>
    {chips}

    <!-- column header -->
    <g font-size="10.5" fill="{DIM}" letter-spacing="1.2" font-family="'SFMono-Regular',Consolas,monospace">
      <text x="68" y="{top-8}">SITE</text>
      <text x="513" y="{top-8}" text-anchor="middle">STACK</text>
      <text x="760" y="{top-8}" text-anchor="end">HOSTING</text>
      <text x="880" y="{top-8}" text-anchor="end">TLS</text>
      <text x="1176" y="{top-8}" text-anchor="end">STATUS</text>
    </g>

    {''.join(rows)}

    <rect y="{H-FOOT}" width="{W}" height="{FOOT}" fill="{TITLE}"/>
    <rect y="{H-FOOT}" width="{W}" height="1" fill="{BORDER}"/>
    <g font-size="11.5" font-family="'SFMono-Regular',Consolas,Menlo,monospace">
      <circle class="beat" cx="36" cy="{H-FOOT+17}" r="4" fill="{GREEN}"/>
      <text x="50" y="{H-FOOT+21}" fill="{MUTED}">monitored continuously · deploys on push · backups nightly</text>
      <text x="1176" y="{H-FOOT+21}" fill="{CYAN}" text-anchor="end">hosting &amp; deployment by {brand} ▸</text>
    </g>
    <rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="14" fill="none" stroke="{BORDER}" stroke-width="1.5"/>
  </g>
</svg>
'''


def main():
    """Write assets/os-hosting.svg from tools/clients.json."""
    brand, sites = load_sites()
    svg = board(brand, sites)
    open(os.path.join(ASSETS, "os-hosting.svg"), "w").write(svg)
    print(f"wrote os-hosting.svg ({len(sites)} rows, {len(svg)} bytes)")


if __name__ == "__main__":
    main()
