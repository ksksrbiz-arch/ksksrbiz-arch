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
assert 'raw.githubusercontent.com/ksksrbiz-arch/ksksrbiz-arch/main/assets' not in readme
# Regression: client content is data, including ampersands and quotes.
sample = {'domain': 'a&b.example', 'sector': 'Windows & trim <contractor>',
          'stack': 'A&B', 'host': '"Cloud" & edge', 'tls': True, 'live': True,
          'uptime': '99&100'}
root = ET.fromstring(board('A&B "studio"', [sample]))
assert sample['sector'] in ''.join(root.itertext())
assert readme.count('<details>') == readme.count('</details>')
print('PASS: all SVGs parse, README image and picture sources exist, artwork follows the current branch, disclosure blocks balance, generator escapes client data.')
