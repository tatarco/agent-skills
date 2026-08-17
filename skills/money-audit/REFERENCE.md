# money-audit reference

## The query playbook

Everything starts from `v_tx` (one row per transaction, person + account joined, duplicates excluded).

```sql
-- 1. the map: who has what, and what is it worth
SELECT person, provider_id, account_type, account_name, balance, currency
FROM v_person_accounts ORDER BY person, balance;

-- 2. spend per person per month - the sanity check before anything else
SELECT person, substr(tx_date,1,7) month, ROUND(SUM(-amount),2) spent
FROM v_tx WHERE amount < 0 GROUP BY 1,2 ORDER BY 2 DESC;

-- 3. recurring charges: same merchant, in most months
SELECT merchant_name, COUNT(*) n, COUNT(DISTINCT substr(tx_date,1,7)) months,
       ROUND(AVG(-amount),2) avg_amount, ROUND(SUM(-amount),2) total
FROM v_tx WHERE amount < 0 AND merchant_name IS NOT NULL
GROUP BY 1 HAVING months >= 3 ORDER BY total DESC;

-- 4. the payment processors hide the real merchant - open them up
SELECT tx_date, person, description, merchant_name, -amount amt
FROM v_tx WHERE amount < 0
  AND (description LIKE '%PAYPAL%' OR description LIKE '%פייפאל%'
       OR description LIKE '%GOOGLE%' OR description LIKE '%APPLE%')
ORDER BY tx_date DESC;

-- 5. cash out of the system: ATM + counter withdrawals
SELECT person, substr(tx_date,1,7) month, ROUND(SUM(-amount),2) cash
FROM v_tx WHERE amount < 0
  AND (description LIKE '%כספומט%' OR description LIKE '%ATM%'
       OR category_sub LIKE '%withdraw%')
GROUP BY 1,2 ORDER BY 2 DESC;

-- 6. insurance stacking: several policies, same risk
SELECT person, merchant_name, COUNT(DISTINCT substr(tx_date,1,7)) months,
       ROUND(AVG(-amount),2) monthly
FROM v_tx WHERE amount < 0 AND (category_main LIKE '%insur%'
       OR description LIKE '%ביטוח%')
GROUP BY 1,2 HAVING months >= 3 ORDER BY 1, monthly DESC;

-- 7. the one that matters: debt next to idle cash
SELECT person, account_type, account_name, balance FROM v_person_accounts
WHERE account_type IN ('loan','credit','checking','savings') ORDER BY balance;
```

## Traps

**Loan snapshots.** Israeli card issuers report a revolving product (CAL `CALCHOICE`, `סל`) as one row per monthly cycle: same `accountNumber`, different `contractStartDate`. Summing them multiplies the debt by the number of cycles on file.

```sql
-- WRONG: SELECT SUM(balance) FROM accounts WHERE account_type='loan';
-- RIGHT:
WITH latest AS (
  SELECT account_number, MAX(reference_date) rd FROM accounts
  WHERE account_type='loan' GROUP BY 1)
SELECT a.person, a.account_number, a.balance FROM accounts a
JOIN latest l ON l.account_number=a.account_number AND l.rd=a.reference_date;
```

**Bilingual owner strings.** The same person is `כהן דנה` at one bank and `DANA COHEN` at another. Filtering on the raw owner name drops whole cards. Always filter on the resolved `person`.

**Joint accounts fan out.** `v_tx_by_owner` emits one row per owner per transaction - correct for "everything this person is party to", wrong for any total. Use `v_tx` to sum.

**Booking date vs value date.** Cash and card totals move by thousands depending on which you use. Pick one, say which one in the output.

**Balance types.** An account carries several balances; a forward-dated `expected` will beat a current `closingBooked` if you take the first one. The script picks the latest `closingBooked` and falls back only if there is none.

**Interest is not a transaction at all.** Revolving interest is already inside the carried balance - it is not a merchant, not a fee row, not anything a transaction query will return. Read the rate off the credit/loan account fields, then compute the monthly cost yourself and the doubling time (`ln 2 / ln(1+r)`); the person has never seen either number written down. This is the highest-value finding in a household audit and the only one invisible to every budgeting app, because they all read transactions.

**Insurance duplication is not automatically waste.** Reimbursement clauses (שיפוי) pay an incurred expense once regardless of how many policies cover it. Compensation clauses (פיצוי - long-term care, critical illness) pay a fixed sum from every insurer in parallel. Classify each policy before recommending a cancellation.

## The verification pass

This is the part worth copying. Before any finding reaches the person whose money it is:

1. **Re-derive independently.** A second agent gets the raw data and the claim, not the query. If it cannot reproduce the number from scratch, the number is not real yet.
2. **Attack the aggregation.** For every total, ask: could one entity be represented more than once? (That is the snapshot trap.) Could one be missing because of a name, a currency, a date basis?
3. **Check ground truth before accusing.** A charge that looks like a scam may be a real supplier. The mailbox settles it - order confirmations, delivery notices. Two merchants flagged as fraud in the real run were legitimate, and only the emails proved it.
4. **Disagreement is data.** When the verifier disagreed, it was right once and wrong once. The wrong one had filtered by a Hebrew owner name and lost the cards spelled in Latin. Resolve disagreements by going back to rows, not by voting.

Three independent passes cost a few cents of tokens each. Most people never get a second opinion on their money; here the second, third and fourth are cheaper than the coffee you drink while reading them.

## Handing the findings over

A wall of findings changes nothing. What worked:

- One line per item: what it is, what it costs a month, the action.
- Sorted by monthly recovery, not by how alarming it is.
- The things needing their password or their phone separated from the things you can do.
- Written in their language, on one page they can tick off.
- Nothing cancelled without an item-by-item yes.
