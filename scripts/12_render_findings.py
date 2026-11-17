#!/usr/bin/env python3
"""Render FINDINGS.md from docs/FINDINGS.template.md by inserting the generated tables."""
import re
tables = {}
for f in ('results/tables.md', 'results/tables_features.md', 'results/tables_stats.md'):
    for block in re.split(r'\n(?=### T)', '\n' + open(f).read()):
        m = re.match(r'\s*### (T\w+)\. (.*)', block)
        if m: tables[m.group(1)] = '**Table ' + m.group(1) + '. ' + m.group(2).strip() + '**\n\n' + block.split('\n', 2)[2].rstrip() if block.strip().count('\n') > 1 else ''
text = open('docs/FINDINGS.template.md').read()
missing = [k for k in re.findall(r'\{\{(T\w+)\}\}', text) if k not in tables]
assert not missing, missing
open('FINDINGS.md', 'w').write(re.sub(r'\{\{(T\w+)\}\}', lambda m: tables[m.group(1)], text))
print('FINDINGS.md written;', len(tables), 'tables available')
