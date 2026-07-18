#!/usr/bin/env python3
from pathlib import Path
import shutil, sys

PATH = Path('index.html')
MARKER = '[iop-not-wild-dunes-v1]'
if not PATH.exists():
    sys.exit('ERROR: index.html not found; run from golfcart-booking root')
src = PATH.read_text(encoding='utf-8')
if MARKER in src:
    print('SKIP: Isle of Palms / Wild Dunes notice already applied')
    sys.exit(0)

def rep(old, new, label):
    global src
    n = src.count(old)
    if n != 1:
        sys.exit(f'ANCHOR ERROR [{label}]: expected 1 match, found {n}')
    src = src.replace(old, new, 1)
    print(f'  ok: {label}')

rep(
'''      <div class="card-sub">Luxury LSV rentals delivered to your door across the Charleston area.</div>
''',
'''      <div class="card-sub">Luxury LSV rentals delivered to your door across the Charleston area.</div>
      <div data-marker="iop-not-wild-dunes-v1" style="margin-top:8px;padding:8px 10px;border-radius:8px;background:#fff7df;border:1px solid #f1c75b;color:#775500;font-size:13px;line-height:1.35;">
        <strong>Isle of Palms:</strong> rentals currently exclude Wild Dunes.
      </div>
''',
'add cart-selection Isle of Palms notice')

rep(
'''          <div class="zone-pill" onclick="selectZone('Isle of Palms',79.99,this)">Isle of Palms<br><span class="zone-fee">$79.99 delivery</span></div>
''',
'''          <div class="zone-pill" onclick="selectZone('Isle of Palms',79.99,this)">Isle of Palms<br><span style="font-size:11px;font-weight:700;color:#b35c00;">Not Wild Dunes</span><br><span class="zone-fee">$79.99 delivery</span></div>
''',
'clarify Isle of Palms delivery option')

backup = PATH.with_suffix('.html.bak')
shutil.copy2(PATH, backup)
PATH.write_text(src, encoding='utf-8')
print('DONE: patched index.html')
