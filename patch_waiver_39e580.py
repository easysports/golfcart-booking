#!/usr/bin/env python3
"""
patch_waiver_39e580.py — [patch39e580-waiver-terms-v2]  (golfcart-booking, DEPLOY SECOND)

Run in the golfcart-booking Codespace, on main — ONLY AFTER the backend patch
(patch_server_39e580.py) is live on Render and
    curl "https://studops-api.onrender.com/waiver-terms?version=wherewolf-v2"
returns v2_derivation_ok: true. Never before.

    python3 patch_waiver_39e580.py && git add -A && git commit -m "waiver: terms v2 - delivery/collection clauses, report terms_version (39e580)" && git push

What changes in waiver.html
  1. Sections 3, 5(j), 7(g), 10 rewritten with the SAME strings the backend derives
     for wherewolf-v2 (byte-identical, so the PDF matches what the customer read).
  2. #waiver-text carries data-terms-version="wherewolf-v2" and a small
     customer-visible "Terms version" line at the end of the terms.
  3. The signing POST sends terms_version so the backend stamps the row with the
     version that was actually displayed.

Idempotent (marker check), anchor-validated (each anchor exactly once),
all-or-nothing write, backup waiver.html.bak_39e580.
"""

import os
import shutil
import sys

MARKER = "patch39e580-waiver-terms-v2"
PAGE = "waiver.html"
VERSION = "wherewolf-v2"

EDITS = [
    ("3",
     "You must return the Vehicle to our rental office on the date and time specified in this Agreement, and in the same condition that you received it, except for ordinary wear. If the Vehicle is returned after closing hours, you remain responsible for the safety of, and any damage to, or loss of, the Vehicle until we inspect it upon our next opening for business.",
     "We deliver the Vehicle to the delivery address shown in this Agreement and collect it from that same address at the end of the rental period. You must have the Vehicle available for collection at that address on the return date and time specified in this Agreement, in the same condition that you received it, except for ordinary wear. You remain responsible for the safety of, and any damage to, or loss of, the Vehicle until we collect and inspect it."),
    ("5",
     "(j) occurs as a result of driving the Vehicle on unpaved roads;",
     "(j) occurs as a result of driving the Vehicle on the beach, on dunes or marsh, or on any other off-road terrain;"),
    ("7",
     "(g) $50, plus $5/mile for every mile between the renting location and the place where the Vehicle is returned, repossessed or abandoned, plus all other expenses we incur in locating and recovering the Vehicle if you fail to return it or if we elect to repossess the Vehicle under the terms of this Agreement;",
     "(g) $50, plus $5/mile for every mile between the delivery address shown in this Agreement and the place where the Vehicle is recovered, repossessed or abandoned, plus all other expenses we incur in locating and recovering the Vehicle if it is not available at that address at the scheduled collection time, if it has been moved from that address without our consent, or if we elect to repossess the Vehicle under the terms of this Agreement;"),
    ("10",
     "If you wish to extend the rental period, you must return the Vehicle to our rental office for inspection and written amendment by us of the due-in date.",
     "If you wish to extend the rental period, you must request the extension from us by text message or email before the scheduled collection time. An extension is effective only when we confirm it in writing and any additional charges are paid; a text message or email from us is a writing for this purpose."),
]


def fail(msg):
    print(f"ERROR [{MARKER}]: {msg}", file=sys.stderr)
    sys.exit(1)


if not os.path.exists(PAGE):
    fail(f"{PAGE} not found — run from the golfcart-booking repo root")

with open(PAGE, "r", encoding="utf-8") as f:
    html = f.read()

if MARKER in html:
    print(f"SKIP: {MARKER} already applied.")
    sys.exit(0)


def repl(old, new, label):
    global html
    n = html.count(old)
    if n != 1:
        fail(f"[{label}] expected 1 match, found {n}. Page drifted — read the live file and re-anchor.")
    html = html.replace(old, new, 1)
    print(f"  ✓ {label}")


# Pre-flight every anchor before touching anything.
for n, frm, _ in EDITS:
    c = html.count(frm)
    if c != 1:
        fail(f"section {n} v1 clause expected exactly once in {PAGE}, found {c}")
print("  ✓ all four v1 clause anchors present exactly once")

# 1. Marker + version attribute on the terms container
repl('<div class="waiver-text" id="waiver-text">',
     f'<div class="waiver-text" id="waiver-text" data-terms-version="{VERSION}"><!-- [{MARKER}] -->',
     "terms container carries data-terms-version")

# 2. Four clause rewrites
for n, frm, to in EDITS:
    repl(frm, to, f"section {n} rewritten")

# 3. Customer-visible version line at the end of the terms
repl("If any provision of this Agreement is deemed void or unenforceable, the remaining provisions are valid and enforceable.</p>\n      </div>",
     "If any provision of this Agreement is deemed void or unenforceable, the remaining provisions are valid and enforceable.</p>\n"
     f'        <p style="font-size:11px; color:#94a3b8; margin-top:10px;">Terms version {VERSION}</p>\n'
     "      </div>",
     "terms version line")

# 4. Signing POST reports the displayed version
repl("        agreed: true,\n        signature: sigCanvas.toDataURL('image/png'),",
     "        agreed: true,\n"
     f"        terms_version: ((document.getElementById('waiver-text') || {{}}).dataset || {{}}).termsVersion || '{VERSION}',\n"
     "        signature: sigCanvas.toDataURL('image/png'),",
     "POST sends terms_version")

backup = f"{PAGE}.bak_39e580"
shutil.copyfile(PAGE, backup)
with open(PAGE, "w", encoding="utf-8") as f:
    f.write(html)
print(f"  ✓ wrote {PAGE} (backup: {backup})")
print(f"DONE [{MARKER}]")
