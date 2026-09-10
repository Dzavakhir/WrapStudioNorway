#!/usr/bin/env python3
"""Print the brief for one designer group: python3 tools/brief.py g07"""
import json, os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(root, 'codes.json')))
g = sys.argv[1] if len(sys.argv) > 1 else 'g01'
cat = {c['slug']: c for c in d['categories']}
rows = [c for c in d['codes'] if c['group'] == g]
if not rows:
    sys.exit('unknown group ' + g)
print('=== Group %s — category: %s (%s) ===\n' % (g, rows[0]['category_uz'], cat[rows[0]['category']]['name_en']))
print('Category intro (uz):', cat[rows[0]['category']]['intro_uz'], '\n')
for c in rows:
    print('#%03d  @effect(%r)   file: effects/%s.py' % (c['id'], c['code'], g))
    print('   title (uz):  %s — %s' % (c['title_uz'], c['desc_uz']))
    print('   PROMPT (the promise to deliver): %s' % c['prompt_en'])
    print('   hints: %s\n' % c['hint'])
