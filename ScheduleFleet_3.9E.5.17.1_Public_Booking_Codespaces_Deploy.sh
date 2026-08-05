#!/usr/bin/env bash
set -euo pipefail
REPO=/workspaces/golfcart-booking
ZIP_NAME=ScheduleFleet_3.9E.5.17.1_Public_Booking_Checkout_State_Integrity.zip
ZIP="$REPO/$ZIP_NAME"
EXPECTED_ZIP_SHA=26a9cce5b0065b3cdb9e805f611a42e4e3979a271c3ab50fdec78e539ee872ed
EXPECTED_HEAD=0919200a7bd663ef6fc08c57efe9c080dfa7823b
BACKEND_URL="${BACKEND_URL:-https://studops-api.onrender.com}"
PUBLIC_URL="${PUBLIC_URL:-https://book.golfcart.fun}"

echo "=== VERIFY CHECKOUT-INTEGRITY BACKEND BASELINE ==="
BACKEND_BODY="$(curl -fsS "$BACKEND_URL/version")"
echo "$BACKEND_BODY"
[[ "$BACKEND_BODY" == *"v1.9.14 · a44cef3"* ]] || { echo "ERROR: expected backend v1.9.14 · a44cef3"; exit 1; }

echo "=== VERIFY PUBLIC BOOKING BASELINE ==="
cd "$REPO"
echo "Branch: $(git branch --show-current)"
echo "HEAD:   $(git rev-parse HEAD)"
git log -5 --oneline
git status --short
[[ "$(git branch --show-current)" == "main" ]] || { echo "ERROR: branch must be main"; exit 1; }
[[ "$(git rev-parse HEAD)" == "$EXPECTED_HEAD" ]] || { echo "ERROR: expected HEAD $EXPECTED_HEAD"; exit 1; }
[[ -z "$(git status --porcelain --untracked-files=no)" ]] || { echo "ERROR: tracked working tree is not clean"; exit 1; }
[[ -f "$ZIP" ]] || { echo "ERROR: Could not find $ZIP_NAME"; exit 1; }
ACTUAL_SHA="$(sha256sum "$ZIP" | awk '{print $1}')"
echo "Patch ZIP: $ZIP"
echo "SHA-256:   $ACTUAL_SHA"
[[ "$ACTUAL_SHA" == "$EXPECTED_ZIP_SHA" ]] || { echo "ERROR: ZIP checksum mismatch"; exit 1; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
unzip -q "$ZIP" -d "$TMP"

echo "=== INSTALLER CHECK MODE ==="
bash "$TMP/install.sh" --check "$REPO"
echo "=== APPLY PUBLIC BOOKING PATCH ==="
bash "$TMP/install.sh" --apply "$REPO"

git diff --check
echo "=== PUBLIC BOOKING DIFF ==="
git diff --stat
git status --short
FILES=(
  index.html
  checkoutStateIntegrity39E5171.js
  test_public_pricing_contract_39e517.mjs
  test_checkout_state_integrity_39e5171.mjs
  test_checkout_state_runtime_39e5171.mjs
)
git add -- "${FILES[@]}"
STAGED="$(git diff --cached --name-only | sort)"
EXPECTED="$(printf '%s\n' "${FILES[@]}" | sort)"
[[ "$STAGED" == "$EXPECTED" ]] || { echo "ERROR: staged file set mismatch"; printf '%s\n' "$STAGED"; exit 1; }
echo "=== STAGED PUBLIC BOOKING PATCH ==="
git diff --cached --stat

git commit -m "Booking: invalidate stale checkout state"
NEW_SHA="$(git rev-parse --short HEAD)"

# Validate the exact committed tree before push.
node test_public_pricing_contract_39e517.mjs
node test_checkout_state_integrity_39e5171.mjs
node test_checkout_state_runtime_39e5171.mjs
node --check checkoutStateIntegrity39E5171.js
python - <<'PY'
from pathlib import Path
import os, re, subprocess, tempfile
html = Path('index.html').read_text()
scripts = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', html, re.S | re.I)
fd, name = tempfile.mkstemp(suffix='.js'); os.close(fd)
try:
    Path(name).write_text('\n'.join(scripts))
    subprocess.run(['node', '--check', name], check=True)
finally:
    Path(name).unlink(missing_ok=True)
print('PASS public booking inline JavaScript syntax')
PY

git push origin main
echo "PUBLIC BOOKING PUSHED: $NEW_SHA"

echo "=== WAITING FOR VERCEL LIVE MARKER ==="
for i in $(seq 1 30); do
  BODY="$(curl -fsS "$PUBLIC_URL/?deploy_check=$NEW_SHA" || true)"
  if grep -q 'schedulefleet-public-version" content="3.9E.5.17.1"' <<<"$BODY"; then
    echo "PUBLIC BOOKING LIVE: 3.9E.5.17.1 · $NEW_SHA"
    exit 0
  fi
  echo "Vercel check $i: marker not live yet"
  sleep 10
done
echo "ERROR: Vercel did not expose the 3.9E.5.17.1 marker in time"
exit 1
