#!/usr/bin/env bash
set -euo pipefail
REPO=/workspaces/golfcart-booking
ZIP_NAME=ScheduleFleet_3.9E.5.17_Public_Booking_Pricing_Contract.zip
ZIP="$REPO/$ZIP_NAME"
EXPECTED_ZIP_SHA=0ba84a92bc11406795b184bc8031f1d25560f53d35802e00b31e42edd95107e6
EXPECTED_HEAD=60bc0d86988c350afc8ac98174aab7190a04efa6
BACKEND_URL="${BACKEND_URL:-https://studops-api.onrender.com}"
PUBLIC_URL="${PUBLIC_URL:-https://book.golfcart.fun}"

echo "=== VERIFY PRICING-CONTRACT BACKEND IS LIVE ==="
BACKEND_BODY="$(curl -fsS "$BACKEND_URL/version")"
echo "$BACKEND_BODY"
[[ "$BACKEND_BODY" == *"v1.9.14"* ]] || { echo "ERROR: backend v1.9.14 is not live"; exit 1; }

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
FILES=(index.html test_public_pricing_contract_39e517.mjs)
git add -- "${FILES[@]}"
STAGED="$(git diff --cached --name-only | sort)"
EXPECTED="$(printf '%s\n' "${FILES[@]}" | sort)"
[[ "$STAGED" == "$EXPECTED" ]] || { echo "ERROR: staged file set mismatch"; printf '%s\n' "$STAGED"; exit 1; }
git diff --cached --stat
git commit -m "Booking: restore core live pricing"
NEW_SHA="$(git rev-parse --short HEAD)"
git push origin main
echo "PUBLIC BOOKING PUSHED: $NEW_SHA"

echo "=== WAITING FOR VERCEL LIVE MARKER ==="
for i in $(seq 1 30); do
  BODY="$(curl -fsS "$PUBLIC_URL/?deploy_check=$NEW_SHA" || true)"
  if grep -q 'schedulefleet-public-version" content="3.9E.5.17"' <<<"$BODY"; then
    echo "PUBLIC BOOKING LIVE: 3.9E.5.17 · $NEW_SHA"
    exit 0
  fi
  echo "Vercel check $i: marker not live yet"
  sleep 10
done
echo "ERROR: Vercel did not expose the 3.9E.5.17 marker in time"
exit 1
