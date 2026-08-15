#!/usr/bin/env python3
"""
patch_waiver_upload.py
Waiver page: allow uploading an existing photo of the license / insurance card.

Run from the golfcart-booking repo root:
    python3 patch_waiver_upload.py && git add -A && git commit -m "waiver: allow photo library and file upload" && git push

Why:
Both file inputs on waiver.html carry capture="environment". On iPhone and
Android that attribute forces the camera to open directly - the customer never
sees the "Photo Library / Choose File" options, so a photo they already have
(or a scan someone emailed them) cannot be used. Removing the attribute
restores the standard chooser: Take Photo, Photo Library, or Browse. Taking a
picture on the spot still works exactly as before; it just stops being the
only option. The backend already accepts any image the input produces.

Idempotent; validates both inputs exist before editing; writes
waiver.html.bak_upload first.
"""

import os
import shutil
import sys

PAGE = "waiver.html"

OLD_DL = '<input type="file" id="dl_photo" accept="image/*" capture="environment" />'
NEW_DL = '<input type="file" id="dl_photo" accept="image/*" />'
OLD_INS = '<input type="file" id="insurance_photo" accept="image/*" capture="environment" />'
NEW_INS = '<input type="file" id="insurance_photo" accept="image/*" />'


def fail(message):
    print(f"FAIL: {message}")
    sys.exit(1)


def main():
    if not os.path.exists(PAGE):
        fail("waiver.html not found. Run this from the golfcart-booking repo root.")
    with open(PAGE, "r", encoding="utf-8") as handle:
        html = handle.read()

    if NEW_DL in html and NEW_INS in html and OLD_DL not in html and OLD_INS not in html:
        print("Already applied. Nothing to do.")
        return

    for anchor, label in [(OLD_DL, "driver's license input"), (OLD_INS, "insurance input")]:
        if html.count(anchor) != 1:
            fail(f"{label} matched {html.count(anchor)} times, expected 1. "
                 f"The live file has drifted. Re-upload a fresh copy.")
    print("Anchors validated (2/2).")

    shutil.copy2(PAGE, PAGE + ".bak_upload")
    html = html.replace(OLD_DL, NEW_DL, 1).replace(OLD_INS, NEW_INS, 1)
    with open(PAGE, "w", encoding="utf-8") as handle:
        handle.write(html)

    print("Applied. Customers can now take a photo OR pick one from their")
    print("library / files on both waiver uploads.")


if __name__ == "__main__":
    main()
