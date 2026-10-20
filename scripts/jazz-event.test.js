'use strict';

const assert = require('assert');
const { spawnSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');
const test = require('node:test');

const {
  addDays,
  extractEvent,
  nextJazzSunday,
  nyOffset,
  publishHtml,
  safePublish,
  stripEvent,
  validateSchemaEvent,
} = require('./stamp-jazz-event');

const root = path.join(__dirname, '..');
const pagePath = path.join(root, 'public', 'sunday-jazz-brunch.html');
const datesPath = path.join(root, 'public', 'data', 'jazz-dates.json');

function bounds(extra = {}) {
  return { through: '2026-12-13', skip: [], ...extra };
}

function at(isoInstant) {
  return nextJazzSunday(new Date(isoInstant), bounds());
}

test('a build on Tuesday October 20 publishes Sunday October 25 at 10am EDT', () => {
  const next = at('2026-10-20T15:00:00.000Z');
  assert.deepStrictEqual(next, {
    date: '2026-10-25',
    startDate: '2026-10-25T10:00:00-04:00',
    endDate: '2026-10-25T13:00:00-04:00',
  });
});

test('on a Sunday before 1pm today still counts, and 1pm rolls forward', () => {
  assert.strictEqual(at('2026-10-25T16:00:00.000Z').date, '2026-10-25');
  assert.strictEqual(at('2026-10-25T16:59:00.000Z').startDate, '2026-10-25T10:00:00-04:00');
  assert.strictEqual(at('2026-10-25T17:00:00.000Z').date, '2026-11-01');
});

test('dates across the November 1 daylight-saving change use the offset at 10am', () => {
  assert.strictEqual(nyOffset('2026-10-25'), '-04:00');
  assert.strictEqual(nyOffset('2026-11-01'), '-05:00');
  assert.strictEqual(nyOffset('2026-12-13'), '-05:00');
  assert.strictEqual(nyOffset('2026-03-01'), '-05:00');
  assert.strictEqual(nyOffset('2026-03-08'), '-04:00');

  const crossing = at('2026-10-25T17:00:00.000Z');
  assert.strictEqual(crossing.startDate, '2026-11-01T10:00:00-05:00');
  assert.strictEqual(crossing.endDate, '2026-11-01T13:00:00-05:00');

  const morningOfChange = at('2026-11-01T17:59:00.000Z');
  assert.strictEqual(morningOfChange.startDate, '2026-11-01T10:00:00-05:00');

  const afterChange = at('2026-11-01T18:00:00.000Z');
  assert.strictEqual(afterChange.startDate, '2026-11-08T10:00:00-05:00');
  assert.strictEqual(afterChange.endDate, '2026-11-08T13:00:00-05:00');
});

test('December 13 is included through that morning, and the next Sunday is left out', () => {
  assert.strictEqual(at('2026-12-13T17:30:00.000Z').startDate, '2026-12-13T10:00:00-05:00');
  assert.strictEqual(at('2026-12-13T18:00:00.000Z'), null);
  assert.strictEqual(at('2026-12-14T15:00:00.000Z'), null);
});

test('a skipped Sunday rolls to the next open one, including across November 1', () => {
  const skipped = nextJazzSunday(new Date('2026-10-20T15:00:00.000Z'), bounds({
    skip: ['2026-10-25'],
  }));
  assert.strictEqual(skipped.startDate, '2026-11-01T10:00:00-05:00');

  const todaySkipped = nextJazzSunday(new Date('2026-10-25T14:00:00.000Z'), bounds({
    skip: ['2026-10-25', '2026-11-01'],
  }));
  assert.strictEqual(todaySkipped.startDate, '2026-11-08T10:00:00-05:00');

  const sundays = [];
  let day = '2026-10-25';
  while (day <= '2026-12-13') {
    sundays.push(day);
    day = addDays(day, 7);
  }
  const noneLeft = nextJazzSunday(new Date('2026-10-20T15:00:00.000Z'), bounds({ skip: sundays }));
  assert.strictEqual(noneLeft, null);
});

test('the schedule file is a through date and a skip list the owner can edit', () => {
  const file = JSON.parse(fs.readFileSync(datesPath, 'utf8'));
  assert.match(file.through, /^\d{4}-\d{2}-\d{2}$/);
  assert.ok(Array.isArray(file.skip));
  assert.throws(() => nextJazzSunday(new Date('2026-10-20T15:00:00.000Z'), {
    through: '2026-12-13',
    skip: ['2026-11-02'],
  }), /not a Sunday/);
});

test('the published page is a schema.org Event for October 25 and keeps the rest of the page', () => {
  const original = fs.readFileSync(pagePath, 'utf8');
  const published = publishHtml(original, new Date('2026-10-20T15:00:00.000Z'), bounds());
  const event = extractEvent(published);
  validateSchemaEvent(event);
  assert.strictEqual(event.startDate, '2026-10-25T10:00:00-04:00');
  assert.strictEqual(event.endDate, '2026-10-25T13:00:00-04:00');
  assert.match(event.name, /brunch 10am–1pm/);
  assert.match(event.name, /jazz 10:30am–1pm/);
  assert.match(event.description, /Brunch is 10am–1pm/);
  assert.match(event.description, /live jazz is 10:30am–1pm/);
  assert.match(event.description, /alcohol-free/);
  assert.doesNotMatch(`${event.name}\n${event.description}`, /zero-?proof|ABV|kava|0\.5\s*%/i);

  assert.match(published, /name="description" content="Live jazz every Sunday in Gulfport, FL with the Western Gypsies\. Brunch is 10am to 1pm/);
  assert.match(published, /Every Sunday, with the Western Gypsies\. Brunch is 10am to 1pm\./);
  assert.match(published, /"@type": "FAQPage"/);
  assert.match(published, /"@type": "Article"/);
  assert.match(published, /"@type": "BreadcrumbList"/);

  const onlyDates = published
    .replace(event.startDate, '2026-10-18T10:00:00-04:00')
    .replace(event.endDate, '2026-10-18T13:00:00-04:00');
  assert.strictEqual(onlyDates, original);
});

test('outside the window, or when the stamp fails, the Event is left out', () => {
  const original = fs.readFileSync(pagePath, 'utf8');
  const closed = publishHtml(original, new Date('2026-12-20T15:00:00.000Z'), bounds());
  assert.strictEqual(extractEvent(closed), null);
  assert.match(closed, /"@type": "FAQPage"/);

  const broken = safePublish(original, new Date('2026-10-20T15:00:00.000Z'), {
    through: 'nope',
    skip: [],
  });
  assert.strictEqual(extractEvent(broken), null);
  assert.match(stripEvent(original), /"@type": "WebPage"/);
  assert.doesNotMatch(stripEvent(original), /"@type": "Event"/);
});

test('the stamp script exits 0 when it writes October 25 and when the dates file is bad', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'jazz-event-'));
  const page = path.join(dir, 'sunday-jazz-brunch.html');
  const dates = path.join(dir, 'jazz-dates.json');
  const script = path.join(__dirname, 'stamp-jazz-event.js');
  try {
    fs.copyFileSync(pagePath, page);
    fs.copyFileSync(datesPath, dates);
    const ok = spawnSync(process.execPath, [script], {
      env: {
        ...process.env,
        JAZZ_PAGE: page,
        JAZZ_DATES: dates,
        JAZZ_NOW: '2026-10-20T15:00:00.000Z',
      },
      encoding: 'utf8',
    });
    assert.strictEqual(ok.status, 0, ok.stderr);
    assert.match(ok.stdout, /2026-10-25T10:00:00-04:00/);
    assert.strictEqual(
      extractEvent(fs.readFileSync(page, 'utf8')).startDate,
      '2026-10-25T10:00:00-04:00'
    );

    fs.copyFileSync(pagePath, page);
    fs.writeFileSync(dates, '{');
    const bad = spawnSync(process.execPath, [script], {
      env: { ...process.env, JAZZ_PAGE: page, JAZZ_DATES: dates, JAZZ_NOW: '2026-10-20T15:00:00.000Z' },
      encoding: 'utf8',
    });
    assert.strictEqual(bad.status, 0, bad.stderr);
    assert.strictEqual(extractEvent(fs.readFileSync(page, 'utf8')), null);

    fs.copyFileSync(pagePath, page);
    const stripped = spawnSync(process.execPath, [script, '--strip-only'], {
      env: { ...process.env, JAZZ_PAGE: page },
      encoding: 'utf8',
    });
    assert.strictEqual(stripped.status, 0, stripped.stderr);
    assert.strictEqual(extractEvent(fs.readFileSync(page, 'utf8')), null);
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
});

test('the October 18 event timestamp is only the template on the jazz page', () => {
  const hits = [];
  const walk = (dir) => {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      if (entry.name === '.git' || entry.name === 'node_modules') continue;
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (/\.(html|txt|json|xml|yml|yaml|js|md)$/.test(entry.name)) {
        if (full.startsWith(path.join(root, 'scripts') + path.sep)) continue;
        const text = fs.readFileSync(full, 'utf8');
        if (text.includes('2026-10-18T10:00:00')) hits.push(path.relative(root, full));
      }
    }
  };
  walk(root);
  assert.deepStrictEqual(hits, ['public/sunday-jazz-brunch.html']);
  for (const rel of ['public/index.html', 'public/llms.txt', 'public/llms-full.txt', 'public/sitemap.xml']) {
    assert.doesNotMatch(fs.readFileSync(path.join(root, rel), 'utf8'), /2026-10-18T/);
  }
  assert.strictEqual(fs.existsSync(path.join(root, 'public', 'facts.json')), false);
  assert.strictEqual(fs.existsSync(path.join(root, 'facts.json')), false);
});

test('the Pages workflow stamps the date on Sunday afternoon before upload', () => {
  const yml = fs.readFileSync(path.join(root, '.github', 'workflows', 'pages.yml'), 'utf8');
  assert.match(yml, /cron:\s*'30 18 \* \* 0'/);
  assert.match(yml, /November 1, 2026/);
  const stamp = yml.indexOf('stamp-jazz-event.js');
  const upload = yml.indexOf('upload-pages-artifact');
  assert.ok(stamp > 0 && upload > stamp);
  assert.match(yml, /exit 0/);
});
