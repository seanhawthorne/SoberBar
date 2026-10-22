'use strict';

const assert = require('assert');
const fs = require('fs');
const path = require('path');
const test = require('node:test');

const root = path.join(__dirname, '..');
const banned = ['seat' + 'on', 'get' + 'seat'];
const siteWidget = 'ot_source=Restaurant%20website&ot_campaign=site-widget';
const plainBook = 'https://www.opentable.com/r/sipsoberbar-reservations-gulfport?restref=1563214';
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
      if (!url.includes('rid=1563214') && !url.includes('restref=1563214')) {
        offCampaign.push(`${rel} missing rid: ${url}`);
      }
      if (!url.includes(siteWidget)) offCampaign.push(`${rel} ${url}`);
    }
  }
  assert.deepStrictEqual(plainHits, ['public/reservations.html']);
  assert.deepStrictEqual(offCampaign, []);
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
    assert.ok(target.includes(siteWidget), target);
    assert.ok(target.includes('restref=1563214'), target);
    assert.match(html, /Book online for 1–6/);
  }
  const reservations = fs.readFileSync(path.join(root, 'public/reservations.html'), 'utf8');
  assert.match(reservations, /Book a table on OpenTable for parties of 1–6/);
  assert.match(reservations, /theme=wide/);
  assert.match(reservations, /color=3/);
  assert.match(reservations, /rid=1563214&type=standard&theme=wide/);
  assert.match(reservations, /ot_campaign=site-widget/);
});
