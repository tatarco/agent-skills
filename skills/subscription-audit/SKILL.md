---
name: subscription-audit
description: Audit a person's mailbox, app stores and invoice PDFs for recurring charges they no longer want or never knew about, then cancel them and claim refunds. Finds fleeceware, duplicate subscriptions, lapsed-discount price creep and charges hidden inside phone bills. Use when auditing someone's spending, "what is he paying for", "find subscriptions to cancel", helping an elderly parent or relative with money leaking out, suspected fleeceware or app-store scam charges, cancelling a subscription with no cancel button, or claiming a refund for unauthorised charges.
---

# Subscription audit

Find every recurring charge on someone's accounts, decide what should die, kill it, and get money back.

Built for the common case: a parent or relative whose money leaks to things they don't use, don't understand, or never agreed to.

## The rule that governs everything

**Never cancel or spend on someone's behalf without their explicit approval, item by item.** Present a list, get a decision, then act. The exception is nothing — "clean it all up" is not approval for a specific cancellation.

Marketing unsubscribes are the one safe default.

## Workflow

### 1. Get read access to the mailbox

The mailbox is where the evidence lives. Use the `gmail` skill's CLI with a second token so their account never becomes the default:

```bash
GMAIL_TOKEN=token_<name>.json python3 ~/.claude/skills/gmail/gmail_cli.py auth
```

One browser consent by someone who has their password. Prefix every later command with the same `GMAIL_TOKEN`.

### 2. Sweep for billing signals

```bash
GMAIL_TOKEN=token_<name>.json bash ~/.claude/skills/subscription-audit/scripts/sweep.sh
```

Ranks senders by frequency across receipt/invoice/renewal/processor/app-store queries. **Read the sender histogram, not the individual mails** — recurring payees rise to the top on their own.

### 3. Harvest and parse the invoice PDFs

Amounts usually live in attachments, not email bodies.

```bash
GMAIL_TOKEN=token_<name>.json bash ~/.claude/skills/subscription-audit/scripts/harvest.sh "from:<sender> newer_than:13m"
python3 ~/.claude/skills/subscription-audit/scripts/parse.py pdfs/
```

### 4. Open the app-store and vendor accounts

App-store subscriptions rarely email a cancel link. Drive the real account with the `ego-browser` skill and their login. See [REFERENCE.md](REFERENCE.md) for the account URLs and the patterns that keep this from wasting an hour.

### 5. Build the ledger, then ask

Produce one table: payee, amount, cadence, annualised, card, verdict. Mark every figure **confirmed** (read off an invoice) or **estimated**. Never blur the two — the estimated numbers are the ones that embarrass you later.

Then hand it over for approval.

### 6. Cancel, and verify each one

Re-read the account page after every cancellation. A cancellation you didn't confirm on screen did not happen.

### 7. Claim refunds

See [REFERENCE.md](REFERENCE.md#refunds). The winning argument is almost never "he changed his mind" — it's **"the service was never delivered"**, which sits outside refund-window rules.

### 8. Verify before you share

If you publish a summary, dispatch an independent skeptic to re-derive every figure from the raw evidence before sending it. Require zero critical findings. Arithmetic errors in a financial document destroy the credibility of the true findings around them.

## What people miss

- **The phone bill.** Operators fold appliance instalments and add-ons into it. Compare the total against the service lines; the gap is the story.
- **Duplicates.** Two of the same product, two fitness apps, an add-on already included in the tier above it.
- **Lapsed discounts.** "Continuation benefit" expires quietly and the price doubles. Find the expiry date before it arrives.
- **Geo-dead features.** Roadside assistance and identity monitoring are frequently US-only and worthless abroad.
- **Zero-usage subscriptions.** "0 devices protected", "0 of 1 devices used" — pure refund leverage.
- **Backup payment cards**, which keep billing alive through declines.

## Honesty rules

- Do not claim to **be** the account holder to a support agent. "I manage this account for my father" works and costs nothing. A false identity claim is the thread that unravels a later chargeback.
- Report inferences as inferences.
- Statements from banks and card issuers are usually **not** in email. Say so plainly rather than implying the audit is complete without them.

## Sensitive material

Mailboxes contain medical and legal correspondence. Read only what the audit needs, and exclude it from any shared document.
