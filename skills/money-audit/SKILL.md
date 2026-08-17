---
name: money-audit
description: Pull a household's real bank, credit-card and loan data into a local SQLite snapshot through an open-banking aggregator, attribute every account to a person, then investigate it with SQL - debt and its true interest rate, idle cash sitting next to expensive credit, recurring charges, PayPal billing agreements, duplicated insurance. Use when someone asks to audit a family member's finances, "where is the money going", "how much do my parents actually owe", find hidden subscriptions or interest, or before giving anyone financial advice based on statements.
---

# Money audit

Bank statements are the wrong interface for this. A PDF per month per account, times nine institutions, is not something a person or an agent reads well. Get the same data as rows, put it in SQLite, and ask questions in SQL.

This skill is the pipeline plus - more importantly - the two traps that will make you tell someone a wrong number about their own money.

## The rule that governs everything

**Verify before you frighten anyone.** A financial finding is not done when the query returns. It is done when an independent pass has re-derived it from the raw data and agreed. See `REFERENCE.md` → *The verification pass*. The first run of this audit reported ILS 350,000 of loans. The real number was ILS 70,000. Nobody was told the wrong one, and that is the only part of this worth copying.

Also: read-only. Aggregators offer payment initiation endpoints. Do not implement them, do not call them.

## What it costs (it is not free)

| Thing | Cost |
|---|---|
| Open-banking aggregator (Israel: Financy / Open-Finance.ai, Starter) | ~ILS 49/mo, cancel after |
| The agent time for a real 2-person, 9-institution audit | ~2,000 assistant turns. At Claude API list prices that is on the order of USD 1,000-1,700; on a Claude Max subscription it is inside the monthly fee |

The API bill is the honest part. This is not a weekend hack that costs nothing - it is a few hundred to a few thousand dollars of model time if you pay per token, and it recovered ILS 3,000-4,500 a month.

**Why an aggregator and not the bank's API:** in Israel (חוק שירות מידע פיננסי, live 2023) bank APIs open only to an ISA-licensed information-service provider. There is no consumer tier. You are renting a licence, not paying for a wrapper. In the EU/UK, PSD2 AISP licensing works the same way; the aggregator changes, the shape does not. For *your own* accounts only, scrapers like `israeli-bank-scrapers` are the free path and break whenever a bank redesigns.

## Setup

1. The account holder links their banks and cards in the aggregator's UI. There is no API for linking, and there should not be.
2. Credentials in `~/.config/openbank/.env`:

```
FINANCY_CLIENT_ID=...
FINANCY_CLIENT_SECRET=...
FINANCY_USER_IDS=user_xxx,user_yyy
```

3. Copy `owners.example.json` to `owners.json` next to the script and map each owner string the banks return to a person.

```bash
python3 scripts/openbank.py pull        # API -> ~/.config/openbank/snapshot.db
python3 scripts/openbank.py owners      # every owner string + who it maps to
python3 scripts/openbank.py schema      # tables, views, row counts, last pull
python3 scripts/openbank.py sql "..."   # investigate
python3 scripts/openbank.py selfcheck   # the ownership resolver still holds
```

`pull` is `INSERT OR REPLACE` on stable ids, so re-running never duplicates.

## Start every investigation with `v_tx`

One row per transaction, person and account already joined, duplicates excluded. `SUM()` on it is safe. Query playbook, trap list and the verification protocol: `REFERENCE.md`.

## The two traps, in short

**1. A revolving card reports as many monthly snapshots of itself.** Same account number, one row per month. `SUM()` over them multiplies the debt by the number of months on file - 13 snapshots read as 13 loans. True balance is the **latest snapshot per distinct account number**. This is what produced the 10x error.

**2. Owner strings are dirty and bilingual.** The same person appears as `כהן דנה` on one bank and `DANA COHEN` on another. Query by the resolved `person` column, never by the raw owner name, or one card silently disappears from the total.

## What it actually finds

In one real household, none of it visible from any single statement:

- A revolving card at 17.7% rolling since 2006 - the single most valuable find, and the hardest. It has **no schedule and no end date**, doubles every 4.3 years, is not a line item on any statement (the interest is already inside the balance), and is not a charge, so no transaction search will ever surface it. Look in the account fields, not the transactions.
- Idle cash in checking, earning nothing, larger than half the debt it could kill.
- PayPal **billing agreements** - not subscriptions - still authorised for suppliers the person forgot ordering from years ago. They renew without a merchant email.
- Stacked private health policies. **Do not call this waste before sorting the clauses:** reimbursement cover (שיפוי - surgery, medication) pays once no matter how many policies exist, but compensation cover (פיצוי - long-term care, critical illness) pays in full from *every* insurer holding one. Cancelling a "duplicate" compensation policy destroys real money.
- Weekly app-store fleeceware, which the companion [`subscription-audit`](../subscription-audit/) skill kills and claims refunds for.

## Before you present anything

- Never state a number you did not get from a query.
- Run the verification pass (`REFERENCE.md`). Two of the findings in the real run were wrong: a merchant flagged as a scam turned out to be a legitimate supplier, confirmed only by reading the order-confirmation emails. **Check the ground truth before accusing anyone of anything.**
- Present as decisions, not as a report: one line per finding, the amount, and the action to approve.
- Never commit `owners.json`, the snapshot DB or anything under `~/.config/openbank/`.
