#!/usr/bin/env python3
"""
patch_waiver.py — "Hi {name}'s friend!" on forwarded waiver links

The success-screen "share this link" + Copy button now append shared=1, and the
page greets shared visitors as "{first}'s friend" instead of the booker's name.
The booker's original (emailed) link is unchanged — they still see "Hi {first}!".

Run from the golfcart-booking repo root (where waiver.html lives).
  git add -A && git commit -m "Waiver: friend greeting on shared links" && git push
Idempotent.
"""
import os, sys
PATH = "waiver.html"
if not os.path.exists(PATH):
    sys.exit("ERROR: waiver.html not found — run from the golfcart-booking repo root")

with open(PATH, "r", encoding="utf-8") as f: src = f.read()
if "params.get('shared')" in src:
    print("SKIP: friend-greeting patch already applied.")
    sys.exit(0)

def repl(old, new, label):
    global src
    if src.count(old) != 1:
        sys.exit(f"ANCHOR ERROR [{label}]: expected 1 match, found {src.count(old)}")
    src = src.replace(old, new)
    print(f"  ok: {label}")

# 1. greeting: friend variant when shared=1
repl(
    "    document.getElementById('greeting').textContent = `Hi ${info.first_name || 'there'}!`;",
    "    const _shared = params.get('shared') === '1';\n"
    "    document.getElementById('greeting').textContent = _shared\n"
    "      ? `Hi ${info.first_name ? info.first_name + \"'s\" : 'their'} friend!`\n"
    "      : `Hi ${info.first_name || 'there'}!`;",
    "greeting friend variant",
)

# 2. success-screen share link -> add shared=1
repl(
    "    const link = window.location.href;\n"
    "    els.shareLink.textContent = link;",
    "    const _su = new URL(window.location.href); _su.searchParams.set('shared', '1');\n"
    "    const link = _su.toString();\n"
    "    els.shareLink.textContent = link;",
    "share link shared=1",
)

# 3. copy button -> copy the shared=1 link
repl(
    "  navigator.clipboard.writeText(window.location.href).then(() => {",
    "  const _cu = new URL(window.location.href); _cu.searchParams.set('shared', '1');\n"
    "  navigator.clipboard.writeText(_cu.toString()).then(() => {",
    "copy shared=1 link",
)

with open(PATH, "w", encoding="utf-8") as f: f.write(src)
print(f"OK: friend-greeting patch applied to {PATH}")
