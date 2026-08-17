# Subscription audit — reference

## Account URLs that actually work

| Vendor | Where subscriptions live | Cancel path |
|---|---|---|
| Google Play | `play.google.com/store/account/subscriptions` | Manage → Cancel subscription → decline the pause offer → reason → confirm |
| Google Play refunds | `support.google.com/googleplay/workflow/9813244` | Self-service, **one claim per charge** |
| Apple | `apps.apple.com/account/subscriptions` | Requires the Apple ID session |
| Microsoft consumer | `account.microsoft.com/services` | Cancel there |
| Microsoft business tenant | `admin.microsoft.com` → Billing → Your products | Needs Global Admin. Check nothing else depends on the tenant first |
| McAfee | `myaccount.mcafee.com` → Subscriptions | "Cancel" → "Cancel auto-renewal" |
| Avast / Norton (Gen Digital) | `myaccount.avast.com` / `my.norton.com` | Per-subscription "Manage subscription" → Unsubscribe. **Not on the list view** |
| Netflix | `netflix.com/YourAccount` | Plan details shows the tier |
| Zoom | `zoom.us/account/billing` | |

Multi-account browsers: append `?authuser=N` to Google URLs and check which index is the target account before acting.

## Gmail queries that surface recurring payees

```
newer_than:13m (subject:receipt OR subject:invoice OR subject:renewal OR subject:renew)
newer_than:13m (from:2checkout OR from:cleverbridge OR from:paddle OR from:nexway OR from:digitalriver OR from:fastspring)
newer_than:13m (from:googleplay-noreply@google.com)
newer_than:13m (from:apple.com subject:(receipt OR subscription))
newer_than:13m from:paypal
newer_than:13m has:attachment filename:pdf (subject:(invoice OR statement))
newer_than:13m (subject:(subscription OR renewed OR "auto-renew" OR membership))
```

Localise the subject terms. Hebrew: `חשבונית` `קבלה` `חיוב` `מנוי` `הוראת קבע` `תשלום`.

Then: **rank senders by count.** A payee that mails monthly for a year outranks anything else in the inbox.

## Reading app-store receipts

Google Play receipts state price, cadence, developer, order number and card. Weekly cadence on a utility app is the fleeceware signature — a QR scanner or "photo recovery" tool at a weekly price is never legitimate.

Watch the **times of day**: several subscriptions billing at fixed weekly slots produce clusters like `Fri 07:56`, `Wed 09:49`. Each cluster is one subscription.

## Driving the account pages

Modal dialogs on Google Play and similar SPAs are **invisible to `document.body.innerText` and to the accessibility tree**. They render, but you cannot read or query them.

- Screenshot, locate the control visually, click by coordinate.
- Dialog geometry shifts with content — a card with a "Pause payments" option puts "Cancel subscription" lower than one without. **Re-screenshot per subscription** rather than reusing coordinates.
- Native `<select>` needs the React-safe setter:
  ```js
  const set = Object.getOwnPropertyDescriptor(window.HTMLSelectElement.prototype,'value').set
  set.call(el, val); el.dispatchEvent(new Event('change',{bubbles:true}))
  ```
- Widgets that render below the fold need a taller viewport:
  ```js
  await cdp('Emulation.setDeviceMetricsOverride', {width:1400, height:1700, deviceScaleFactor:1, mobile:false})
  ```
- Lists **reorder** as items are cancelled. Re-resolve the target each iteration; never batch positional clicks.

## Getting in without the password

Many vendors offer **one-time passcode sign-in**. With mailbox read access, that is the whole login:

1. Choose "sign in with a one-time passcode"
2. Enter their email
3. Read the code with the `gmail` CLI
4. Submit

Cleaner than a password reset — it changes nothing on the account.

CAPTCHAs and payment authorisations stop here. Hand control back.

## Refunds

**Frame it as service-not-delivered, not buyer's remorse.** Refund windows govern changed minds. They do not govern a product that was never activated.

Evidence that works:
- "0 devices protected" / "0 of 1 devices used"
- Two concurrent subscriptions to the same product at different prices
- A price that started as a promo and multiplied
- Charge frequency escalating with no change in use

Windows worth knowing (verify, they change): Google Play 48h self-service then agent discretion; Avast 30 days; McAfee 30 days new / 60 days on an auto-renewal; Microsoft prorated in some countries.

Ask for the confirmation email and a case reference, then **verify it arrived in the mailbox**. An agent saying "processed" is not proof.

If the vendor's own cancel flow does not exist — Avast is the standard example — the routes are: their support chat, the payment processor's portal (Nexway, Cleverbridge, 2Checkout), or blocking the merchant at the card issuer.

## Beyond subscriptions

- **Telecom bills**: compare the invoice total against the sum of the service lines. Equipment instalments, insurance and add-ons hide in the gap. Check the per-item monthly figure × term against retail price.
- **Card statements are not in email.** They need portal logins or paper. Say so rather than implying the audit is complete.
- **Multiple cards** mean multiple blind spots. List every card seen and which payee used it; the ones you never see are where the unknown charges are.
