#!/usr/bin/env python3
"""
gen_repo_windows.py — auto-generate 1COMMERCE OS "directory tile" windows,
one per repository, in the house style of the profile README.

Usage:
    python3 tools/gen_repo_windows.py            # fetch live repo list (or fall back to tools/repos.json)
    GITHUB_TOKEN=... python3 tools/gen_repo_windows.py   # authenticated fetch (higher rate limit)

What it does:
  1. Fetches the public repo list for the profile user (skips forks/archived).
     If the API is unreachable it uses the committed seed in tools/repos.json.
  2. Emits assets/repo-<name>.svg — a compact animated window per repo with a
     deterministic motif (hash of the repo name picks one of six animations),
     language chip, star count when known, and description.
  3. Rewrites the block between REPO-WINDOWS markers in README.md so new
     repos appear on the profile automatically the next time this runs.

No GitHub Actions required: run it locally and commit, or trigger the
manual-only workflow in .github/workflows/regen-repo-windows.yml.
"""
import hashlib, json, os, re, sys, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
README = os.path.join(ROOT, "README.md")
SEED = os.path.join(ROOT, "tools", "repos.json")
RAW = "https://raw.githubusercontent.com/ksksrbiz-arch/ksksrbiz-arch/main/assets"

LANG_COLORS = {
    "JavaScript": "#F7DF1E", "TypeScript": "#3178C6", "Python": "#3776AB",
    "HTML": "#E34C26", "CSS": "#663399", "Shell": "#89E051", "Go": "#00ADD8",
    "Rust": "#DEA584", "SVG": "#FFB13B", "Markdown": "#8C8178",
}

def load_repos():
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
    out = []
    for r in seed.get("extra", []):
        out.append({**r, "owner": r.get("owner", user)})
    for r in repos:
        out.append({**r, "owner": user})
    return user, out

def motif(kind, x):
    """Six deterministic mini-animations, anchored at motif zone origin x (y 32..88)."""
    if kind == 0:  # orbit
        return (f'<circle cx="{x+34}" cy="60" r="17" fill="none" stroke="#7A5B49" stroke-width="1.2" stroke-dasharray="3 4"/>'
                f'<circle cx="{x+34}" cy="60" r="5" fill="#D97757"/>'
                f'<circle r="3" fill="#E8A33D"><animateMotion dur="3.2s" repeatCount="indefinite" '
                f'path="M{x+51} 60 A17 17 0 1 0 {x+17} 60 A17 17 0 1 0 {x+51} 60"/></circle>')
    if kind == 1:  # eq bars
        b = ''
        for i, (bx, d) in enumerate([(x+16, 0), (x+30, .4), (x+44, .8)]):
            b += (f'<rect x="{bx}" y="44" width="9" height="32" rx="2" fill="#D97757" '
                  f'style="transform-box:fill-box;transform-origin:50% 100%;animation:eqb 1.8s ease-in-out {d}s infinite"/>')
        return b
    if kind == 2:  # wave
        return (f'<path d="M{x+8} 60 q8 -14 16 0 t16 0 t16 0" fill="none" stroke="#E8A33D" stroke-width="2" '
                f'stroke-linecap="round" stroke-dasharray="4 5" style="animation:wv 1.2s linear infinite"/>')
    if kind == 3:  # ring pulse
        return (f'<circle cx="{x+34}" cy="60" r="8" fill="#D97757"/>'
                f'<circle cx="{x+34}" cy="60" r="12" fill="none" stroke="#E8A33D" stroke-width="1.6" '
                f'style="transform-box:fill-box;transform-origin:50% 50%;animation:png 2.4s ease-out infinite"/>')
    if kind == 4:  # spark
        return (f'<path d="M{x+34} 42 l5 13 13 5 -13 5 -5 13 -5 -13 -13 -5 13 -5 z" fill="#E8A33D" '
                f'style="transform-box:fill-box;transform-origin:50% 50%;animation:spk 2.6s ease-in-out infinite"/>')
    return (f'<rect x="{x+22}" y="48" width="24" height="24" rx="5" fill="#C25B3C" '
            f'style="transform-box:fill-box;transform-origin:50% 50%;animation:cub 3s ease-in-out infinite"/>')

def tile(r):
    name = r["name"]
    desc = (r.get("description") or "no description — pure vibes")
    if len(desc) > 46: desc = desc[:44].rstrip() + "…"
    lang = r.get("language") or "Code"
    lc = LANG_COLORS.get(lang, "#8C8178")
    stars = r.get("stargazers_count")
    kind = int(hashlib.sha256(name.encode()).hexdigest(), 16) % 6
    title = name if len(name) <= 26 else name[:25] + "…"
    star_txt = f'<text x="356" y="79" font-size="11" fill="#E8A33D" text-anchor="end">★ {stars}</text>' if stars else ''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 110" width="380" height="110" role="img" aria-label="{name}: {desc}">
  <style>
    text {{ font-family:'Segoe UI',Helvetica,Arial,sans-serif; }}
    @keyframes eqb {{ 0%,100% {{transform:scaleY(.3);}} 50% {{transform:scaleY(1);}} }}
    @keyframes wv  {{ to {{stroke-dashoffset:-9;}} }}
    @keyframes png {{ 0% {{opacity:.9;transform:scale(.6);}} 100% {{opacity:0;transform:scale(2);}} }}
    @keyframes spk {{ 0%,100% {{opacity:.4;transform:scale(.8);}} 50% {{opacity:1;transform:scale(1.1);}} }}
    @keyframes cub {{ 0%,100% {{transform:rotate(0deg);}} 50% {{transform:rotate(180deg);}} }}
    .led {{ animation: led 2.2s ease-in-out infinite; }}
    @keyframes led {{ 0%,100% {{opacity:1;}} 50% {{opacity:.3;}} }}
  </style>
  <defs><clipPath id="t"><rect width="380" height="110" rx="10"/></clipPath></defs>
  <g clip-path="url(#t)">
    <rect width="380" height="110" fill="#1E1814"/>
    <rect width="380" height="22" fill="#2A211A"/>
    <rect y="21" width="380" height="1" fill="#3A2E24"/>
    <circle cx="13" cy="11" r="3.5" fill="#FF5F57"/><circle cx="26" cy="11" r="3.5" fill="#FEBC2E"/><circle cx="39" cy="11" r="3.5" fill="#28C840"/>
    <text x="190" y="15" font-size="10" fill="#8C8178" text-anchor="middle" font-family="'SFMono-Regular',Consolas,monospace">~/repos/{name}</text>
    <circle class="led" cx="24" cy="48" r="4" fill="#28C840"/>
    <text x="38" y="53" font-size="15.5" font-weight="800" fill="#F5F0E8">{title}</text>
    <text x="24" y="76" font-size="11.5" fill="#B5AB9F">{desc}</text>
    <circle cx="28" cy="93" r="4" fill="{lc}"/>
    <text x="38" y="97" font-size="11" fill="#8C8178" font-family="'SFMono-Regular',Consolas,monospace">{lang}</text>
    <text x="356" y="97" font-size="11" font-weight="700" fill="#D97757" text-anchor="end">open ▸</text>
    {star_txt}
    {motif(kind, 288)}
    <rect x=".75" y=".75" width="378.5" height="108.5" rx="10" fill="none" stroke="#3A2E24" stroke-width="1.5"/>
  </g>
</svg>
'''

def header_bar(n):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 46" width="1200" height="46" role="img" aria-label="repos.d — auto-indexed directory">
  <style>.c {{ animation: c 1s steps(1,end) infinite; }} @keyframes c {{ 0%,49% {{opacity:1;}} 50%,100% {{opacity:0;}} }}</style>
  <defs><clipPath id="hb"><rect width="1200" height="46" rx="10"/></clipPath></defs>
  <g clip-path="url(#hb)" font-family="'SFMono-Regular',Consolas,Menlo,monospace">
    <rect width="1200" height="46" fill="#1E1814"/>
    <rect y="45" width="1200" height="1" fill="#3A2E24"/>
    <text x="24" y="29" font-size="14" fill="#D97757" font-weight="700">$ ls ~/repos.d <tspan fill="#8C8178" font-weight="400">— auto-indexed by tools/gen_repo_windows.py · {n} entries</tspan><tspan class="c" fill="#E7DFD6">▌</tspan></text>
    <text x="1176" y="29" font-size="12" fill="#8C8178" text-anchor="end">drwxr-xr-x</text>
  </g>
</svg>
'''

def main():
    user, repos = load_repos()
    lines = []
    for i, r in enumerate(repos):
        fn = f"repo-{r['name']}.svg"
        open(os.path.join(ASSETS, fn), "w").write(tile(r))
        print("wrote", fn)
    open(os.path.join(ASSETS, "repos-header.svg"), "w").write(header_bar(len(repos)))
    # README block
    block = ['<p align="center">',
             f'  <img src="{RAW}/repos-header.svg?v=4" alt="repos.d — auto-indexed directory" width="100%">',
             '</p>']
    for i in range(0, len(repos), 3):
        block.append('<p align="center">')
        for r in repos[i:i+3]:
            url = f"https://github.com/{r['owner']}/{r['name']}"
            block.append(f'  <a href="{url}">')
            block.append(f'    <img src="{RAW}/repo-{r["name"]}.svg?v=4" alt="{r["name"]}" width="32.6%">')
            block.append('  </a>')
        block.append('</p>')
    blocktxt = '\n'.join(block)
    md = open(README).read()
    marked = re.search(r'<!-- REPO-WINDOWS:START -->.*?<!-- REPO-WINDOWS:END -->', md, re.S)
    payload = f'<!-- REPO-WINDOWS:START -->\n{blocktxt}\n<!-- REPO-WINDOWS:END -->'
    if marked:
        md = md.replace(marked.group(0), payload)
        open(README, "w").write(md)
        print("README block updated")
    else:
        print("\nNo REPO-WINDOWS markers in README yet — paste this where you want the section:\n")
        print(payload)

if __name__ == "__main__":
    main()
