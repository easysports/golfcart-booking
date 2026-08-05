#!/usr/bin/env bash
set -Eeuo pipefail
REPO=/workspaces/golfcart-booking
ZIP_NAME=ScheduleFleet_3.9E.5.17.2_Public_Booking_Build_Identity.zip
ZIP="$REPO/$ZIP_NAME"
EXPECTED_ZIP_SHA=840bf3c060d8bb1f19e698cd507a46956b1f755f6ed31bee42e9013d78743ed8
EXPECTED_HEAD_SHORT=e67db1c
BACKEND_URL="${BACKEND_URL:-https://studops-api.onrender.com}"
PUBLIC_URL="${PUBLIC_URL:-https://book.golfcart.fun}"

fail(){ echo "ERROR: $*" >&2; exit 1; }

echo "=== VERIFY CUTOVER-READINESS BACKEND IS LIVE ==="
BACKEND_BODY="$(curl -fsS "$BACKEND_URL/version")"
echo "$BACKEND_BODY"
[[ "$BACKEND_BODY" == *"v1.9.15 ·"* ]] || fail "backend v1.9.15 is not live"

echo "=== VERIFY PUBLIC BOOKING BASELINE ==="
cd "$REPO"
echo "Branch: $(git branch --show-current)"
echo "HEAD:   $(git rev-parse HEAD)"
git log -5 --oneline
git status --short
[[ "$(git branch --show-current)" == "main" ]] || fail "branch must be main"
[[ "$(git rev-parse --short=7 HEAD)" == "$EXPECTED_HEAD_SHORT" ]] || fail "expected HEAD $EXPECTED_HEAD_SHORT"
[[ -z "$(git status --porcelain --untracked-files=no)" ]] || fail "tracked working tree is not clean"
[[ -f "$ZIP" ]] || fail "Could not find $ZIP_NAME"
ACTUAL_SHA="$(sha256sum "$ZIP" | awk '{print $1}')"
echo "Patch ZIP: $ZIP"
echo "SHA-256:   $ACTUAL_SHA"
[[ "$ACTUAL_SHA" == "$EXPECTED_ZIP_SHA" ]] || fail "ZIP checksum mismatch"

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
  buildIdentity39E5172.js
  test_build_identity_39e5172.mjs
  test_checkout_state_integrity_39e5171.mjs
  test_public_pricing_contract_39e517.mjs
)
git add -- "${FILES[@]}"
STAGED="$(git diff --cached --name-only | sort)"
EXPECTED="$(printf '%s\n' "${FILES[@]}" | sort)"
[[ "$STAGED" == "$EXPECTED" ]] || { echo "Staged:"; printf '%s\n' "$STAGED"; fail "staged file set mismatch"; }

echo "=== STAGED PUBLIC BOOKING PATCH ==="
git diff --cached --stat
git commit -m "Booking: expose live build identity"
NEW_SHA="$(git rev-parse --short HEAD)"

for test_file in test_*.mjs; do node "$test_file"; done
node --check buildIdentity39E5172.js
node --check checkoutStateIntegrity39E5171.js
python - <<'PY'
from pathlib import Path
import os, re, subprocess, tempfile
html=Path('index.html').read_text()
scripts=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', html, re.S|re.I)
fd,name=tempfile.mkstemp(suffix='.js'); os.close(fd)
try:
    Path(name).write_text('\n'.join(scripts))
    subprocess.run(['node','--check',name],check=True)
finally:
    Path(name).unlink(missing_ok=True)
print('PASS public booking inline JavaScript syntax')
PY

git push origin main
echo "PUBLIC BOOKING PUSHED: $NEW_SHA"

echo "=== WAITING FOR VERCEL LIVE MARKER ==="
for i in $(seq 1 30); do
  BODY="$(curl -fsS "$PUBLIC_URL/?deploy_check=$NEW_SHA" || true)"
  if grep -q 'schedulefleet-public-version" content="3.9E.5.17.2"' <<<"$BODY"; then
    echo "PUBLIC BOOKING LIVE: 3.9E.5.17.2 · $NEW_SHA"
    exit 0
  fi
  echo "Vercel check $i: marker not live yet"
  sleep 10
done
fail "Vercel did not expose the 3.9E.5.17.2 marker in time"
