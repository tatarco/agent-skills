#!/usr/bin/env node
/* Capture the visual truth the audit agents will share.
   usage: node shots.js <baseURL> <outDir> [pathsCSV]
   Every agent reads the SAME screenshots, so their findings can be compared
   instead of each one describing a different render. */
const PUP = process.env.PUPPETEER_PATH || require('child_process')
  .execSync(__dirname + '/resolve-puppeteer.sh').toString().trim();
const puppeteer = require(PUP);
const fs = require('fs');

const [, , BASE, OUT, PATHS] = process.argv;
if (!BASE || !OUT) { console.error('usage: shots.js <baseURL> <outDir> [pathsCSV]'); process.exit(1); }
const paths = (PATHS || '/').split(',');

// Deliberately includes the awkward middle. Most responsive bugs live between
// "phone" and "laptop", which is exactly the range nobody screenshots.
const SIZES = [[1920,1080,'desk-xl'],[1440,900,'desk'],[1180,820,'laptop'],
               [1024,768,'lap-sm'],[900,1200,'tab-l'],[834,1112,'tab'],
               [768,1024,'tab-sm'],[700,900,'tween'],[600,800,'wide-phone'],
               [430,932,'phone'],[360,740,'phone-sm']];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const br = await puppeteer.launch({ headless: 'new' });
  for (const p of paths) {
    const slug = p.replace(/[^a-z0-9]+/gi, '-').replace(/^-|-$/g, '') || 'home';
    for (const [w, h, name] of SIZES) {
      // full pages only for the primary path: 11 full-page shots per page
      // is more pixels than any reviewer will actually look at.
      const full = p === paths[0] && ['desk', 'phone'].includes(name);
      const pg = await br.newPage();
      await pg.setViewport({ width: w, height: h });
      await pg.goto(BASE + p, { waitUntil: 'networkidle0' });
      await pg.evaluate(() => new Promise(r => setTimeout(r, 500)));
      await pg.screenshot({ path: `${OUT}/${slug}-${name}.png` });
      if (full) await pg.screenshot({ path: `${OUT}/${slug}-${name}-full.png`, fullPage: true });
      await pg.close();
    }
    console.log('shot', p);
  }
  await br.close();
  console.log('screenshots in', OUT);
})();
