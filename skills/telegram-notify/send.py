#!/usr/bin/env python3
"""Send a Telegram message. Stdlib-only.

Usage:
    python3 send.py "your message here"
    echo "your message" | python3 send.py

Credentials are read from (first found wins):
    1. env vars TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID
    2. ~/.claude/telegram-notify.env   (KEY=VALUE lines)
"""

import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ENV_FILE = Path.home() / ".claude" / "telegram-notify.env"
TIMEOUT = 30


def load_creds() -> tuple[str, str]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if (not token or not chat) and ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            v = v.strip().strip('"').strip("'")
            if k.strip() == "TELEGRAM_BOT_TOKEN" and not token:
                token = v
            elif k.strip() == "TELEGRAM_CHAT_ID" and not chat:
                chat = v
    if not token or not chat:
        sys.exit(
            "ERROR: missing Telegram credentials. Set TELEGRAM_BOT_TOKEN and "
            f"TELEGRAM_CHAT_ID as env vars or in {ENV_FILE}"
        )
    return token, chat


def main() -> int:
    text = " ".join(sys.argv[1:]).strip()
    if not text and not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    if not text:
        sys.exit('Usage: python3 send.py "message"')

    token, chat = load_creds()
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    redact = lambda m: str(m).replace(token, "***")  # URLError text can carry the URL, and so the token
    data = urllib.parse.urlencode(
        {"chat_id": chat, "text": text, "disable_web_page_preview": "true"}
    ).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data=data), timeout=TIMEOUT) as r:
            body = json.loads(r.read().decode("utf-8"))
    except urllib.error.URLError as e:
        # Some Pythons here (python.org framework builds) ship their own CA bundle and reject a
        # locally-trusted TLS root that the system keychain accepts, so urllib fails where the
        # system does not. Fall back to curl, which uses the system trust store.
        import shutil, subprocess
        curl = shutil.which("curl")
        if not curl:
            sys.exit(f"ERROR: {redact(e)} (and no curl to fall back to)")
        out = subprocess.run(
            [curl, "-s", "-m", str(TIMEOUT), url,
             "--data-urlencode", f"chat_id={chat}",
             "--data-urlencode", f"text={text}",
             "--data-urlencode", "disable_web_page_preview=true"],
            capture_output=True, text=True)
        if out.returncode:
            sys.exit(f"ERROR: urllib failed ({redact(e)}); curl also failed: {redact(out.stderr.strip()[:200])}")
        body = json.loads(out.stdout)
    if not body.get("ok"):
        sys.exit(f"ERROR: Telegram rejected the message: {redact(body)}")
    print("sent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
