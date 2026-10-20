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
for asset in re.findall(r'/assets/([^?"\s]+)\?', readme):
    assert (ROOT / 'assets' / asset).is_file(), f'Missing image: {asset}'
# Regression: client content is data, including ampersands and quotes.
sample = {'domain': 'a&b.example', 'sector': 'Windows & trim <contractor>',
          'stack': 'A&B', 'host': '"Cloud" & edge', 'tls': True, 'live': True,
          'uptime': '99&100'}
root = ET.fromstring(board('A&B "studio"', [sample]))
assert sample['sector'] in ''.join(root.itertext())
assert readme.count('<details>') == readme.count('</details>')
print('PASS: all SVGs parse, README image paths exist, disclosure blocks balance, generator escapes client data.')
