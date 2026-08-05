#!/usr/bin/env python3
"""GolfCart.Fun Public Booking Patch 3.9E.5.17.3 — Calendar visual polish.

Booking repo only. Run from /workspaces/golfcart-booking on its deploy
branch at PUBLIC_BOOKING_VERSION 3.9E.5.17.2 (index.html sha256
79a13b37c8c7...). Bumps the public version to 3.9E.5.17.3 in LOCKSTEP
across index.html, buildIdentity39E5172.js, and the three test suites
that pin it (that lockstep is what the identity test exists to enforce).

Visual-only refinement of the arrival-date calendar: pastel tier
backgrounds become a thin colored accent bar with tier-tinted prices on
clean white cells; a subtle dot marks today; the selected day gets a
solid brand fill with a crisp focus ring; disabled days read quietly;
typography is tightened (tabular numerals, letterspaced weekday row,
divider under month titles); legend swatches match the new bars.

ZERO functional change: same classes, handlers, pricing math, tier
thresholds, checkout state, and waiver flow. The only script edit adds a
display-only .today class. All four test suites pass after applying.

Usage
  python3 patch39e5173_public_calendar_polish.py --check
  python3 patch39e5173_public_calendar_polish.py
"""
import hashlib, sys
from pathlib import Path

MARK = "[patch39e5173-calendar-polish-v1]"
IDX = Path("index.html")
EXPECTED = "79a13b37c8c7a623d39f5975630042c00a32022d0dd2ad0fe83b114f698cd726"
OLD_LIT, NEW_LIT = "3.9E.5.17.2", "3.9E.5.17.3"
OLD_ESC, NEW_ESC = "3\\.9E\\.5\\.17\\.2", "3\\.9E\\.5\\.17\\.3"
CHECK_ONLY = "--check" in sys.argv[1:]

IDX_EDITS = [('month card', '  .calendar-month { min-width:0; border:1px solid #d7e8f1; border-radius:17px; background:rgba(255,255,255,.94); padding:13px; overflow:hidden; box-shadow:0 7px 20px rgba(13,71,108,.055); }', '  .calendar-month { min-width:0; border:1px solid #e0ecf3; border-radius:16px; background:#fff; padding:14px; overflow:hidden; box-shadow:0 4px 14px rgba(13,71,108,.05); } /* [patch39e5173-calendar-polish-v1] */'), ('month title', "  .calendar-month-title { text-align:center; font-family:'Nunito',sans-serif; font-weight:900; color:var(--brand-deep); margin:2px 0 11px; font-size:17px; }", "  .calendar-month-title { text-align:center; font-family:'Nunito',sans-serif; font-weight:900; color:var(--brand-deep); margin:2px 0 10px; padding-bottom:9px; border-bottom:1px solid #ecf3f8; font-size:16px; letter-spacing:.2px; }"), ('weekday header', '  .calendar-weekday { min-width:0; text-align:center; font-size:9px; font-weight:900; color:#7790a2; padding:3px 0 6px; text-transform:uppercase; letter-spacing:.3px; }', '  .calendar-weekday { min-width:0; text-align:center; font-size:8.5px; font-weight:900; color:#93aaba; padding:3px 0 7px; text-transform:uppercase; letter-spacing:.6px; }'), ('day cell base', '  .calendar-day { appearance:none; width:100%; min-width:0; min-height:62px; box-sizing:border-box; border:1px solid #d8e7ef; background:#fff; border-radius:12px; cursor:pointer; padding:7px 5px 6px; text-align:left; color:var(--text); transition:.15s ease; overflow:hidden; box-shadow:0 2px 5px rgba(13,71,108,.035); }', "  .calendar-day { appearance:none; position:relative; width:100%; min-width:0; min-height:62px; box-sizing:border-box; border:1px solid #e3edf3; background:#fff; border-radius:10px; cursor:pointer; padding:12px 6px 7px; text-align:left; color:var(--text); transition:border-color .15s ease, box-shadow .15s ease, transform .15s ease; overflow:hidden; box-shadow:0 1px 3px rgba(13,71,108,.04); }\n  .calendar-day::before { content:''; position:absolute; top:6px; left:7px; right:7px; height:3px; border-radius:2px; background:transparent; }\n  .calendar-day.price-tier-low::before { background:#31c186; } .calendar-day.price-tier-mid::before { background:#f0b43e; } .calendar-day.price-tier-high::before { background:#ef6f6a; }\n  .calendar-day.price-tier-low .calendar-price { color:#137a4d; } .calendar-day.price-tier-mid .calendar-price { color:#96690f; } .calendar-day.price-tier-high .calendar-price { color:#bf403c; }\n  .calendar-day.today { border-color:#9fd1ee; }\n  .calendar-day.today .calendar-date-num::after { content:''; display:inline-block; width:4px; height:4px; border-radius:50%; background:#0277bd; margin-left:4px; vertical-align:2px; }"), ('day hover', '  .calendar-day:hover { border-color:#29b6f6; transform:translateY(-2px); box-shadow:0 8px 18px rgba(2,136,209,.16); }', '  .calendar-day:hover { border-color:#29b6f6; transform:translateY(-1px); box-shadow:0 6px 14px rgba(2,136,209,.13); }'), ('selected state', '  .calendar-day.selected { border:2px solid #fff; outline:3px solid rgba(2,136,209,.34); background:linear-gradient(145deg,#16a8eb,#0277bd) !important; color:#fff; box-shadow:0 9px 20px rgba(2,119,189,.28); transform:translateY(-1px); }', '  .calendar-day.selected { border-color:transparent; background:#0277bd !important; color:#fff; box-shadow:0 0 0 3px rgba(2,119,189,.22), 0 8px 18px rgba(2,119,189,.26); transform:translateY(-1px); }\\n  .calendar-day.selected::before { background:rgba(255,255,255,.55) !important; }'), ('disabled state', '  .calendar-day.disabled { opacity:.42; cursor:not-allowed; background:#f1f5f7 !important; box-shadow:none; transform:none; }', '  .calendar-day.disabled { opacity:1; cursor:not-allowed; background:#f7fafc !important; border-color:#e8f0f5; color:#a7bcc9; box-shadow:none; transform:none; }\\n  .calendar-day.disabled::before { display:none; } .calendar-day.disabled .calendar-price { color:#b7c8d3; }'), ('date number', '  .calendar-date-num { display:block; font-weight:950; font-size:14px; line-height:1; }', '  .calendar-date-num { display:block; font-weight:900; font-size:15px; line-height:1; color:#12354c; font-variant-numeric:tabular-nums; }\\n  .calendar-day.selected .calendar-date-num { color:#fff; }'), ('price text', '  .calendar-price { display:block; font-size:10px; line-height:1.15; margin-top:9px; font-weight:900; white-space:nowrap; color:#173a50; letter-spacing:-.15px; }', '  .calendar-price { display:block; font-size:10px; line-height:1.15; margin-top:8px; font-weight:800; white-space:nowrap; color:#3d5a6e; letter-spacing:0; font-variant-numeric:tabular-nums; }'), ('tier fills become legend chips only', '  .price-tier-low { background:linear-gradient(145deg,#effdf4,#dcfce7); } .price-tier-mid { background:linear-gradient(145deg,#fffaf0,#fef3c7); } .price-tier-high { background:linear-gradient(145deg,#fff6f6,#fee2e2); }', '  .calendar-legend .price-tier-low { background:#31c186; } .calendar-legend .price-tier-mid { background:#f0b43e; } .calendar-legend .price-tier-high { background:#ef6f6a; }\\n  .calendar-legend i { border:none; height:5px; width:14px; border-radius:3px; }'), ('today class in renderer', "if(iso===state.start_date)btn.classList.add('selected');", "if(iso===state.start_date)btn.classList.add('selected');if(iso===localISODate(new Date()))btn.classList.add('today');")]
VERSION_FILES = {'index.html': {'lit': 3, 'esc': 0}, 'buildIdentity39E5172.js': {'lit': 1, 'esc': 0}, 'test_build_identity_39e5172.mjs': {'lit': 2, 'esc': 4}, 'test_checkout_state_integrity_39e5171.mjs': {'lit': 0, 'esc': 1}, 'test_public_pricing_contract_39e517.mjs': {'lit': 0, 'esc': 1}}

def fail(m): sys.exit("ABORT: " + m + " No files were changed.")
for name in VERSION_FILES:
    if not Path(name).exists(): fail("missing " + name + " — run from the golfcart-booking repository root.")
text = IDX.read_text(encoding="utf-8")
if MARK in text:
    print("SKIP: Patch 3.9E.5.17.3 is already applied."); sys.exit(0)
act = hashlib.sha256(IDX.read_bytes()).hexdigest()
if act != EXPECTED:
    print("WARNING: index.html sha256 " + act[:12] + "... differs from the audited 3.9E.5.17.2 baseline.")
    print("         Exact anchor validation below still protects every change.")
problems = []
for label, old, new in IDX_EDITS:
    c = text.count(old)
    if c != 1: problems.append("  index.html [" + label + "]: expected 1 match, found " + str(c))
contents = {}
for name, expect in VERSION_FILES.items():
    src = Path(name).read_text(encoding="utf-8")
    contents[name] = src
    lit, esc = src.count(OLD_LIT), src.count(OLD_ESC)
    if lit != expect["lit"] or esc != expect["esc"]:
        problems.append("  " + name + " [version pins]: expected " + str(expect["lit"]) + " literal / " + str(expect["esc"]) + " escaped, found " + str(lit) + " / " + str(esc))
if problems: fail("anchor validation failed:\n" + "\n".join(problems) + "\n ")
if CHECK_ONLY:
    total = sum(v["lit"] + v["esc"] for v in VERSION_FILES.values())
    print("CHECK OK: " + str(len(IDX_EDITS)) + " calendar anchors + " + str(total) + " version pins verified across " + str(len(VERSION_FILES)) + " files."); sys.exit(0)
for label, old, new in IDX_EDITS:
    text = text.replace(old, new, 1); print("  ok: " + label)
contents["index.html"] = text
for name in VERSION_FILES:
    updated = contents[name].replace(OLD_LIT, NEW_LIT).replace(OLD_ESC, NEW_ESC)
    Path(name).write_text(updated, encoding="utf-8")
    print("  ok: version lockstep -> " + name)
print()
print("Patch 3.9E.5.17.3 applied — public booking calendar polish.")
print("Next: for t in test_*.mjs; do node $t; done   then commit/push per the booking deploy flow.")
