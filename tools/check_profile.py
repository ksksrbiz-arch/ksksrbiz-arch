#!/usr/bin/env python3
"""Offline profile checks. Run: python3 tools/check_profile.py"""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from gen_status_board import board

ROOT = Path(__file__).resolve().parents[1]
for asset in (ROOT / 'assets').glob('*.svg'):
    ET.parse(asset)
readme = (ROOT / 'README.md').read_text()
local_sources = re.findall(r'(?:src|srcset)="(\./assets/[^"]+)"', readme)
assert local_sources, 'README must include local artwork'
for source in local_sources:
    assert (ROOT / source.split('?')[0]).is_file(), f'Missing image: {source}'
assert './assets/os-identity-mobile.svg' in local_sources
assert './assets/project-atlas-mobile.svg' in local_sources
assert 'raw.githubusercontent.com/ksksrbiz-arch/ksksrbiz-arch/main/assets' not in readme
assert 'https://1commerce.online' not in readme
assert '[Website](https://1commercesolutions.com)' in readme
assert '[Shop](https://shop.1commercesolutions.com)' in readme
assert 'https://1commerce.shop' not in readme
assert 'mailto:skdev@1commerce.online' in readme
for target in re.findall(r'\]\((\./[^)#]+)', readme):
    assert (ROOT / target).exists(), f'Missing local link: {target}'
# Generated replays must have valid SMIL timing and actual static alternatives.
animated_studies = list((ROOT / 'assets').glob('lab-study-*.svg'))
animated_studies += [ROOT / 'assets' / f'project-atlas-{name}.svg'
                     for name in ('feature', 'mobile', 'journeys', 'spoilers')]
for asset in animated_studies:
    root = ET.parse(asset).getroot()
    assert any(node.get('class') == 'motion' for node in root.iter())
    assert any(node.get('class') == 'still' for node in root.iter())
    assert 'prefers-reduced-motion' in asset.read_text()
    for node in root.iter():
        if 'keyTimes' in node.attrib:
            times = [float(t) for t in node.get('keyTimes').split(';')]
            assert times[0] == 0 and times[-1] == 1 and times == sorted(times)
            values = node.get('values', node.get('keyPoints', '')).split(';')
            assert len(values) == len(times), f'Invalid animation timing: {asset}'
# Regression: client content is data, including ampersands and quotes.
sample = {'domain': 'a&b.example', 'sector': 'Windows & trim <contractor>',
          'stack': 'A&B', 'host': '"Cloud" & edge', 'tls': True, 'live': True,
          'uptime': '99&100'}
root = ET.fromstring(board('A&B "studio"', [sample]))
assert sample['sector'] in ''.join(root.itertext())
assert readme.count('<details>') == readme.count('</details>')
print('PASS: SVGs, local images/links, marketing URL, research and Atlas timing/static alternatives, disclosures, and client-data escaping.')
