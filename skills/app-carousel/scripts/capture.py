#!/usr/bin/env python3
"""Drive a live web app through a flow and screenshot each step.

Reads a flow.json. Never types credentials — a gated app must be logged into by the
user, whose session is then replayed via `storage` (see SKILL.md).
"""
import argparse
import json
import pathlib
import sys

from playwright.sync_api import sync_playwright

# Same phrases that ate an hour in the field: click the CONTROL, not body copy that
# happens to contain the phrase.
DISMISS_DEFAULT = ["Continue", "Skip", "Close", "Got it", "Accept",
                   "המשיכו כאן בכל זאת", "אני רוצה להמשיך בדפדפן", "דלג", "סגור"]


def dismiss(page, labels):
    for _ in range(5):
        hit = False
        for label in labels:
            for sel in (f'button:has-text("{label}")',
                        f'a:has-text("{label}")',
                        f'[role="button"]:has-text("{label}")'):
                el = page.locator(sel)
                if el.count() and el.first.is_visible():
                    el.first.click()
                    page.wait_for_timeout(700)
                    hit = True
                    break
        if not hit:
            return


def blur_selectors(page, selectors):
    """Blur sensitive nodes IN THE PAGE before the screenshot — far more reliable
    than trying to find them again with OCR afterwards."""
    for sel in selectors or []:
        page.eval_on_selector_all(
            sel,
            "els => els.forEach(e => { e.style.filter = 'blur(14px)';"
            " e.style.userSelect = 'none'; })",
        )


def blur_text(page, patterns):
    """Blur every LEAF element whose text matches a regex.

    Selectors break the moment the markup changes, and real apps scatter personal data
    across dozens of components. Matching the *content* (names, money, dates, emails) is
    what actually holds up.
    """
    if not patterns:
        return
    page.evaluate(
        """(pats) => {
            const res = pats.map(p => new RegExp(p, 'iu'));
            document.querySelectorAll('*').forEach(el => {
                if (el.children.length) return;               // leaves only
                const t = (el.textContent || '').trim();
                if (!t) return;
                if (res.some(r => r.test(t))) {
                    el.style.filter = 'blur(9px)';
                    el.style.userSelect = 'none';
                }
            });
        }""",
        patterns,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("flow", help="flow.json")
    ap.add_argument("-o", "--out", default="shots", help="output dir")
    args = ap.parse_args()

    flow = json.loads(pathlib.Path(args.flow).read_text())
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    vp = flow.get("viewport", {"width": 430, "height": 932})
    dpr = flow.get("device_scale_factor", 3)
    dismiss_labels = flow.get("dismiss", DISMISS_DEFAULT)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Phone-sized viewport but a DESKTOP user-agent on purpose: an iOS UA makes many
        # PWAs show an "add to home screen" interstitial instead of the actual screen.
        ctx = browser.new_context(
            viewport=vp,
            device_scale_factor=dpr,
            locale=flow.get("locale", "en-US"),
        )
        if flow.get("storage"):
            ctx.add_init_script(
                "for (const [k,v] of Object.entries(%s)) localStorage.setItem(k,v);"
                % json.dumps(flow["storage"], ensure_ascii=False)
            )

        page = ctx.new_page()
        for i, step in enumerate(flow["steps"], 1):
            name = step.get("name") or f"step{i:02d}"

            if step.get("goto"):
                page.goto(step["goto"], wait_until="networkidle")
                # hash routing does NOT remount on a hash change — reload or you get
                # the previous screen with a new URL
                if "#" in step["goto"] or step.get("reload", True):
                    page.reload(wait_until="networkidle")

            page.wait_for_timeout(step.get("wait", 2500))
            dismiss(page, dismiss_labels)

            for click in step.get("click", []):
                el = page.locator(click).first
                if el.count():
                    el.scroll_into_view_if_needed()
                    el.click()
                    page.wait_for_timeout(step.get("after_click_wait", 1200))

            if step.get("wait_for"):
                page.wait_for_selector(step["wait_for"], timeout=15000)

            if step.get("eval"):
                page.evaluate(step["eval"])
                page.wait_for_timeout(step.get("after_eval_wait", 300))

            if step.get("scroll"):
                page.mouse.wheel(0, step["scroll"])
                page.wait_for_timeout(700)

            blur_selectors(page, step.get("blur"))
            blur_text(page, step.get("blur_text") or flow.get("blur_text"))
            page.wait_for_timeout(300)

            target = step.get("shot_selector")
            path = out / f"{name}.png"
            if target and page.locator(target).count():
                page.locator(target).first.screenshot(path=str(path))
            else:
                page.screenshot(path=str(path), full_page=step.get("full_page", False))
            print(f"  captured {path}")

        browser.close()

    print(f"\n-> {out}")


if __name__ == "__main__":
    sys.exit(main())
