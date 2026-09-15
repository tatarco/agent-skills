---
name: telegram-notify
description: Send the user a Telegram message about ANYTHING from ANY session — notify, ping, alert, "let me know when", "tell me on telegram". General-purpose, not tied to any one project. Works from a local machine or a remote/cloud box.
---

# telegram-notify

Send an arbitrary message to the user's Telegram via their personal bot. This is
a general notification channel: any session, any task, any machine. Whenever the
user wants to be told something on Telegram — a job finished, a deploy is done, a
long task on a cloud instance completed, a value crossed a threshold — use this.

## How to send

Run the bundled sender with the message as the argument:

```bash
python3 ~/.claude/skills/telegram-notify/send.py "✅ Build passed on main"
```

Pick a short, useful message. Emoji are fine. For multi-line, pass a single
quoted string with real newlines, or pipe via stdin:

```bash
printf '%s\n' "Deploy done" "3 services updated" | python3 ~/.claude/skills/telegram-notify/send.py
```

Report back to the user whether the send succeeded (the script prints `sent`)
or the error it returned.

## Credentials

The script reads `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from env vars, or
from `~/.claude/telegram-notify.env` (KEY=VALUE lines). If it errors with
"missing Telegram credentials", that file has not been set up yet — ask the user
for their bot token and chat ID, then create the file:

```
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_CHAT_ID=123456789
```

To get these: message **@BotFather** → `/newbot` for the token; send the bot a
message, then open `https://api.telegram.org/bot<TOKEN>/getUpdates` and read
`chat.id` for the chat ID.

## Remote / cloud machines

If you are on a box that does not have this script (e.g. an SSH'd cloud
instance), send directly with `curl` — just supply the token + chat ID from the
user's `~/.claude/telegram-notify.env` or ask for them:

```bash
curl -s "https://api.telegram.org/bot<TOKEN>/sendMessage" \
  --data-urlencode "chat_id=<CHAT_ID>" --data-urlencode "text=your message"
```

## Scope

This skill only *sends* messages. It does not poll, schedule, or receive. For
recurring/scheduled notifications, pair it with a cron/GitHub Action that calls
the sender (see the `gal-automations` repo for a working example).
