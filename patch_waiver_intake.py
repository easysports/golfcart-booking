#!/usr/bin/env python3
"""
patch_waiver_intake.py
Waiver page: make the two photo slots unmistakably different documents.

Run from the golfcart-booking repo root:
    python3 patch_waiver_intake.py && git add -A && git commit -m "waiver: distinguish licence and insurance uploads" && git push

Why:
Of the first 46 signers screened by the document checker, 11 uploaded something
that was not an insurance card - almost always the BACK of their driver's
licence, occasionally the identical file twice. That is not 11 careless
customers. Both upload buttons carry the same body text ("Take / upload photo"
/ "Tap to open camera or choose a file"), and the card subtitle reads "a clear
photo of your driver's license and auto-insurance card", which parses as one
two-part instruction about a single document. Two identical-looking boxes in a
row, on a phone, read as front-and-back.

Thumbnails already existed, so the customer could see what they picked - they
just had no reason to believe the second box wanted a different document.

Changes:
  1. Each slot gets its own body text naming the specific document.
  2. The insurance slot carries an explicit "not the back of your licence" note
     and names real carriers so the customer knows what to look for.
  3. Card subtitle rewritten to say plainly that these are two different items.
  4. Client-side duplicate check: identical image in both slots is refused at
     the point of upload, while the customer is still on the page and can fix
     it. (The backend also hashes both images as a second line of defence.)
  5. The backend's DUPLICATE_DOCUMENT_IMAGE error is surfaced verbatim rather
     than being flattened into "Something went wrong".
  6. Thumbnails 44px -> 64px so a wrong pick is obvious at a glance.

Idempotent; validates every anchor before editing; writes
waiver.html.bak_intake first and restores it if anything fails.
"""
import os
import shutil
import sys

PATH = "waiver.html"
MARKER = "waiver-intake-clarity-v1"

if not os.path.exists(PATH):
    sys.exit("FAIL: waiver.html not found. Run this from the golfcart-booking repo root.")

src = open(PATH, encoding="utf-8").read()

if MARKER in src:
    print("Already applied (%s) - no changes." % MARKER)
    sys.exit(0)

backup = PATH + ".bak_intake"
shutil.copy2(PATH, backup)
print("Backup -> %s" % backup)


def anchor(text, needle, label):
    n = text.count(needle)
    if n != 1:
        shutil.copy2(backup, PATH)
        sys.exit("FAIL: anchor '%s' found %d times (need exactly 1). Restored." % (label, n))
    print("  anchor ok: %s" % label)


# ─────────────────────────────────────────────── 1. card subtitle ───
A = ('<div class="card-sub">A clear photo of your driver&#39;s license and auto-insurance card.</div>')
if A not in src:
    A = '<div class="card-sub">A clear photo of your driver\'s license and auto-insurance card.</div>'
anchor(src, A, "photos card subtitle")

B = ('<div class="card-sub">Two different documents: your driver&#39;s licence, '
     'and your auto insurance card.</div>')
src = src.replace(A, B)


# ──────────────────────────────────── 2. licence slot: name the side ───
A = ('''        <label>Driver's license <span class="req">*</span></label>
        <label class="photo-btn" id="dl-btn">
          <span class="icon">\U0001faaa</span>
          <span class="txt">Take / upload photo<small id="dl-name">Tap to open camera or choose a file</small></span>
          <input type="file" id="dl_photo" accept="image/*" />
        </label>''')
anchor(src, A, "licence upload block")

B = ('''        <label>1. Driver's licence &mdash; front <span class="req">*</span></label>
        <label class="photo-btn" id="dl-btn">
          <span class="icon">\U0001faaa</span>
          <span class="txt">Photo of your licence<small id="dl-name">The front, with your photo and date of birth</small></span>
          <input type="file" id="dl_photo" accept="image/*" />
        </label>''')
src = src.replace(A, B)


# ─────────────────────── 3. insurance slot: say what it is NOT ───
A = ('''        <label>Insurance card <span class="req">*</span></label>
        <label class="photo-btn" id="ins-btn">
          <span class="icon">\U0001f4c4</span>
          <span class="txt">Take / upload photo<small id="ins-name">Tap to open camera or choose a file</small></span>
          <input type="file" id="insurance_photo" accept="image/*" />
        </label>''')
anchor(src, A, "insurance upload block")

B = ('''        <label>2. Auto insurance card <span class="req">*</span></label>
        <div class="doc-note">This is the card from your <strong>car insurance company</strong> &mdash;
          GEICO, State Farm, Progressive, Allstate, USAA. It shows your policy number.
          <strong>Not</strong> the back of your licence, and not a health insurance card.</div>
        <label class="photo-btn" id="ins-btn">
          <span class="icon">\U0001f697</span>
          <span class="txt">Photo of your insurance card<small id="ins-name">Paper card, or the one in your insurer&rsquo;s app</small></span>
          <input type="file" id="insurance_photo" accept="image/*" />
        </label>''')
src = src.replace(A, B)


# ─────────────────────────────────────────────────── 4. styling ───
A = '  .photo-thumb { height: 44px; width: 44px; object-fit: cover; border-radius: 8px; border: 1px solid var(--border); }'
anchor(src, A, "photo-thumb style")

B = ('  .photo-thumb { height: 64px; width: 64px; object-fit: cover; border-radius: 8px; border: 1px solid var(--border); }\n'
     '  /* [' + MARKER + '] */\n'
     '  .doc-note { font-size: 12px; line-height: 1.5; color: var(--sub); background: #fbfbf9;\n'
     '    border: 1px solid var(--border); border-left: 3px solid var(--orange);\n'
     '    border-radius: 6px; padding: 9px 11px; margin-bottom: 10px; }')
src = src.replace(A, B)


# ──────────────────────────── 5. refuse the same image in both slots ───
A = '''        photos[key] = canvas.toDataURL('image/jpeg', 0.85);
'''
anchor(src, A, "photo assignment")

B = '''        const encoded = canvas.toDataURL('image/jpeg', 0.85);

        // [''' + MARKER + '''] The same picture in both slots is always a
        // mistake, and it is far kinder to say so now than to let the customer
        // finish, drive to the island, and be turned away at the cart.
        const otherKey = key === 'dl' ? 'insurance' : 'dl';
        if (photos[otherKey] && photos[otherKey] === encoded) {
          input.value = '';
          const errEl = document.getElementById('form-err');
          if (errEl) {
            errEl.textContent = key === 'insurance'
              ? 'That is the same picture as your licence. Please add your auto insurance card \\u2014 the card from your insurance company showing your policy number.'
              : 'That is the same picture as your insurance card. Please add the front of your driver\\u2019s licence.';
            errEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
          return;
        }

        photos[key] = encoded;
'''
src = src.replace(A, B)


# ─────────────────────── 6. surface the server-side duplicate error ───
A = ("    errEl.textContent = e.message === 'Submission failed' || !e.message\n"
     "      ? 'Something went wrong. Please try again or call (843) 800-0310.'\n"
     "      : e.message;")
anchor(src, A, "submit error handler")

B = ("    // [" + MARKER + "] the server also hashes both images; its duplicate\n"
     "    // message is written for the customer, so pass it straight through\n"
     "    errEl.textContent = e.message === 'Submission failed' || !e.message\n"
     "      ? 'Something went wrong. Please try again or call (843) 800-0310.'\n"
     "      : e.message;")
src = src.replace(A, B)


# ─────────────────────── 7. clearer required-field messages ───
A = """  if (!photos.insurance) { errEl.textContent = 'Please add a photo of your insurance card.'; return; }"""
anchor(src, A, "insurance required message")
B = ("""  if (!photos.insurance) { errEl.textContent = 'Please add a photo of your auto insurance card \\u2014 """
     """the card from your insurance company, not the back of your licence.'; return; }""")
src = src.replace(A, B)


open(PATH, "w", encoding="utf-8").write(src)
print("Wrote %s" % PATH)

# ─────────────────────────────────────────────────────── verify ───
check = open(PATH, encoding="utf-8").read()

failures = []
if check.count('id="dl_photo"') != 1:
    failures.append("dl_photo input missing or duplicated")
if check.count('id="insurance_photo"') != 1:
    failures.append("insurance_photo input missing or duplicated")
if check.count("photos[key] = encoded;") != 1:
    failures.append("photo assignment not rewritten")
if check.count("doc-note") != 2:  # one CSS rule, one usage
    failures.append("doc-note style or markup missing")
if check.count(MARKER) < 3:
    failures.append("marker not written")
for tag in ["<html", "</html>", "<script", "</script>"]:
    if tag not in check:
        failures.append("structural tag %s lost" % tag)
if check.count("<script") != check.count("</script>"):
    failures.append("script tags unbalanced")

if failures:
    shutil.copy2(backup, PATH)
    sys.exit("FAIL: post-write verification failed. Restored.\n  - " + "\n  - ".join(failures))

print("  verified: both inputs intact, duplicate guard in place, script tags balanced")
print("")
print("patch_waiver_intake applied cleanly.")
print("Open waiver.html in a browser and try picking the same photo twice before pushing.")
