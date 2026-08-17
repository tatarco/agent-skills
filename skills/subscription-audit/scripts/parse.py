#!/usr/bin/env python3
"""Extract amounts and billing context from invoice PDFs.

Usage:  python3 parse.py pdfs/            # summarise every PDF
        python3 parse.py pdfs/ --full     # dump full text too

Prints, per file: currency amounts found, any card digits, any dates, and
the first lines of text so you can identify the vendor. Amounts are printed,
never interpreted — you decide which number is the charge.
"""
import glob, os, re, sys

try:
    from pypdf import PdfReader
except ImportError:
    try:
        from PyPDF2 import PdfReader  # type: ignore
    except ImportError:
        sys.exit("pip install pypdf")

AMOUNT = re.compile(r'(?:[$€£₪]|ILS|USD|EUR|GBP)?\s?\d{1,3}(?:,\d{3})*\.\d{2}')
CARD   = re.compile(r'(?:ending|\*+|xxxx|•+)\s*(\d{4})\b', re.I)
DATE   = re.compile(r'\b\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}\b')

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    full = '--full' in sys.argv
    root = args[0] if args else 'pdfs'
    files = sorted(glob.glob(os.path.join(root, '**', '*.pdf'), recursive=True))
    if not files:
        sys.exit(f'no PDFs under {root}')

    for f in files:
        try:
            text = "\n".join((p.extract_text() or '') for p in PdfReader(f).pages[:3])
        except Exception as e:
            print(f'--- {os.path.basename(f)}: UNREADABLE ({e})')
            continue
        amounts = list(dict.fromkeys(m.group().strip() for m in AMOUNT.finditer(text)))
        cards   = list(dict.fromkeys(CARD.findall(text)))
        dates   = list(dict.fromkeys(DATE.findall(text)))[:4]
        print('=' * 72)
        print(os.path.basename(f))
        print('  amounts :', ', '.join(amounts[:12]) or '(none found)')
        if cards: print('  cards   :', ', '.join('••••' + c for c in cards))
        if dates: print('  dates   :', ', '.join(dates))
        head = [l.strip() for l in text.splitlines() if l.strip()][:6]
        for l in head:
            print('  |', l[:96])
        if full:
            print('-' * 72); print(text)

if __name__ == '__main__':
    main()
