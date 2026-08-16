#!/usr/bin/env python3
"""
patch_waivers_mobile.py
Waivers tab: make the rows usable on a phone.

Run from the studops-frontend repo root, on the dev branch:
    python3 patch_waivers_mobile.py && git add -A && git commit -m "waivers: responsive rows on mobile" && git push && git checkout main && git pull && git merge dev && git push && git checkout dev

Why:
Each waiver row is a CSS grid locked to four fixed-minimum columns:
    minmax(190px,1.2fr) minmax(160px,1fr) minmax(160px,.8fr) minmax(280px,auto)
That is an 826px minimum before gaps. Grid columns never wrap, so on a phone
(~390px) the row simply runs off the right edge: the status badge clips
mid-word and the Email / SMS / Copy Link / View buttons are entirely
off-screen - exactly what you hit trying to send Deborah her link.

Fix: switch the row to the same wrap-capable pattern the tab's own stat cards
already use - repeat(auto-fit, minmax(min(240px,100%),1fr)). Desktop keeps a
four-across layout; a tablet folds to two-by-two; a phone stacks the four
sections vertically with every button reachable. The button cluster and the
expanded signer rows already flex-wrap, so nothing else needs touching.

Idempotent; validates the anchor; esbuild syntax check; writes
src/WaiversTab.jsx.bak_mobile and restores it on failure.
"""

import os
import shutil
import subprocess
import sys

FILE = os.path.join("src", "WaiversTab.jsx")
MARKER = "patch-waivers-mobile-v1"

OLD = 'gridTemplateColumns: "minmax(190px,1.2fr) minmax(160px,1fr) minmax(160px,.8fr) minmax(280px,auto)"'
NEW = 'gridTemplateColumns: "repeat(auto-fit, minmax(min(240px, 100%), 1fr))" /* [patch-waivers-mobile-v1] wraps on phones */'


def fail(message):
    print(f"FAIL: {message}")
    sys.exit(1)


def main():
    if not os.path.exists(FILE):
        fail(f"{FILE} not found. Run this from the studops-frontend repo root.")
    with open(FILE, "r", encoding="utf-8") as handle:
        source = handle.read()

    if MARKER in source:
        print(f"Already applied ({MARKER}). Nothing to do.")
        return

    count = source.count(OLD)
    if count != 1:
        fail(f"row grid anchor matched {count} times, expected 1. "
             f"The live file has drifted. Re-upload a fresh copy.")
    print("Anchor validated (1/1).")

    shutil.copy2(FILE, FILE + ".bak_mobile")
    source = source.replace(OLD, NEW, 1)
    with open(FILE, "w", encoding="utf-8") as handle:
        handle.write(source)
    print("Edit applied.")

    result = subprocess.run(
        ["npx", "--yes", "esbuild", FILE, "--loader:.jsx=jsx", "--outfile=/dev/null"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        shutil.copy2(FILE + ".bak_mobile", FILE)
        print(result.stderr)
        fail("esbuild syntax check failed. File restored. Nothing changed.")
    print("esbuild syntax check passed.")

    print("")
    print("Applied. Waiver rows now stack on phones - status badge, counts, and")
    print("the Email / SMS / Copy Link / View buttons all reachable.")


if __name__ == "__main__":
    main()
