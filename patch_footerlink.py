#!/usr/bin/env python3
"""
patch_footerlink.py
Booking site: truthful footer credit linking book.golfcart.fun -> golfcartrentalsoftware.com.

Run from the golfcart-booking Codespace, repo root:
    python3 patch_footerlink.py && git add -A && git commit -m "footer: Fleet powered by ScheduleFleet link" && git push

Why:
golfcartrentalsoftware.com has 3 of 36 URLs indexed and Google last read its
sitemap on Jun 24 — a young domain with no inbound links gets crawl-apathy, and
no amount of on-page work fixes that. The cheapest real link it can get is a
truthful one from a domain Google already crawls: the booking page for the
fleet the software actually runs. Dofollow on purpose (no rel="nofollow").

Adds one item to the existing footer line, after "Charleston, SC":

    · Fleet powered by ScheduleFleet   (ScheduleFleet -> https://golfcartrentalsoftware.com/)

Canonical target verified 2026-09-13: https://golfcartrentalsoftware.com (no www).
The footer is static HTML in index.html, so this push is the whole deploy.

Idempotent; anchor-validated; writes index.html.bak_footerlink before editing.
"""

import os
import shutil
import sys

PAGE = "index.html"
MARKER = "patch-footerlink-v1"

ANCHOR = '''  <a href="mailto:info@golfcart.fun">info@golfcart.fun</a> &nbsp;·&nbsp; Charleston, SC
  <div>'''

NEW = '''  <a href="mailto:info@golfcart.fun">info@golfcart.fun</a> &nbsp;·&nbsp; Charleston, SC
  &nbsp;·&nbsp; Fleet powered by <a href="https://golfcartrentalsoftware.com/" target="_blank" rel="noopener" title="Golf cart rental software by ScheduleFleet">ScheduleFleet</a><!-- [patch-footerlink-v1] -->
  <div>'''


def fail(msg):
    print(f"[{MARKER}] FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    if not os.path.exists(PAGE):
        fail(f"{PAGE} not found — run from the golfcart-booking repo root.")

    with open(PAGE, "r", encoding="utf-8") as handle:
        html = handle.read()

    if MARKER in html:
        print(f"[{MARKER}] already applied — nothing to do.")
        return

    count = html.count(ANCHOR)
    if count != 1:
        fail(f"footer anchor matched {count} times, expected 1. "
             f"Footer markup has drifted — read <footer> in {PAGE} and re-anchor.")

    shutil.copyfile(PAGE, f"{PAGE}.bak_footerlink")
    html = html.replace(ANCHOR, NEW, 1)

    with open(PAGE, "w", encoding="utf-8") as handle:
        handle.write(html)

    print(f"[{MARKER}] applied: footer now links 'ScheduleFleet' -> https://golfcartrentalsoftware.com/ "
          f"(backup: {PAGE}.bak_footerlink)")


if __name__ == "__main__":
    main()
