#!/usr/bin/env python3
"""Blur sensitive text in screenshots, then PROVE it's gone.

Post-hoc safety net. Prefer blurring in-browser via a step's "blur" selectors (capture.py) —
that is deterministic. This catches what CSS could not reach, and, more importantly, it
re-OCRs its own output and FAILS if anything still matches. A blur you did not verify is a
blur you cannot trust.

Requires: tesseract on PATH, Pillow.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

from PIL import Image, ImageFilter

# Sensible defaults. Extend per project via --rules rules.json:  {"patterns": ["..."]}
DEFAULT_PATTERNS = [
    r"\+?\d[\d\-\s()]{7,}\d",            # phone numbers
    r"[\w.+-]+@[\w-]+\.[\w.]+",           # emails
    r"\b\d{6}\b",                          # 6-digit codes (venue/OTP/discount)
    r"\b\d{1,3}\.\d%|\b\d{1,3}%",         # percentages / performance figures
    r"\b(?:\d[ -]*?){13,19}\b",           # card-ish numbers
]


def ocr_boxes(path):
    """(text, x, y, w, h) for every OCR'd word."""
    tsv = subprocess.run(["tesseract", str(path), "-", "tsv"],
                         capture_output=True, text=True).stdout
    out = []
    for line in tsv.splitlines()[1:]:
        f = line.split("\t")
        if len(f) >= 12 and f[11].strip():
            try:
                x, y, w, h = map(int, f[6:10])
            except ValueError:
                continue
            out.append((f[11].strip(), x, y, w, h))
    return out


def redact_image(src, dst, patterns, pad=14, radius=26):
    im = Image.open(src).convert("RGB")
    hits = []
    for text, x, y, w, h in ocr_boxes(src):
        if any(re.fullmatch(p, text) or re.search(p, text) for p in patterns):
            box = (max(0, x - pad), max(0, y - pad),
                   min(im.width, x + w + pad), min(im.height, y + h + pad))
            im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(radius)), box)
            hits.append(text)
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst)
    return hits


def verify(path, patterns):
    """Re-OCR the OUTPUT. Anything still matching is a leak."""
    leaks = []
    for text, *_ in ocr_boxes(path):
        if any(re.fullmatch(p, text) or re.search(p, text) for p in patterns):
            leaks.append(text)
    return leaks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="dir of screenshots (or a single png)")
    ap.add_argument("-o", "--out", default="clean")
    ap.add_argument("--rules", help="rules.json with {'patterns': [...]}")
    ap.add_argument("--verify-only", action="store_true",
                    help="don't redact; just check the files for leaks")
    args = ap.parse_args()

    patterns = list(DEFAULT_PATTERNS)
    if args.rules:
        patterns += json.loads(pathlib.Path(args.rules).read_text()).get("patterns", [])

    src = pathlib.Path(args.src)
    files = sorted(src.glob("*.png")) if src.is_dir() else [src]
    out = pathlib.Path(args.out)

    if args.verify_only:
        bad = False
        for f in files:
            leaks = verify(f, patterns)
            print(f"  {f.name}: {'LEAK -> ' + ', '.join(leaks) if leaks else 'clean'}")
            bad |= bool(leaks)
        return 1 if bad else 0

    failed = False
    for f in files:
        dst = out / f.name
        hits = redact_image(f, dst, patterns)
        leaks = verify(dst, patterns)          # prove it, don't assume it
        status = "clean" if not leaks else f"!! STILL VISIBLE: {', '.join(leaks)}"
        print(f"  {f.name}: blurred {len(hits)} -> {status}")
        failed |= bool(leaks)

    print(f"\n-> {out}")
    if failed:
        print("\nFAIL: something survived the blur. Widen the pattern, raise --radius, "
              "or blur it in-browser via the step's 'blur' selectors.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
