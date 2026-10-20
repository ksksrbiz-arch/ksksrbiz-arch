# Profile audit — 2026-10-20

## Repaired

- `assets/os-hosting.svg` was invalid XML: ClearView's sector contained a raw ampersand. Escaped all client-supplied text and brand values in the generator, then regenerated the board.
- Removed the HSTS claim: the input only records TLS, which does not establish HSTS.
- Replaced invalid `height="170em"` HTML sizing with a numeric image width.
- Added real social links outside the contact image. The image's apparent buttons all previously led to email.
- Added an offline regression check for SVG parsing, image paths, disclosure balance and generator escaping.

## Presentation

- Kept the animated OS theme, artwork and experiments.
- Added a visible name, short introduction, contact link and section navigation.
- Changed four squeezed client cards to 380px cards that can wrap, with native text links below. GitHub's max-width image styling can shrink a card to its container.
- Made the terminal and activity panels wrap rather than shrink to tiny percentage columns.
- Grouped hosting and delivery panels in a disclosure to shorten the main project showcase.
- Improved muted text contrast in the hosting board.
- Labeled animated platform previews as illustrative sample data and the hosting board as a manually maintained snapshot.
- Replaced the streak and follower image embeds with outbound links after automated requests returned 403. This is an availability finding from this environment, not proof of a permanent outage.

## Verification and limits

`python3 tools/check_profile.py` and `git diff --check` pass. All 30 committed SVG assets parse. The regenerated hosting board was rasterized and visually inspected.

The GitHub stats endpoint returned a valid stats SVG. The Atlas, Precision Core Builders, Montucky Moonshine and both featured platform repository links returned HTTP 200. Automated requests to 1commerce.online, To Be Read and ClearView returned 403; those links were retained. Other destinations have not all been independently verified.

A full GitHub browser/mobile rendering and animation playback check was not completed: the local Playwright browser executable was unavailable. Static asset rendering and source validation do not substitute for that check.

No GitHub Actions were run or added. The existing manual-only workflow was left unchanged. Hosting metadata and the repository index remain manually generated snapshots; they should not be treated as live monitoring.
