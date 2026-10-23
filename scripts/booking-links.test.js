'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const test = require('node:test');

const root = path.join(__dirname, '..');
const banned = ['seat' + 'on', 'get' + 'seat'];
const siteWidget = 'ot_source=Restaurant%20website&ot_campaign=site-widget';
const brunchBook = 'https://www.opentable.com/booking/experiences-availability?rid=1563214&experienceId=833122&shareReferrer=web&ot_source=Restaurant%20website&ot_campaign=site-brunch';
const plainBook = 'https://www.opentable.com/r/sipsoberbar-reservations-gulfport?restref=1563214';
const brunchCtas = [
  'header-brunch',
  'jazz-crumb',
  'jazz-top',
  'jazz-menu',
  'footer-brunch',
  'dock-brunch',
  'chooser-brunch',
  'res-brunch',
  'home-sunday',
];
const giftNav = 'utm_source=website&utm_medium=nav&utm_campaign=giftcards';
const giftHome = 'utm_source=website&utm_medium=homepage&utm_campaign=giftcards';
const skipDir = new Set(['.git', 'node_modules']);

function walk(dir, out = []) {
  for (const name of fs.readdirSync(dir)) {
    if (skipDir.has(name)) continue;
    const full = path.join(dir, name);
    const stat = fs.statSync(full);
    if (stat.isDirectory()) walk(full, out);
    else out.push(full);
  }
  return out;
}

function textFiles() {
  return walk(root).filter((file) => {
    const rel = path.relative(root, file);
    if (rel.startsWith('public/images/') || rel.startsWith('public/fonts/')) return false;
    const buf = fs.readFileSync(file);
    return !buf.includes(0);
  });
}

test('no legacy booking-brand strings remain', () => {
  const hits = [];
  for (const file of textFiles()) {
    const text = fs.readFileSync(file, 'utf8');
    const lower = text.toLowerCase();
    for (const needle of banned) {
      let from = 0;
      while (from < lower.length) {
        const at = lower.indexOf(needle, from);
        if (at === -1) break;
        const line = text.slice(0, at).split('\n').length;
        hits.push(`${path.relative(root, file)}:${line}`);
        from = at + needle.length;
      }
    }
  }
  assert.deepStrictEqual(hits, []);
});

test('reserve links use the site-widget campaign, with one plain fallback', () => {
  const plainHits = [];
  const offCampaign = [];
  for (const file of textFiles()) {
    const rel = path.relative(root, file);
    if (!rel.startsWith('public/')) continue;
    const text = fs.readFileSync(file, 'utf8');
    const re = /https?:\/\/www\.opentable\.com\/[^"'<\s]+|\/\/www\.opentable\.com\/[^"'<\s]+/g;
    let match;
    while ((match = re.exec(text))) {
      const url = match[0].replace(/&amp;/g, '&');
      if (url === plainBook) {
        plainHits.push(rel);
        continue;
      }
      if (url === brunchBook) continue;
      if (!url.includes('rid=1563214') && !url.includes('restref=1563214')) {
        offCampaign.push(`${rel} missing rid: ${url}`);
      }
      if (!url.includes(siteWidget)) offCampaign.push(`${rel} ${url}`);
    }
  }
  assert.deepStrictEqual(plainHits, ['public/reservations.html']);
  assert.deepStrictEqual(offCampaign, []);
});

test('jazz brunch reserve links use the brunch experience', () => {
  const pages = walk(path.join(root, 'public')).filter((file) => file.endsWith('.html'));
  const misses = [];
  let brunchLinks = 0;
  for (const file of pages) {
    const rel = path.relative(root, file);
    const text = fs.readFileSync(file, 'utf8');
    const anchors = text.match(/<a\b[^>]*>[\s\S]*?<\/a>/g) || [];
    for (const anchor of anchors) {
      const cta = anchor.match(/\bdata-cta="([^"]+)"/);
      const href = anchor.match(/\bhref="([^"]+)"/);
      if (!cta || !href) continue;
      if (!brunchCtas.includes(cta[1])) continue;
      brunchLinks += 1;
      const url = href[1].replace(/&amp;/g, '&');
      if (url !== brunchBook) misses.push(`${rel} ${cta[1]} ${url}`);
    }
  }
  assert.ok(brunchLinks > 0);
  assert.deepStrictEqual(misses, []);

  const jazz = fs.readFileSync(path.join(root, 'public/sunday-jazz-brunch.html'), 'utf8');
  assert.equal((jazz.match(/experienceId=833122/g) || []).length, 8);
  const home = fs.readFileSync(path.join(root, 'public/index.html'), 'utf8');
  assert.match(home, /data-cta="home-sunday"/);
  assert.match(home, /data-cta="chooser-brunch"/);
  const js = fs.readFileSync(path.join(root, 'public/site.js'), 'utf8');
  assert.ok(js.includes(brunchBook));
  assert.match(js, /a\.href = OT_BRUNCH/);
  assert.match(js, /\[data-cta="chooser-dinner"\]/);
  assert.match(js, /\[data-cta="chooser-brunch"\]/);
  assert.match(js, /var OT_RESERVE = 'https:\/\/www\.opentable\.com\/r\/sipsoberbar-reservations-gulfport\?restref=1563214&lang=en-US&ot_source=Restaurant%20website&ot_campaign=site-widget'/);
});

test('dinner entrées use the card, owner prices, photos, and service hours', () => {
  const names = [
    'Pesto Parm Gnocchi',
    'Three-Cheese Stuffed Shells',
    'Chicken "Lasagna" al Forno',
    'Chicken Bacon Ranch Tortellini',
    'Cajun Crawfish Tortellini',
    'Creole Shrimp & Grits',
  ];
  const prices = ['18', '19', '22', '20', '26', '23'];
  const menu = fs.readFileSync(path.join(root, 'public/menu.html'), 'utf8');
  const home = fs.readFileSync(path.join(root, 'public/index.html'), 'utf8').replace(/&amp;/g, '&');
  const menuStart = menu.indexOf('id="entrees"');
  const menuSlice = menu.slice(menuStart, menu.indexOf('</section>', menuStart)).replace(/&amp;/g, '&');
  const hours = 'Served from 4pm onward daily, and during Sunday brunch (10am–1pm).';
  assert.ok(menuStart > 0);
  assert.ok(menu.indexOf('id="entrees"') < menu.indexOf('id="breakfast"'));
  for (const name of names) assert.ok(menuSlice.includes(name), name);
  assert.match(menuSlice, /\$18\. Pillowy potato gnocchi/);
  assert.match(menuSlice, /Add fire-braised chicken \+\$3\./);
  assert.match(menuSlice, /\$26\. Cheese tortellini and tender crawfish tails/);
  assert.equal(menuSlice.includes('$24'), false);
  assert.match(menuSlice, /Each served with Cheesy Garlic Focaccia/);
  assert.ok(menuSlice.includes(hours));
  assert.equal(menu.includes('list.jpg'), false);
  assert.equal(/non-alcoholic|mocktail|zero-proof/i.test(menuSlice), false);
  for (const name of ['pesto-parm-gnocchi', 'three-cheese-stuffed-shells', 'chicken-lasagna-al-forno', 'chicken-bacon-ranch-tortellini', 'cajun-crawfish-tortellini', 'creole-shrimp-grits']) {
    assert.ok(menuSlice.includes(`/images/menu/${name}-200.webp`));
    assert.ok(menuSlice.includes(`/images/menu/${name}-200.jpg`));
    assert.ok(fs.existsSync(path.join(root, 'public/images/menu', `${name}-400.webp`)));
    assert.ok(fs.existsSync(path.join(root, 'public/images/menu', `${name}-400.jpg`)));
  }

  assert.match(home, /Now serving <em class="it">dinner\.<\/em>/);
  assert.ok(home.includes(hours));
  assert.ok(home.includes('Each served with Cheesy Garlic Focaccia'));
  assert.ok(home.includes('Pesto Parm Gnocchi'));
  assert.ok(home.includes('Chicken "Lasagna" al Forno'));
  assert.ok(home.includes('Creole Shrimp & Grits'));
  assert.ok(home.includes('/images/dish/pesto-parm-gnocchi-800.webp'));
  assert.ok(home.includes('/images/dish/pesto-parm-gnocchi-800.jpg'));
  const dinnerAnchor = home.match(/<a\b[^>]*data-cta="home-dinner"[^>]*>/);
  assert.ok(dinnerAnchor);
  const dinnerUrl = dinnerAnchor[0].match(/href="([^"]+)"/)[1].replace(/&amp;/g, '&');
  assert.ok(dinnerUrl.includes(siteWidget), dinnerUrl);
  assert.equal(dinnerUrl.includes('experienceId=833122'), false);

  const blocks = [...menu.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)];
  const data = JSON.parse(blocks[0][1]);
  const section = data.hasMenuSection.find((entry) => entry.name === 'Entrées');
  assert.equal(section.description, `${hours} Each served with Cheesy Garlic Focaccia.`);
  assert.deepStrictEqual(section.hasMenuItem.map((item) => item.name), names);
  assert.deepStrictEqual(section.hasMenuItem.map((item) => item.offers.price), prices);
  const crawfish = section.hasMenuItem.find((item) => item.name === 'Cajun Crawfish Tortellini');
  assert.equal(crawfish.offers.price, '26');
  assert.equal(JSON.stringify(crawfish).includes('24'), false);
  const gnocchi = section.hasMenuItem.find((item) => item.name === 'Pesto Parm Gnocchi');
  assert.match(gnocchi.description, /Add fire-braised chicken \+\$3\./);
});

test('menu lists beignets as alcohol-free with no price', () => {
  const html = fs.readFileSync(path.join(root, 'public/menu.html'), 'utf8');
  assert.match(html, /<h3>Beignets<\/h3><p>Alcohol-free<\/p>/);
  const visible = html.slice(html.indexOf('<h3>Beignets</h3>'), html.indexOf('<h3>Beignets</h3>') + 80);
  assert.equal(/\$\d/.test(visible), false);
  assert.equal(/non-alcoholic|mocktail|zero-proof/i.test(visible), false);
  const blocks = [...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)];
  const menu = JSON.parse(blocks[0][1]);
  const breakfast = menu.hasMenuSection.find((section) => section.name === 'Breakfast Sandwiches');
  const item = breakfast.hasMenuItem.find((entry) => entry.name === 'Beignets');
  assert.equal(item.description, 'Alcohol-free');
  assert.equal(item.offers, undefined);
});

test('titles and meta descriptions lead with dinner and leave kava on the menu', () => {
  const title = 'Sober Bar & Kitchen | Alcohol-Free Bar, Dinner & Coffee in Gulfport, FL';
  const description = 'Alcohol-free bar and dinner in Gulfport, FL. Coffee from 7am, a New Orleans kitchen, and Sunday jazz brunch. Open daily.';
  assert.ok(description.length < 160, String(description.length));
  assert.match(description, /^Alcohol-free bar and dinner/);
  const home = fs.readFileSync(path.join(root, 'public/index.html'), 'utf8').replace(/&amp;/g, '&');
  assert.equal(home.split(title).length - 1, 3);
  assert.equal(home.split(description).length - 1, 3);
  const business = JSON.parse(home.match(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/)[1]);
  assert.equal(business.name, 'Sober Bar & Kitchen');
  assert.match(business.description, /^Sober Bar & Kitchen is an alcohol-free bar and dinner/);
  assert.equal(/kava/i.test(business.description), false);

  const misses = [];
  for (const file of walk(path.join(root, 'public')).filter((entry) => entry.endsWith('.html'))) {
    const html = fs.readFileSync(file, 'utf8');
    const tags = html.match(/<title>[\s\S]*?<\/title>|<meta\b[^>]*(?:name|property)="(?:description|og:title|og:description|twitter:title|twitter:description)"[^>]*>/g) || [];
    for (const tag of tags) {
      const text = tag.replace(/&amp;/g, '&');
      if (/kava/i.test(text)) misses.push(`${path.basename(file)} ${text.slice(0, 120)}`);
    }
  }
  assert.deepStrictEqual(misses, []);

  const menu = fs.readFileSync(path.join(root, 'public/menu.html'), 'utf8');
  assert.match(menu, /<h3>Kava<\/h3>/);
  const kavaPage = fs.readFileSync(path.join(root, 'public/kava-bar-gulfport.html'), 'utf8');
  assert.match(kavaPage, /<h1>A kava bar in/);
});

test('gift cards are in the nav, footer, and one homepage line', () => {
  const pages = walk(path.join(root, 'public')).filter((file) => file.endsWith('.html'));
  const missingNav = [];
  for (const file of pages) {
    const text = fs.readFileSync(file, 'utf8');
    if (!text.includes('class="nav"')) continue;
    const decoded = text.replace(/&amp;/g, '&');
    const navCount = decoded.split(giftNav).length - 1;
    if (navCount !== 3) missingNav.push(`${path.basename(file)} has ${navCount} nav gift links`);
  }
  assert.deepStrictEqual(missingNav, []);

  const home = fs.readFileSync(path.join(root, 'public/index.html'), 'utf8').replace(/&amp;/g, '&');
  assert.equal(home.split(giftHome).length - 1, 1);
  assert.match(home, /Gift cards<\/a> — for coffee, brunch, and the bar\./);
  const others = pages.filter((file) => !file.endsWith('index.html'));
  for (const file of others) {
    const text = fs.readFileSync(file, 'utf8');
    assert.equal(text.includes('utm_medium=homepage'), false, path.basename(file));
  }
});

test('reservation structured data points at OpenTable and still accepts parties of 1–6', () => {
  const expect = [
    'public/index.html',
    'public/breakfast-gulfport.html',
    'public/private-events.html',
    'public/reservations.html',
    'public/sunday-jazz-brunch.html',
  ];
  for (const rel of expect) {
    const html = fs.readFileSync(path.join(root, rel), 'utf8');
    const blocks = [...html.matchAll(/<script type="application\/ld\+json">([\s\S]*?)<\/script>/g)];
    assert.ok(blocks.length > 0, rel);
    let reserve = null;
    for (const block of blocks) {
      const data = JSON.parse(block[1]);
      if (data.potentialAction && data.potentialAction['@type'] === 'ReserveAction') reserve = data;
      if (data['@type'] === 'FAQPage') JSON.parse(block[1]);
    }
    assert.ok(reserve, rel);
    if (rel !== 'public/sunday-jazz-brunch.html') assert.equal(reserve.acceptsReservations, true);
    const target = reserve.potentialAction.target.urlTemplate;
    if (rel === 'public/sunday-jazz-brunch.html') {
      assert.equal(target, brunchBook);
    } else {
      assert.ok(target.includes(siteWidget), target);
      assert.ok(target.includes('restref=1563214'), target);
    }
    assert.match(html, /Book online for 1–6/);
  }
  const reservations = fs.readFileSync(path.join(root, 'public/reservations.html'), 'utf8');
  assert.match(reservations, /Book a table on OpenTable for parties of 1–6/);
  assert.match(reservations, /theme=wide/);
  assert.match(reservations, /color=3/);
  assert.match(reservations, /rid=1563214&type=standard&theme=wide/);
  assert.match(reservations, /ot_campaign=site-widget/);
});
