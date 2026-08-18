#!/usr/bin/env python3
"""
gen_repo_windows.py — auto-generate the 1COMMERCE OS repo file-manager,
a single full "Files" window listing every repository, in the midnight
theme of the profile README.

Usage:
    python3 tools/gen_repo_windows.py            # fetch live repo list (or fall back to tools/repos.json)
    GITHUB_TOKEN=... python3 tools/gen_repo_windows.py   # authenticated fetch (higher rate limit)

What it does:
  1. Fetches the public repo list for the profile user (skips forks/archived).
     If the API is unreachable it uses the committed seed in tools/repos.json.
  2. Emits assets/repos-fm.svg — one file-manager window: title bar, toolbar
     with path crumbs + search box, sidebar with smart folders, one animated
     row per repo (language icon chip, description, meta, pulsing LED), and
     a status bar. Window height scales with the repo count.
  3. Rewrites the block between REPO-WINDOWS markers in README.md so new
     repos appear on the profile automatically the next time this runs.

No GitHub Actions required: run it locally and commit, or trigger the
manual-only workflow in .github/workflows/regen-repo-windows.yml.
"""
import json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
README = os.path.join(ROOT, "README.md")
SEED = os.path.join(ROOT, "tools", "repos.json")
RAW = "https://raw.githubusercontent.com/ksksrbiz-arch/ksksrbiz-arch/main/assets"

# midnight theme
BG, PANEL, TITLE, BORDER, SIDE = "#0F131B", "#161C26", "#1B2230", "#2B3648", "#121826"
TEXT, MUTED, DIM = "#F1F5FB", "#7C8798", "#4C5870"
CYAN, VIOLET, AMBER, GREEN, CORAL = "#4FD1C5", "#B794F6", "#F6AD55", "#68D391", "#FF8B6A"

LANG = {
    "JavaScript": ("#F6E05E", "JS"), "TypeScript": ("#63B3ED", "TS"),
    "Python": ("#63B3ED", "PY"), "HTML": ("#FC8181", "‹›"),
    "CSS": ("#B794F6", "{}"), "Shell": ("#68D391", "$_"),
    "SVG": (AMBER, "◠"), "Markdown": (MUTED, "M↓"),
}

def load_repos():
    """Return (user, repos) for the profile.

    Tries the live GitHub API first (authenticated via GITHUB_TOKEN when set),
    skipping forks and archived repos. Falls back to the committed seed list in
    tools/repos.json when the API is unreachable, so the generator still works
    offline. Entries from the seed's "extra" list (repos owned by someone else)
    are prepended, each tagged with its owner.
    """
    seed = json.load(open(SEED))
    user = seed["user"]
    repos = None
    try:
        req = urllib.request.Request(
            f"https://api.github.com/users/{user}/repos?per_page=100&sort=updated",
            headers={"Accept": "application/vnd.github+json",
                     **({"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"} if os.environ.get("GITHUB_TOKEN") else {})})
        data = json.load(urllib.request.urlopen(req, timeout=15))
        if isinstance(data, list):
            repos = [{"name": r["name"], "description": r.get("description"),
                      "language": r.get("language"), "stargazers_count": r.get("stargazers_count")}
                     for r in data if not r.get("fork") and not r.get("archived")]
            print(f"fetched {len(repos)} live repos for {user}")
    except Exception as e:
        print(f"live fetch unavailable ({e.__class__.__name__}); using seed list", file=sys.stderr)
    if repos is None:
        repos = seed["repos"]
    out = [{**r, "owner": r.get("owner", user)} for r in seed.get("extra", [])]
    out += [{**r, "owner": user} for r in repos]
    return user, out

def fm_window(user, repos):
    """Render the ~/repos file-manager window as a standalone SVG string.

    Lays out a title bar, a toolbar with path crumbs and a search field, a
    sidebar of smart folders (one per language, counted from `repos`), one row
    per repo, and a status bar. Window height scales with the repo count, so
    the caller never has to size it.
    """
    W = 1200
    TB, TOOL, HDR, ROW, FOOT = 34, 46, 26, 52, 32
    n = len(repos)
    H = TB + TOOL + HDR + n * ROW + FOOT + 2
    SB = 210                          # sidebar width
    top = TB + TOOL + HDR
    langs = {}
    for r in repos:
        langs[r.get("language") or "Code"] = langs.get(r.get("language") or "Code", 0) + 1

    rows = []
    for i, r in enumerate(repos):
        y = top + i * ROW
        name = r["name"]
        desc = (r.get("description") or "no description — pure vibes")
        if len(desc) > 74: desc = desc[:72].rstrip() + "…"
        lang = r.get("language") or "Code"
        lc, glyph = LANG.get(lang, (MUTED, "··"))
        stars = r.get("stargazers_count")
        star_txt = f'<text x="{W-160}" y="{y+32}" font-size="12" fill="{AMBER}" text-anchor="end">★ {stars}</text>' if stars else ''
        selected = (name == "ksksrbiz-arch")
        sel = (f'<rect x="{SB+8}" y="{y+3}" width="{W-SB-20}" height="{ROW-6}" rx="8" '
               f'fill="{VIOLET}" fill-opacity=".12" stroke="{VIOLET}" stroke-opacity=".55"/>') if selected else (
              f'<rect x="{SB+8}" y="{y+3}" width="{W-SB-20}" height="{ROW-6}" rx="8" fill="{PANEL}" fill-opacity="{".55" if i%2 else ".25"}"/>')
        rows.append(f'''{sel}
    <rect x="{SB+22}" y="{y+11}" width="30" height="30" rx="8" fill="{lc}" fill-opacity=".16" stroke="{lc}" stroke-opacity=".6"/>
    <text x="{SB+37}" y="{y+31}" font-size="12" font-weight="800" fill="{lc}" text-anchor="middle" font-family="'SFMono-Regular',Consolas,monospace">{glyph}</text>
    <circle cx="{SB+70}" cy="{y+26}" r="3.5" fill="{GREEN}" style="animation:led 2.4s ease-in-out {i*.3:.1f}s infinite"/>
    <text x="{SB+84}" y="{y+23}" font-size="14.5" font-weight="700" fill="{TEXT}">{name}</text>
    <text x="{SB+84}" y="{y+40}" font-size="11.5" fill="{MUTED}">{desc}</text>
    <text x="{W-64}" y="{y+23}" font-size="11" fill="{DIM}" text-anchor="end" font-family="'SFMono-Regular',Consolas,monospace">{lang.lower()}</text>
    <text x="{W-64}" y="{y+40}" font-size="11" fill="{DIM}" text-anchor="end" font-family="'SFMono-Regular',Consolas,monospace">dir ▸</text>
    {star_txt}''')

    side_langs = []
    for j, (lg, cnt) in enumerate(sorted(langs.items(), key=lambda kv: -kv[1])):
        lc, _ = LANG.get(lg, (MUTED, ""))
        yy = TB + TOOL + 74 + j * 24
        side_langs.append(f'<circle cx="34" cy="{yy-4}" r="4" fill="{lc}"/>'
                          f'<text x="48" y="{yy}" font-size="12" fill="{MUTED}">{lg.lower()}</text>'
                          f'<text x="{SB-24}" y="{yy}" font-size="11" fill="{DIM}" text-anchor="end">{cnt}</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Files — ~/repos: every repository, auto-indexed">
  <style>
    text {{ font-family:'Segoe UI',Helvetica,Arial,sans-serif; }}
    @keyframes led {{ 0%,100% {{opacity:1;}} 50% {{opacity:.25;}} }}
    .scaret {{ animation: blink 1.1s steps(1,end) infinite; }}
    @keyframes blink {{ 0%,49% {{opacity:1;}} 50%,100% {{opacity:0;}} }}
    .sync {{ animation: spin 5s linear infinite; transform-box: fill-box; transform-origin: 50% 50%; }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
  </style>
  <defs><clipPath id="fm"><rect width="{W}" height="{H}" rx="14"/></clipPath></defs>
  <g clip-path="url(#fm)">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <!-- title bar -->
    <rect width="{W}" height="{TB}" fill="{TITLE}"/>
    <rect y="{TB-1}" width="{W}" height="1" fill="{BORDER}"/>
    <circle cx="22" cy="{TB//2}" r="6" fill="#FF5F57"/><circle cx="42" cy="{TB//2}" r="6" fill="#FEBC2E"/><circle cx="62" cy="{TB//2}" r="6" fill="#28C840"/>
    <text x="{W//2}" y="{TB//2+5}" font-size="13" fill="{MUTED}" text-anchor="middle" font-family="'SFMono-Regular',Consolas,Menlo,monospace">Files — ~/repos · {user}</text>
    <!-- toolbar -->
    <rect y="{TB}" width="{W}" height="{TOOL}" fill="{PANEL}"/>
    <rect y="{TB+TOOL-1}" width="{W}" height="1" fill="{BORDER}"/>
    <g font-size="15" fill="{MUTED}">
      <text x="{SB+16}" y="{TB+30}">‹</text><text x="{SB+40}" y="{TB+30}">›</text>
    </g>
    <rect x="{SB+64}" y="{TB+9}" width="300" height="28" rx="8" fill="{BG}" stroke="{BORDER}"/>
    <text x="{SB+80}" y="{TB+28}" font-size="12.5" fill="{TEXT}" font-family="'SFMono-Regular',Consolas,Menlo,monospace"><tspan fill="{CYAN}">🏠</tspan> home <tspan fill="{DIM}">›</tspan> <tspan fill="{CYAN}" font-weight="700">repos</tspan></text>
    <rect x="{W-320}" y="{TB+9}" width="296" height="28" rx="14" fill="{BG}" stroke="{BORDER}"/>
    <text x="{W-300}" y="{TB+28}" font-size="12.5" fill="{DIM}" font-family="'SFMono-Regular',Consolas,Menlo,monospace">⌕ search {n} repos<tspan class="scaret" fill="{CYAN}">▌</tspan></text>
    <!-- sidebar -->
    <rect y="{TB+TOOL}" width="{SB}" height="{H-TB-TOOL}" fill="{SIDE}"/>
    <rect x="{SB-1}" y="{TB+TOOL}" width="1" height="{H-TB-TOOL}" fill="{BORDER}"/>
    <g font-family="'SFMono-Regular',Consolas,Menlo,monospace">
      <text x="22" y="{TB+TOOL+30}" font-size="10.5" fill="{DIM}" letter-spacing="2">SMART FOLDERS</text>
      <text x="22" y="{TB+TOOL+52}" font-size="12.5" fill="{CYAN}" font-weight="700">▸ all repos <tspan fill="{DIM}">({n})</tspan></text>
      {''.join(side_langs)}
      <text x="22" y="{H-FOOT-46}" font-size="10.5" fill="{DIM}" letter-spacing="2">LOCATIONS</text>
      <text x="22" y="{H-FOOT-24}" font-size="12" fill="{MUTED}">☁ 1commerce.online</text>
    </g>
    <!-- column header -->
    <g font-size="10.5" fill="{DIM}" font-family="'SFMono-Regular',Consolas,Menlo,monospace" letter-spacing="1">
      <text x="{SB+84}" y="{TB+TOOL+18}">NAME</text>
      <text x="{W-64}" y="{TB+TOOL+18}" text-anchor="end">KIND</text>
    </g>
    <!-- rows -->
    {''.join(rows)}
    <!-- status bar -->
    <rect y="{H-FOOT}" width="{W}" height="{FOOT}" fill="{TITLE}"/>
    <rect y="{H-FOOT}" width="{W}" height="1" fill="{BORDER}"/>
    <g font-size="11.5" fill="{MUTED}" font-family="'SFMono-Regular',Consolas,Menlo,monospace">
      <g class="sync" stroke="{DIM}" stroke-width="1.4" fill="none">
        <path d="M26 {H-FOOT+10} a6 6 0 1 1 -3.5 10.5" stroke-linecap="round"/>
      </g>
      <text x="42" y="{H-FOOT+21}">{n} items · 1 selected · indexed by tools/gen_repo_windows.py</text>
      <text x="{W-24}" y="{H-FOOT+21}" text-anchor="end" fill="{CYAN}">click anywhere to browse on GitHub ▸</text>
    </g>
    <rect x=".75" y=".75" width="{W-1.5}" height="{H-1.5}" rx="14" fill="none" stroke="{BORDER}" stroke-width="1.5"/>
  </g>
</svg>
'''

def main():
    """Write assets/repos-fm.svg and refresh the README's REPO-WINDOWS block.

    The README block is emitted as a single line with no whitespace between
    tags: newlines between inline <img>/<a> tags render as spaces on GitHub and
    would make percentage-width rows wrap on narrow screens.
    """
    user, repos = load_repos()
    svg = fm_window(user, repos)
    open(os.path.join(ASSETS, "repos-fm.svg"), "w").write(svg)
    print(f"wrote repos-fm.svg ({len(repos)} rows, {len(svg)} bytes)")
    # README block — single-line, whitespace-free (mobile-safe)
    payload = ('<!-- REPO-WINDOWS:START -->\n'
               f'<p align="center"><a href="https://github.com/{user}?tab=repositories">'
               f'<img src="{RAW}/repos-fm.svg?v=10" alt="Files — ~/repos: every repository auto-indexed in one file-manager window" width="100%"></a></p>\n'
               '<!-- REPO-WINDOWS:END -->')
    md = open(README).read()
    marked = re.search(r'<!-- REPO-WINDOWS:START -->.*?<!-- REPO-WINDOWS:END -->', md, re.S)
    if marked:
        open(README, "w").write(md.replace(marked.group(0), payload))
        print("README block updated")
    else:
        print("\nNo REPO-WINDOWS markers in README — paste manually:\n" + payload)

if __name__ == "__main__":
    main()
