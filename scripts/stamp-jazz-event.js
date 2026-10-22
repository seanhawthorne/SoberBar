'use strict';

const fs = require('fs');
const path = require('path');

const PAGE = path.join(__dirname, '..', 'public', 'sunday-jazz-brunch.html');
const DATES = path.join(__dirname, '..', 'public', 'data', 'jazz-dates.json');
const BRUNCH_START = '10:00:00';
const BRUNCH_END = '13:00:00';

function weekdayIndex(iso) {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(Date.UTC(y, m - 1, d)).getUTCDay();
}

function addDays(iso, days) {
  const [y, m, d] = iso.split('-').map(Number);
  const dt = new Date(Date.UTC(y, m - 1, d));
  dt.setUTCDate(dt.getUTCDate() + days);
  const month = String(dt.getUTCMonth() + 1).padStart(2, '0');
  const day = String(dt.getUTCDate()).padStart(2, '0');
  return `${dt.getUTCFullYear()}-${month}-${day}`;
}

function nyParts(date) {
  if (!(date instanceof Date) || Number.isNaN(date.getTime())) {
    throw new Error('Need a real date to place the jazz brunch.');
  }
  const fmt = new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/New_York',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    hourCycle: 'h23',
  });
  const map = {};
  for (const part of fmt.formatToParts(date)) {
    if (part.type !== 'literal') map[part.type] = part.value;
  }
  let hour = Number(map.hour);
  if (hour === 24) hour = 0;
  if (!map.year || !map.month || !map.day || Number.isNaN(hour)) {
    throw new Error('Could not read the time in America/New_York.');
  }
  return {
    iso: `${map.year}-${map.month}-${map.day}`,
    hour,
    minute: Number(map.minute),
  };
}

// Offset in effect at 10:00 that morning. DST in New York ends at 2am,
// so a 10am brunch is already on the new offset.
function nyOffset(isoDate) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(isoDate)) {
    throw new Error(`Not a calendar date: ${isoDate}`);
  }
  const [y, m, d] = isoDate.split('-').map(Number);
  const probe = new Date(Date.UTC(y, m - 1, d, 15, 0, 0));
  const parts = nyParts(probe);
  if (parts.iso !== isoDate) {
    throw new Error(`New York date shifted while checking ${isoDate}.`);
  }
  const offsetHours = parts.hour - 15;
  if (offsetHours === -4) return '-04:00';
  if (offsetHours === -5) return '-05:00';
  throw new Error(`Unexpected New York offset on ${isoDate}.`);
}

function assertBounds(bounds) {
  if (!bounds || typeof bounds !== 'object' || Array.isArray(bounds)) {
    throw new Error('jazz-dates.json must be an object with through and skip.');
  }
  if (typeof bounds.through !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(bounds.through)) {
    throw new Error('through must be a YYYY-MM-DD date.');
  }
  if (!Array.isArray(bounds.skip)) {
    throw new Error('skip must be a list of YYYY-MM-DD dates.');
  }
  for (const day of bounds.skip) {
    if (typeof day !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(day)) {
      throw new Error('Each skip date must be YYYY-MM-DD.');
    }
    if (weekdayIndex(day) !== 0) {
      throw new Error(`Skip date ${day} is not a Sunday.`);
    }
  }
}

function nextJazzSunday(now, bounds) {
  assertBounds(bounds);
  const ny = nyParts(now);
  let iso = ny.iso;
  const todayStillOn = weekdayIndex(iso) === 0 && ny.hour < 13;
  if (!todayStillOn) {
    const dow = weekdayIndex(iso);
    iso = addDays(iso, dow === 0 ? 7 : 7 - dow);
  }
  const skip = new Set(bounds.skip);
  let guard = 0;
  while (skip.has(iso)) {
    iso = addDays(iso, 7);
    if (++guard > 520) throw new Error('The skip list has no open Sunday.');
  }
  if (iso > bounds.through) return null;
  const offset = nyOffset(iso);
  return {
    date: iso,
    startDate: `${iso}T${BRUNCH_START}${offset}`,
    endDate: `${iso}T${BRUNCH_END}${offset}`,
  };
}

function listJsonLd(html) {
  const re = /<script type="application\/ld\+json">([\s\S]*?)<\/script>/g;
  const blocks = [];
  let match;
  while ((match = re.exec(html))) {
    blocks.push({
      raw: match[0],
      json: match[1],
      start: match.index,
      end: match.index + match[0].length,
    });
  }
  return blocks;
}

function stripEvent(html) {
  return html.replace(/<script type="application\/ld\+json">[\s\S]*?<\/script>\n?/g, (block) => {
    return /"@type"\s*:\s*"Event"/.test(block) ? '' : block;
  });
}

function extractEvent(html) {
  const events = [];
  for (const block of listJsonLd(html)) {
    let data;
    try {
      data = JSON.parse(block.json);
    } catch {
      continue;
    }
    if (data['@type'] === 'Event') events.push(data);
  }
  if (events.length > 1) throw new Error('The page has more than one Event.');
  return events[0] || null;
}

function wordingProblems(event) {
  const problems = [];
  const name = event.name || '';
  const description = event.description || '';
  const blob = `${name}\n${description}`;
  const brunch = /brunch[\s\S]{0,40}?10(?::00)?\s*am\s*[–-]\s*1\s*pm/i;
  const jazz = /jazz[\s\S]{0,40}?10:30\s*am\s*[–-]\s*1\s*pm/i;
  if (!brunch.test(name)) problems.push('name should say brunch is 10am–1pm');
  if (!jazz.test(name)) problems.push('name should say jazz is 10:30am–1pm');
  if (!brunch.test(description)) problems.push('description should say brunch is 10am–1pm');
  if (!jazz.test(description)) problems.push('description should say jazz is 10:30am–1pm');
  if (!/alcohol-free/i.test(description)) problems.push('description should say alcohol-free');
  if (/zero[\s-]?proof|\bABV\b|0\.5\s*%|kava/i.test(blob)) {
    problems.push('say alcohol-free, with no zero-proof, ABV caveat, or kava');
  }
  return problems;
}

function validateSchemaEvent(event) {
  const problems = [];
  if (!event || typeof event !== 'object') {
    throw new Error('Not a valid schema.org Event: missing event');
  }
  if (event['@context'] !== 'https://schema.org') problems.push('@context must be https://schema.org');
  if (event['@type'] !== 'Event') problems.push('@type must be Event');
  if (typeof event['@id'] !== 'string' || !event['@id']) problems.push('@id');
  if (typeof event.name !== 'string' || !event.name.trim()) problems.push('name');
  if (typeof event.description !== 'string' || !event.description.trim()) problems.push('description');
  if (typeof event.url !== 'string' || !event.url.startsWith('https://')) problems.push('url');
  if (typeof event.image !== 'string' || !event.image.startsWith('https://')) problems.push('image');

  const start = /^(\d{4}-\d{2}-\d{2})T10:00:00(-0[45]:00)$/.exec(event.startDate || '');
  const end = /^(\d{4}-\d{2}-\d{2})T13:00:00(-0[45]:00)$/.exec(event.endDate || '');
  if (!start) problems.push('startDate must be 10:00:00 with a New York offset');
  if (!end) problems.push('endDate must be 13:00:00 with a New York offset');
  if (start && end) {
    if (start[1] !== end[1]) problems.push('startDate and endDate must be the same day');
    if (start[2] !== end[2]) problems.push('startDate and endDate must share an offset');
    if (weekdayIndex(start[1]) !== 0) problems.push('the event date must be a Sunday');
    try {
      if (start[2] !== nyOffset(start[1])) problems.push('offset must match America/New_York at 10am');
    } catch (err) {
      problems.push(err.message);
    }
  }

  const location = event.location;
  if (!location || location['@type'] !== 'Place' || !location.name) problems.push('location');
  const address = location && location.address;
  if (!address || address['@type'] !== 'PostalAddress') problems.push('address');
  else {
    for (const key of ['streetAddress', 'addressLocality', 'addressRegion', 'postalCode', 'addressCountry']) {
      if (typeof address[key] !== 'string' || !address[key]) problems.push(`address.${key}`);
    }
  }

  if (event.eventStatus !== 'https://schema.org/EventScheduled') problems.push('eventStatus');
  if (event.eventAttendanceMode !== 'https://schema.org/OfflineEventAttendanceMode') {
    problems.push('eventAttendanceMode');
  }

  const schedule = event.eventSchedule;
  if (!schedule || schedule['@type'] !== 'Schedule') problems.push('eventSchedule');
  else {
    if (schedule.byDay !== 'https://schema.org/Sunday') problems.push('byDay');
    if (schedule.startTime !== '10:00:00') problems.push('schedule startTime');
    if (schedule.endTime !== '13:00:00') problems.push('schedule endTime');
    if (schedule.repeatFrequency !== 'P1W') problems.push('repeatFrequency');
    if (schedule.scheduleTimezone !== 'America/New_York') problems.push('scheduleTimezone');
  }

  if (!event.organizer || event.organizer['@type'] !== 'Organization' || !event.organizer.name) {
    problems.push('organizer');
  }
  if (!event.performer || event.performer['@type'] !== 'MusicGroup' || !event.performer.name) {
    problems.push('performer');
  }

  problems.push(...wordingProblems(event));
  if (problems.length) {
    throw new Error(`Not a valid schema.org Event: ${problems.join('; ')}`);
  }
  return event;
}

function replaceDates(html, next) {
  const events = listJsonLd(html).filter((block) => /"@type"\s*:\s*"Event"/.test(block.raw));
  if (events.length !== 1) {
    throw new Error(`Expected one Event JSON-LD block, found ${events.length}.`);
  }
  const block = events[0];
  const starts = block.raw.match(/"startDate":/g) || [];
  const ends = block.raw.match(/"endDate":/g) || [];
  if (starts.length !== 1 || ends.length !== 1) {
    throw new Error('Event needs one startDate and one endDate.');
  }
  const raw = block.raw
    .replace(/"startDate": "[^"]*"/, `"startDate": "${next.startDate}"`)
    .replace(/"endDate": "[^"]*"/, `"endDate": "${next.endDate}"`);
  return html.slice(0, block.start) + raw + html.slice(block.end);
}

function publishHtml(html, now, bounds) {
  const next = nextJazzSunday(now, bounds);
  if (!next) return stripEvent(html);
  const updated = replaceDates(html, next);
  validateSchemaEvent(extractEvent(updated));
  return updated;
}

function safePublish(html, now, bounds) {
  try {
    return publishHtml(html, now, bounds);
  } catch {
    return stripEvent(html);
  }
}

function main() {
  const page = process.env.JAZZ_PAGE || PAGE;
  const datesFile = process.env.JAZZ_DATES || DATES;
  try {
    const html = fs.readFileSync(page, 'utf8');
    if (process.argv.includes('--strip-only')) {
      fs.writeFileSync(page, stripEvent(html));
      console.error('Removed the jazz brunch Event.');
      return;
    }
    const now = process.env.JAZZ_NOW ? new Date(process.env.JAZZ_NOW) : new Date();
    const bounds = JSON.parse(fs.readFileSync(datesFile, 'utf8'));
    const published = publishHtml(html, now, bounds);
    fs.writeFileSync(page, published);
    const event = extractEvent(published);
    if (event) console.log(`Jazz brunch Event set to ${event.startDate} – ${event.endDate}`);
    else console.log('Jazz brunch is outside the schedule window; Event removed.');
  } catch (err) {
    console.error('Jazz brunch stamp failed; removing the Event so the deploy can continue.');
    console.error(err && err.stack ? err.stack : err);
    try {
      const html = fs.readFileSync(page, 'utf8');
      fs.writeFileSync(page, stripEvent(html));
    } catch (stripErr) {
      console.error(stripErr && stripErr.stack ? stripErr.stack : stripErr);
    }
  }
}

module.exports = {
  addDays,
  assertBounds,
  extractEvent,
  nextJazzSunday,
  nyOffset,
  publishHtml,
  safePublish,
  stripEvent,
  validateSchemaEvent,
  weekdayIndex,
};

if (require.main === module) {
  process.on('uncaughtException', (err) => {
    console.error(err);
    try {
      const page = process.env.JAZZ_PAGE || PAGE;
      const html = fs.readFileSync(page, 'utf8');
      fs.writeFileSync(page, stripEvent(html));
    } catch (stripErr) {
      console.error(stripErr);
    }
    process.exit(0);
  });
  main();
}
