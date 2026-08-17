#!/usr/bin/env python3
"""Open banking (Financy / Open-Finance.ai) -> local SQLite, with per-person ownership attached.

  openbank.py pull            fetch everything into the snapshot DB
  openbank.py owners          show every distinct owner string + how it maps
  openbank.py sql "SELECT.."  query the snapshot (default: pretty table)
  openbank.py schema          tables, columns, views

Read-only against the API. Payments are deliberately not implemented.
"""
import argparse
import json
import os
import pathlib
import sqlite3
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.open-finance.ai"
HERE = pathlib.Path(__file__).parent
ENV = pathlib.Path.home() / ".config/openbank/.env"
DB = pathlib.Path.home() / ".config/openbank/snapshot.db"
OWNERS = HERE.parent / "owners.json"

# ponytail: python.org builds ship no system CA bundle on macOS; certifi is already installed
try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()


# --- config ----------------------------------------------------------------

def load_env():
    if not ENV.is_file():
        sys.exit(f"missing {ENV} - see SKILL.md")
    cfg = {}
    for line in ENV.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            cfg[k.strip()] = v.strip()
    for k in ("FINANCY_CLIENT_ID", "FINANCY_CLIENT_SECRET", "FINANCY_USER_IDS"):
        if not cfg.get(k):
            sys.exit(f"{ENV} is missing {k}")
    cfg["USER_IDS"] = [u.strip() for u in cfg["FINANCY_USER_IDS"].split(",") if u.strip()]
    return cfg


# --- http ------------------------------------------------------------------

def request(url, token=None, body=None, tries=4):
    data = json.dumps(body).encode() if body is not None else None
    # ponytail: Cloudflare in front of the API 403s (code 1010) on python-urllib's UA
    headers = {"Content-Type": "application/json", "Accept": "application/json",
               "User-Agent": "curl/8.7.1"}
    if token:
        headers["Authorization"] = "Bearer " + token
    for attempt in range(tries):
        req = urllib.request.Request(url, data=data, headers=headers,
                                     method="POST" if data else "GET")
        try:
            with urllib.request.urlopen(req, timeout=90, context=SSL_CTX) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:400]
            # ponytail: retry only what retrying can fix; 4xx other than 429 is final
            if e.code not in (429, 500, 502, 503, 504) or attempt == tries - 1:
                raise SystemExit(f"HTTP {e.code} {url}\n{detail}")
        except urllib.error.URLError as e:
            if attempt == tries - 1:
                raise SystemExit(f"network error {url}: {e}")
        time.sleep(2 ** attempt)


def token_for(cfg, user_id):
    r = request(f"{API}/oauth/token", body={
        "clientId": cfg["FINANCY_CLIENT_ID"],
        "clientSecret": cfg["FINANCY_CLIENT_SECRET"],
        "userId": user_id,
    })
    return r["accessToken"]


def paged(token, path, **params):
    """Yield every item across the nextPage cursor."""
    params = {k: v for k, v in params.items() if v is not None}
    params.setdefault("limit", 200)
    cursor = None
    seen_cursors = set()
    while True:
        q = dict(params)
        if cursor:
            q["nextPage"] = cursor
        page = request(f"{API}{path}?" + urllib.parse.urlencode(q), token=token)
        items = page.get("items") or []
        yield from items
        cursor = page.get("nextPage")
        # ponytail: a repeated or absent cursor is the only stop condition the API gives
        if not cursor or cursor in seen_cursors or not items:
            return
        seen_cursors.add(cursor)


# --- ownership -------------------------------------------------------------

def load_owners():
    if not OWNERS.is_file():
        return {"people": {}, "default_person": None}
    return json.loads(OWNERS.read_text())


def name_key(s):
    """Order-insensitive name key: 'דנה כהן' and 'כהן דנה' collide on purpose,
    because banks disagree about which half comes first."""
    return frozenset(w for w in (s or "").lower().replace(",", " ").split() if w)


def split_owner_names(raw):
    """A joint account arrives as one comma-joined string: 'כהן יוסי,כהן דנה'."""
    return [p.strip() for p in (raw or "").split(",") if p.strip()]


def resolve_people(owners, account):
    """-> [(person, source)], one entry per owner. Empty list means unmapped.

    account_ids is the override that always wins; then national_id; then name.
    """
    people = owners.get("people", {})
    acct_id = account.get("id")
    info = account.get("ownerInfo") or {}

    pinned = [p for p, rec in people.items() if acct_id in rec.get("account_ids", [])]
    if pinned:
        return [(p, "account_id") for p in pinned]

    nid = (info.get("nationalId") or "").strip()
    if nid:
        hits = [p for p, rec in people.items()
                if nid in [str(x).strip() for x in rec.get("national_ids", [])]]
        if hits:
            return [(p, "national_id") for p in hits]

    by_name = {}
    for p, rec in people.items():
        for n in rec.get("names", []):
            by_name.setdefault(name_key(n), p)

    found, unmatched = [], []
    for part in split_owner_names(info.get("fullName")):
        person = by_name.get(name_key(part))
        if person and person not in [f[0] for f in found]:
            found.append((person, "name"))
        elif not person:
            unmatched.append(part)
    if found and not unmatched:
        return found
    if found:
        return found + [(None, "partial:" + "|".join(unmatched))]

    default = owners.get("default_person")
    return [(default, "default")] if default else []


# --- db --------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS connections (
  id TEXT PRIMARY KEY, user_id TEXT, provider_id TEXT, status TEXT, mode TEXT,
  customer_id TEXT, start_date TEXT, expiry_date TEXT, last_fetched_at TEXT,
  n_accounts INT, n_cards INT, n_savings INT, n_loans INT, n_securities INT,
  n_transactions INT, raw TEXT);

CREATE TABLE IF NOT EXISTS accounts (
  id TEXT PRIMARY KEY, user_id TEXT, connection_id TEXT, provider_id TEXT,
  account_type TEXT, account_name TEXT, account_number TEXT, currency TEXT,
  owner_name TEXT, owner_national_id TEXT,
  person TEXT, person_source TEXT, persons TEXT, n_owners INT,
  balance REAL, balance_type TEXT, balance_date TEXT,
  credit_limit REAL, card_due_date TEXT, n_transactions INT, is_duplicate INT, raw TEXT);

-- One row per (account, person). A joint account has several rows. Join through this
-- for "everything person X can see"; note sums fan out, so don't SUM across it blindly.
CREATE TABLE IF NOT EXISTS account_owners (
  account_id TEXT, person TEXT, source TEXT, PRIMARY KEY (account_id, person));

CREATE TABLE IF NOT EXISTS transactions (
  sk TEXT PRIMARY KEY, id TEXT, user_id TEXT, account_id TEXT, connection_id TEXT,
  provider_id TEXT, type TEXT, merchant_name TEXT, description TEXT,
  amount REAL, currency TEXT, original_amount REAL,
  category_main TEXT, category_sub TEXT, changed_category_main TEXT, changed_category_sub TEXT,
  classification TEXT, tx_date TEXT, booking_date TEXT, value_date TEXT,
  installment_n INT, installment_total INT, balance_end_day REAL,
  is_duplicate INT, raw TEXT);

CREATE TABLE IF NOT EXISTS pulls (started_at TEXT, user_id TEXT, note TEXT);

CREATE INDEX IF NOT EXISTS ix_tx_account ON transactions(account_id);
CREATE INDEX IF NOT EXISTS ix_tx_date ON transactions(tx_date);
CREATE INDEX IF NOT EXISTS ix_tx_cat ON transactions(category_main, category_sub);
CREATE INDEX IF NOT EXISTS ix_acc_person ON accounts(person);

-- START HERE for almost every question. Exactly one row per transaction, so SUM() is
-- safe. `person` is the primary owner; `persons` lists all of them for a joint account.
CREATE VIEW IF NOT EXISTS v_tx AS
-- ponytail: bank CHECKING rows (leumi) carry no transactionDate, only booking/value
SELECT t.sk, COALESCE(t.tx_date, t.booking_date, t.value_date) AS tx_date, t.booking_date,
       a.person, a.persons, a.n_owners, a.owner_name,
       a.account_type, a.account_name, a.provider_id,
       t.merchant_name, t.description,
       t.amount, t.currency,
       COALESCE(t.changed_category_main, t.category_main) AS category_main,
       COALESCE(t.changed_category_sub,  t.category_sub)  AS category_sub,
       t.installment_n, t.installment_total, t.type,
       t.account_id, t.connection_id, t.user_id
FROM transactions t LEFT JOIN accounts a ON a.id = t.account_id
WHERE COALESCE(t.is_duplicate, 0) = 0;

-- Fan-out view: a joint transaction appears once PER OWNER. Use it to answer
-- "show me everything the second person is a party to"; never SUM() a total off it.
CREATE VIEW IF NOT EXISTS v_tx_by_owner AS
SELECT ao.person AS owner, ao.source AS owner_source, t.*
FROM v_tx t JOIN account_owners ao ON ao.account_id = t.account_id;

-- One row per account, with its owners resolved.
CREATE VIEW IF NOT EXISTS v_person_accounts AS
SELECT COALESCE(person, '(unmapped)') AS person, persons, n_owners,
       account_type, provider_id, account_name, owner_name,
       balance, currency, n_transactions, id AS account_id
FROM accounts WHERE COALESCE(is_duplicate, 0) = 0;
"""


def db_open():
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    return con


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def first_balance(acc):
    """Prefer closingBooked at the latest referenceDate; fall back to whatever exists."""
    bals = acc.get("balances") or []
    rows = []
    for b in bals:
        amt = b.get("balanceAmount") or {}
        rows.append((b.get("balanceType"), num(amt.get("amount")), b.get("referenceDate")))
    rows = [r for r in rows if r[1] is not None]
    if not rows:
        return None, None, None
    booked = [r for r in rows if r[0] == "closingBooked"]
    pool = booked or rows
    best = max(pool, key=lambda r: (r[2] or ""))
    return best[1], best[0], best[2]


# --- commands --------------------------------------------------------------

def cmd_pull(args):
    cfg = load_env()
    owners = load_owners()
    con = db_open()
    started = time.strftime("%Y-%m-%dT%H:%M:%S")
    totals = {"connections": 0, "accounts": 0, "transactions": 0}

    for user_id in cfg["USER_IDS"]:
        print(f"== {user_id}", file=sys.stderr)
        token = token_for(cfg, user_id)

        conns = list(paged(token, "/v2/connections"))
        for c in conns:
            con.execute("""INSERT OR REPLACE INTO connections VALUES
                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
                c.get("id"), user_id, c.get("providerId"), c.get("status"), c.get("mode"),
                c.get("customerId"), c.get("startDate"), c.get("expiryDate"),
                c.get("lastFetchedAt") or c.get("lastFetchedDataDate"),
                c.get("accounts"), c.get("cards"), c.get("savings"), c.get("loans"),
                c.get("securities"), c.get("transactions"), json.dumps(c, ensure_ascii=False)))
        totals["connections"] += len(conns)
        print(f"   connections: {len(conns)}", file=sys.stderr)

        accs = list(paged(token, "/v2/data/accounts",
                          includeDuplicates=1 if args.include_duplicates else None))
        for a in accs:
            info = a.get("ownerInfo") or {}
            resolved = resolve_people(owners, a)
            named = [(p, s) for p, s in resolved if p]
            person = named[0][0] if named else None
            source = ";".join(s for _, s in resolved) or "unmapped"
            bal, btype, bdate = first_balance(a)
            cl = a.get("creditLimit") or {}
            con.execute("""INSERT OR REPLACE INTO accounts VALUES
                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
                a.get("id"), user_id, a.get("connectionId"), a.get("providerId"),
                a.get("accountType"), a.get("accountName"), a.get("accountNumber"),
                a.get("currency"), info.get("fullName"), info.get("nationalId"),
                person, source, ",".join(p for p, _ in named) or None, len(named),
                bal, btype, bdate,
                num(cl.get("amount")), a.get("cardDueDate"), a.get("transactions"),
                1 if a.get("isDuplicate") else 0, json.dumps(a, ensure_ascii=False)))
            con.execute("DELETE FROM account_owners WHERE account_id = ?", (a.get("id"),))
            for p, s in named:
                con.execute("INSERT OR REPLACE INTO account_owners VALUES (?,?,?)",
                            (a.get("id"), p, s))
        totals["accounts"] += len(accs)
        print(f"   accounts: {len(accs)}", file=sys.stderr)

        n = 0
        for t in paged(token, "/v2/data/transactions",
                       dateFrom=args.date_from, dateTo=args.date_to,
                       includeDuplicates=1 if args.include_duplicates else None):
            amt = t.get("amount") or {}
            charged = amt.get("chargedAmount") or {}
            original = amt.get("originalAmount") or {}
            cat = t.get("category") or {}
            chg = t.get("changedCategory") or {}
            d = t.get("date") or {}
            desc = t.get("description") or {}
            inst = t.get("installments") or {}
            klass = t.get("classification") or {}
            con.execute("""INSERT OR REPLACE INTO transactions VALUES
                (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (
                t.get("SK"), t.get("id"), user_id, t.get("accountId"), t.get("connectionId"),
                t.get("providerId"), t.get("type"), t.get("merchantName"),
                desc.get("description") if isinstance(desc, dict) else desc,
                num(charged.get("amount")), charged.get("currency"), num(original.get("amount")),
                cat.get("main"), cat.get("sub"), chg.get("main"), chg.get("sub"),
                klass.get("type") if isinstance(klass, dict) else klass,
                d.get("transactionDate"), d.get("bookingDate"), d.get("valueDate"),
                inst.get("number"), inst.get("total"), num(t.get("balancePerEndDay")),
                1 if t.get("isDuplicate") else 0, json.dumps(t, ensure_ascii=False)))
            n += 1
            if n % 500 == 0:
                con.commit()
                print(f"   transactions: {n}...", file=sys.stderr)
        totals["transactions"] += n
        print(f"   transactions: {n}", file=sys.stderr)

        con.execute("INSERT INTO pulls VALUES (?,?,?)",
                    (started, user_id, json.dumps(totals)))
        con.commit()

    con.close()
    print(f"\n{DB}")
    print(json.dumps(totals, indent=1))
    unmapped = query(f"SELECT COUNT(*) FROM accounts WHERE person IS NULL")[1]
    if unmapped and unmapped[0][0]:
        print(f"\n{unmapped[0][0]} account(s) have no person. Run: openbank.py owners", file=sys.stderr)


def query(sql, params=()):
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    try:
        cur = con.execute(sql, params)
        return [d[0] for d in (cur.description or [])], cur.fetchall()
    finally:
        con.close()


def table(cols, rows, limit=200):
    if not rows:
        return "(no rows)"
    rows = rows[:limit]
    cells = [[("" if v is None else str(v)) for v in r] for r in rows]
    widths = [max(len(str(c)), *(len(r[i]) for r in cells)) for i, c in enumerate(cols)]
    out = ["  ".join(str(c).ljust(w) for c, w in zip(cols, widths)),
           "  ".join("-" * w for w in widths)]
    out += ["  ".join(c.ljust(w) for c, w in zip(r, widths)) for r in cells]
    return "\n".join(out)


def cmd_owners(args):
    owners = load_owners()
    cols, rows = query("""
        SELECT COALESCE(person,'(unmapped)') AS person, person_source,
               owner_name, owner_national_id, COUNT(*) n_accounts,
               GROUP_CONCAT(DISTINCT account_type), GROUP_CONCAT(DISTINCT provider_id)
        FROM accounts GROUP BY 1,2,3,4 ORDER BY 1,5 DESC""")
    print(table(cols, rows))
    print(f"\nmapping file: {OWNERS}")
    print("people defined: " + (", ".join(owners.get("people", {})) or "(none)"))
    print("Add an owner_name / owner_national_id / account id to a person's list, then re-run `pull`.")


def cmd_sql(args):
    cols, rows = query(args.sql)
    if args.json:
        print(json.dumps([dict(zip(cols, r)) for r in rows], ensure_ascii=False, indent=1,
                         default=str))
    else:
        print(table(cols, rows, args.limit))
        if len(rows) > args.limit:
            print(f"... {len(rows)} rows total, {args.limit} shown (--limit to raise)")


def cmd_schema(args):
    cols, rows = query(
        "SELECT type, name FROM sqlite_master WHERE type IN ('table','view') ORDER BY type, name")
    for typ, name in rows:
        c, r = query(f"SELECT name, type FROM pragma_table_info('{name}')")
        print(f"\n{typ} {name}")
        print("  " + ", ".join(f"{n} {t}" for n, t in r))
    _, counts = query("SELECT (SELECT COUNT(*) FROM connections), (SELECT COUNT(*) FROM accounts),"
                      " (SELECT COUNT(*) FROM transactions)")
    print(f"\nrows: connections={counts[0][0]} accounts={counts[0][1]} transactions={counts[0][2]}")
    _, last = query("SELECT started_at, user_id, note FROM pulls ORDER BY started_at DESC LIMIT 3")
    for r in last:
        print("pull:", *r)


def cmd_selfcheck(args):
    """The ownership resolver is the only non-obvious logic here, so it gets the check."""
    owners = {"default_person": None, "people": {
        "dana": {"names": ["דנה כהן", "DANA COHEN"], "national_ids": ["123"],
                  "account_ids": ["PINNED"]},
        "yossi": {"names": ["יוסי כהן"], "national_ids": [], "account_ids": ["PINNED"]},
    }}

    def r(acc):
        return sorted(resolve_people(owners, acc), key=lambda t: (str(t[0]), t[1]))

    # name order differs per bank; both spellings must land on the same person
    assert r({"ownerInfo": {"fullName": "כהן דנה"}}) == [("dana", "name")]
    assert r({"ownerInfo": {"fullName": "  dana   cohen "}}) == [("dana", "name")]
    # joint account: one comma-joined string, two owners
    assert r({"ownerInfo": {"fullName": "כהן יוסי,כהן דנה"}}) == \
        [("dana", "name"), ("yossi", "name")]
    # a product name is nobody
    assert r({"ownerInfo": {"fullName": "מפתח"}}) == []
    # account_ids overrides everything, and can name several people
    assert r({"id": "PINNED", "ownerInfo": {"fullName": "מפתח"}}) == \
        [("dana", "account_id"), ("yossi", "account_id")]
    # national_id beats name
    assert r({"ownerInfo": {"fullName": "מפתח", "nationalId": "123"}}) == \
        [("dana", "national_id")]
    # a half-recognised joint string keeps the hit AND flags the leftover
    partial = r({"ownerInfo": {"fullName": "כהן דנה,מישהו אחר"}})
    assert ("dana", "name") in partial and any(
        p is None and s.startswith("partial:") for p, s in partial), partial
    # unknown owner with no default is unmapped, never silently assigned
    assert r({"ownerInfo": {"fullName": "פלוני אלמוני"}}) == []
    assert resolve_people({"default_person": "me", "people": {}},
                          {"ownerInfo": {}}) == [("me", "default")]

    # balance picking: latest closingBooked wins over a forward-dated 'expected'
    acc = {"balances": [
        {"balanceType": "closingBooked", "balanceAmount": {"amount": "1.00"},
         "referenceDate": "2026-08-17"},
        {"balanceType": "expected", "balanceAmount": {"amount": "999.00"},
         "referenceDate": "2027-07-15"},
        {"balanceType": "closingBooked", "balanceAmount": {"amount": "2.00"},
         "referenceDate": "2026-08-01"}]}
    assert first_balance(acc) == (1.0, "closingBooked", "2026-08-17"), first_balance(acc)
    assert first_balance({"balances": []}) == (None, None, None)
    # no closingBooked at all -> fall back rather than report nothing
    assert first_balance({"balances": [
        {"balanceType": "expected", "balanceAmount": {"amount": "5"},
         "referenceDate": "2026-01-01"}]}) == (5.0, "expected", "2026-01-01")

    print("selfcheck ok")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("pull", help="fetch everything into the snapshot DB")
    q.add_argument("--date-from", help="YYYY-MM-DD (default: all history the bank gave)")
    q.add_argument("--date-to", help="YYYY-MM-DD")
    q.add_argument("--include-duplicates", action="store_true")
    q.set_defaults(fn=cmd_pull)

    o = sub.add_parser("owners", help="show owner strings and how they map to people")
    o.set_defaults(fn=cmd_owners)

    s = sub.add_parser("sql", help="query the snapshot")
    s.add_argument("sql")
    s.add_argument("--json", action="store_true")
    s.add_argument("--limit", type=int, default=200)
    s.set_defaults(fn=cmd_sql)

    c = sub.add_parser("schema", help="tables, columns, views, row counts")
    c.set_defaults(fn=cmd_schema)

    k = sub.add_parser("selfcheck", help="assert the ownership/balance logic still holds")
    k.set_defaults(fn=cmd_selfcheck)

    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
