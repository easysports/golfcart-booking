#!/usr/bin/env python3
"""
patch_terms_card_disclosure.py
Booking site: card-storage disclosure in the Rental Requirements (approved wording).

Run from the golfcart-booking repo root:
    python3 patch_terms_card_disclosure.py && git add -A && git commit -m "terms: card storage disclosure" && git push

Why:
Every checkout saves the customer's card for off-session use, and Charge Extra
Days later bills that saved card with the customer absent. Stripe's rules (and
any dispute you ever want to win) require telling the customer at collection
time. The Rental Requirements list the customer explicitly agrees to via the
terms checkbox said nothing about it - until now.

Adds one line, your approved wording verbatim, as the closing item of the
Rental Requirements list that sits directly above the "I have read and agree"
checkbox - so acceptance provably covers it:

    Your payment method is securely saved by Stripe and may be charged for
    approved additional rental days or damages per the rental agreement

The list is static HTML in index.html (not CMS-driven), so this push is the
whole deploy.

Idempotent; anchor-validated; writes index.html.bak_terms before editing.
"""

import os
import shutil
import sys

PAGE = "index.html"
MARKER = "patch-terms-card-disclosure-v1"

ANCHOR = '''              <li>All normal driving and parking laws apply</li>
            </ul>'''

NEW = '''              <li>All normal driving and parking laws apply</li>
              <li>Your payment method is securely saved by Stripe and may be charged for approved additional rental days or damages per the rental agreement</li><!-- [patch-terms-card-disclosure-v1] -->
            </ul>'''


def fail(message):
    print(f"FAIL: {message}")
    sys.exit(1)


def main():
    if not os.path.exists(PAGE):
        fail("index.html not found. Run this from the golfcart-booking repo root.")
    with open(PAGE, "r", encoding="utf-8") as handle:
        html = handle.read()

    if MARKER in html:
        print(f"Already applied ({MARKER}). Nothing to do.")
        return

    count = html.count(ANCHOR)
    if count != 1:
        fail(f"Rental Requirements anchor matched {count} times, expected 1. "
             f"The live file has drifted. Re-upload a fresh copy.")
    print("Anchor validated (1/1).")

    shutil.copy2(PAGE, PAGE + ".bak_terms")
    html = html.replace(ANCHOR, NEW, 1)
    with open(PAGE, "w", encoding="utf-8") as handle:
        handle.write(html)

    print("Applied. The disclosure is the final Rental Requirements item,")
    print("covered by the existing terms checkbox.")


if __name__ == "__main__":
    main()
