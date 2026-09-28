#!/usr/bin/env node
/* The verification pass. Reports only things it actually measured.
   usage: node measure.js <baseURL> [pathsCSV]

   Every check here exists because a real bug got past a reviewer who was
   looking at the page. Read the comments before adding to it. */
const PUP = process.env.PUPPETEER_PATH || require('child_process')
  .execSync(__dirname + '/resolve-puppeteer.sh').toString().trim();
const puppeteer = require(PUP);

const [, , BASE, PATHS] = process.argv;
if (!BASE) { console.error('usage: measure.js <baseURL> [pathsCSV]'); process.exit(1); }
const paths = (PATHS || '/').split(',');
const SIZES = [[1920,1080],[1440,900],[1180,820],[1024,768],[834,1112],[768,1024],[700,900],[430,932],[360,740]];

(async () => {
  const br = await puppeteer.launch({ headless: 'new' });
  let problems = 0, n = 0;
  for (const p of paths) for (const [w, h] of SIZES) {
    const pg = await br.newPage();
    await pg.setViewport({ width: w, height: h });
    await pg.goto(BASE + p, { waitUntil: 'networkidle0' });

    // Step down the page. Jumping to the bottom leaves mid-page lazy images
    // unloaded, and they then read as broken when they are perfectly fine.
    await pg.evaluate(async () => {
      const step = innerHeight * 0.8;
      for (let y = 0; y < document.body.scrollHeight; y += step) {
        window.scrollTo(0, y); await new Promise(r => setTimeout(r, 110));
      }
      window.scrollTo(0, document.body.scrollHeight);
      // generous: a long grid of lazy tiles needs more than a beat to settle,
      // and a short wait reports them as broken when they are merely late.
      await new Promise(r => setTimeout(r, 1200));
    });

    const m = await pg.evaluate(() => {
      const doc = document.documentElement;
      const px = v => Math.round(v);
      return {
        // 1. Horizontal scroll. One overflowing child drags the whole page.
        overflowX: doc.scrollWidth - doc.clientWidth,

        // 2. Content that a reveal animation left permanently invisible.
        //    Transitions do not run in a hidden tab or a headless renderer,
        //    so a class-gated reveal can ship a blank section.
        unrevealed: [...document.querySelectorAll('[class*="rv-"],[data-reveal],.reveal')]
          .filter(e => getComputedStyle(e).opacity < 0.05).length,

        // 3. Images that are rendered but have no pixels. Zero-size images are
        //    excluded: hover-only previews are lazy on purpose and never load.
        blankImgs: [...document.images]
          .filter(i => i.getBoundingClientRect().width > 0 && (!i.complete || i.naturalWidth === 0))
          .map(i => i.getAttribute('src')),

        // 4. An element that does not fill the frame it was told to fill.
        //    offsetHeight, not getBoundingClientRect: a drift/parallax
        //    transform inflates the visual box and hides the gap. This is the
        //    check that catches "the photo is cut" — a stale max-block-size or
        //    a percentage height with no definite parent.
        unfilledFrames: [...document.querySelectorAll('img, video')]
          .filter(el => {
            const par = el.parentElement; if (!par) return false;
            const cs = getComputedStyle(el);
            if (cs.position !== 'absolute') return false;   // only frame-fillers
            return par.offsetHeight - el.offsetHeight > 2 || par.offsetWidth - el.offsetWidth > 2;
          })
          .map(el => ({ src: el.getAttribute('src'),
                        shortBy: px(el.parentElement.offsetHeight - el.offsetHeight) })),

        // 5. Anchors pointing at ids that do not exist on this page.
        deadAnchors: [...document.querySelectorAll('a[href^="#"]')]
          .map(a => a.getAttribute('href'))
          .filter(h => h.length > 1 && !document.querySelector(h)),

        // 6. Tap targets under 44px on touch-width viewports. Inline links
        //    inside a sentence are excluded — they are prose, not controls,
        //    and counting them buries the real ones in noise.
        smallTaps: innerWidth > 768 ? 0 :
          [...document.querySelectorAll('a,button')]
            .filter(e => { const r = e.getBoundingClientRect();
                           if (getComputedStyle(e).display === 'inline') return false;
                           return r.width > 0 && r.height > 0 && r.height < 44; })
            .map(e => (e.textContent || '').trim().slice(0, 24)),

        // 7. (nav set is compared across pages after the per-size loop)
      };
    });
    n++;
    const bad = m.overflowX > 1 || m.unrevealed || m.blankImgs.length ||
                m.unfilledFrames.length || m.deadAnchors.length;
    if (bad) { problems++;
      console.log(`PROBLEM ${p} ${w}x${h} ` + JSON.stringify({
        overflowX: m.overflowX || undefined, unrevealed: m.unrevealed || undefined,
        blankImgs: m.blankImgs.length ? m.blankImgs : undefined,
        unfilledFrames: m.unfilledFrames.length ? m.unfilledFrames : undefined,
        deadAnchors: m.deadAnchors.length ? m.deadAnchors : undefined }));
    }
    if (m.smallTaps.length) console.log(`note    ${p} ${w}x${h} tap target(s) under 44px: ${m.smallTaps.join(' | ')}`);
    await pg.close();
  }

  // Cross-page: the same nav on every page, or it is not a nav.
  // Keyed by aria-label, because a page often has more than one <nav> — a
  // breadcrumb is a nav too, and it is SUPPOSED to differ per page. Comparing
  // every <nav> together reports that correct difference as a defect.
  const navs = {};
  for (const p of paths) {
    const pg = await br.newPage();
    await pg.goto(BASE + p, { waitUntil: 'domcontentloaded' });
    navs[p] = await pg.evaluate(() => {
      const out = { __lang: document.documentElement.lang || 'x' };
      document.querySelectorAll('nav').forEach((n, i) => {
        const key = n.id || n.getAttribute('aria-label') || ('nav' + i);
        out[key] = [...n.querySelectorAll('a')]
          .map(a => a.getAttribute('href')).join(' ');
      });
      return out;
    });
    await pg.close();
  }
  // Only compare a nav that appears on more than one page, and compare it to
  // itself. aria-current is expected to move; the link set is not.
  // ...and compared within one language. A translated site's Hebrew nav
  // points at /he/ paths and SHOULD differ from the English one; comparing
  // across languages reports the translation itself as the defect.
  const keys = [...new Set(Object.values(navs).flatMap(o => Object.keys(o)))].filter(k => k !== '__lang');
  const langs = [...new Set(Object.values(navs).map(o => o.__lang))];
  for (const lang of langs) for (const k of keys) {
    const seen = Object.entries(navs).filter(([, o]) => o.__lang === lang && o[k] !== undefined);
    if (seen.length < 2) continue;
    if (new Set(seen.map(([, o]) => o[k])).size > 1) {
      problems++;
      console.log(`PROBLEM nav "${k}" has a different link set across [lang=${lang}] pages:`);
      for (const [p, o] of seen) console.log('  ' + p.padEnd(20) + o[k]);
    }
  }

  console.log(problems ? `\n${problems} problem(s) across ${n} page/size combos`
                       : `\nCLEAN: ${n} page/size combos, and one nav across all pages`);
  await br.close();
  process.exit(problems ? 1 : 0);
})();
