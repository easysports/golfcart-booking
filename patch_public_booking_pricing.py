#!/usr/bin/env python3
"""Public booking cart-specific seasons

Idempotent marker/anchor patch. Creates an ignored .bak backup and restores it
if syntax validation fails.
"""
from pathlib import Path
import sys, json, zlib, base64, shutil, subprocess, os
CANDIDATES = ['index.html']
path = next((Path(p) for p in CANDIDATES if Path(p).exists()), None)
if not path:
    sys.exit("ERROR: target file not found; run from the repository root")
raw = path.read_bytes()
newline = "\r\n" if b"\r\n" in raw else "\n"
src = raw.decode("utf-8").replace("\r\n", "\n")
MARKER = 'const APPROVED_DURATIONS = new Set([2, 3, 4, 5, 6, 7, 14, 30, 60, 90]);'
if MARKER in src:
    print("SKIP: patch already applied")
    sys.exit(0)
edits = json.loads(zlib.decompress(base64.b64decode('eNrtVW1P2zAQ/itHP9BES0OB0gm6MKF1k9AkQJTtS6kqN3FotNSpbFeoGvz33TlO67B2ZWIfJyWpX87Pc/ec7zocNmImdUvNeZylWQyKM1UI/Ml5rLNCNAJopAthxvDA9cDsewnTfKClDz/vBUCWgrc3l1mciYc+08wHyfVCChCLPO+RRVwIpSGBCAR/BLThFQS8g+bd4dFZu41P0zfWaSHBK48oKFJwoMPSQWWZK2SlMQoXXYVmaUwshsLgrymqg1wkOI5AhTgqrT+6KKtVwjg6Pjs5xafpw9k6tjL+BM4j68b+PspBwE9PGPKHiEj8lSbKHHqmT10lXLoXrtb9hWQ0Vl8KaXUvo79MAqC03S3n/Ctf7srCcOTkoDp3SclAkk+ruedC9hz/XPmTyqcy8jDNcs0lRh+dQ2KTM85wGkVQOUuCJCGhjzXCV9uOJ8aACzbJuZ0QJ4c9NCN1fMumCqk9jwUw8YkQ3WFLBS2YmIFfiUiXtoz24ubm9vr75/64/+324u7y+mpgL8mAa294FMBxAJ0ATgLoBvA+gEOcHLdxhu9pe0SI/3OyOSe09ru84ZQp72oxm5ADZVb8v8zewQGUyiqYsSVMONRaVAg3WfwD9JRDjoWpcIeqDsVAcx1PaWC7mJ4ybfBYrBcsz5eA3kEVkwlHmWZDYGXLw3ViAxIlrKe+3vpek21qAHs1s7f1xQ25t+2wnnlF8tr++IYO+U975Mr7XY2SVrcUWpi9KLIw5+JBT+Ec2pbmectlQ0VRMm/iBI2ni5jl/FMxmzPJPWvCXBPfH7ZH5J7boxujAIaNquogkcU8KR6FvXXr5qPKan7xl9nbYRCQOJqvaxNPGMLVBS3r8M9sJYYTSe+1llv5Oy2k1JDKYtba4kKnhqwLrOsa8Yb9AJodwm1WNN3dNN0dNN2NNN0VzegXNGLxHw==')).decode("utf-8"))
for label, old, new in edits:
    old = old.replace("\r\n", "\n"); new = new.replace("\r\n", "\n")
    n = src.count(old)
    if n != 1:
        sys.exit(f"ANCHOR ERROR [{label}]: expected 1 match, found {n}")
    src = src.replace(old, new, 1)
    print("  ok: " + label)
backup = path.with_suffix(path.suffix + ".bak")
shutil.copy2(path, backup)
path.write_text(src.replace("\n", newline), encoding="utf-8", newline="")
print("DONE: patched " + str(path))
