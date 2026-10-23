(function () {
  'use strict';
  var d = document, root = d.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  // Dinner and any-day Reserve controls stay on the standard booking link.
  var OT_RESERVE = 'https://www.opentable.com/r/sipsoberbar-reservations-gulfport?restref=1563214&lang=en-US&ot_source=Restaurant%20website&ot_campaign=site-widget';
  // Jazz brunch buttons and the brunch side of the chooser use the experience.
  var OT_BRUNCH = 'https://www.opentable.com/booking/experiences-availability?rid=1563214&experienceId=833122&shareReferrer=web&ot_source=Restaurant%20website&ot_campaign=site-brunch';

  /* ---- Gulfport time ---- */
  function nowGulfport() {
    var parts = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', weekday: 'short', hour: 'numeric', minute: 'numeric', hourCycle: 'h23' }).formatToParts(new Date());
    var o = {};
    parts.forEach(function (p) { o[p.type] = p.value; });
    var days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    return { day: days.indexOf(o.weekday), min: (+o.hour % 24) * 60 + (+o.minute) };
  }
  function closeMin(day) { return day === 5 || day === 6 ? 1440 : 1320; }
  function fmt(m) {
    m = Math.round(m) % 1440;
    var h = Math.floor(m / 60), mm = m % 60, ap = h >= 12 ? 'PM' : 'AM';
    h = h % 12 || 12;
    return { t: h + ':' + (mm < 10 ? '0' : '') + mm, ap: ap };
  }
  var g = nowGulfport();
  var open = g.min >= 420 && g.min < closeMin(g.day);
  var brunchNow = g.day === 0 && g.min >= 600 && g.min < 780;

  d.querySelectorAll('[data-status]').forEach(function (el) {
    var txt;
    if (brunchNow) txt = 'Jazz brunch is on now · until 1pm';
    else if (open) txt = 'Open now · until ' + (closeMin(g.day) === 1440 ? 'midnight' : '10pm');
    else txt = 'Closed now · doors at 7am';
    el.querySelector('span').textContent = txt;
    el.classList.toggle('closed', !open);
  });
  d.querySelectorAll('.hours tr[data-d]').forEach(function (tr) {
    if (tr.getAttribute('data-d').split(',').indexOf(String(g.day)) > -1) tr.classList.add('today');
  });

  /* ---- Sunday morning: the hero sells brunch ---- */
  if (g.day === 0 && g.min < 780) {
    d.querySelectorAll('[data-cta="hero"]').forEach(function (a) {
      a.removeAttribute('data-reserve');
      a.href = OT_BRUNCH;
      a.setAttribute('data-cta', 'hero-sunday');
      a.firstChild.textContent = 'Reserve Sunday brunch ';
    });
  }

  /* ---- hero: scrub through the day ---- */
  var hero = d.querySelector('.hero');
  if (hero) {
    var range = hero.querySelector('.scrub'), knobT = hero.querySelectorAll('.knob b'), knobS = hero.querySelectorAll('.knob small'), moment = hero.querySelector('.moment');
    var moments = [[420, 'Espresso & free, fast WiFi'], [690, 'The kitchen’s on'], [1020, 'Porch lights on'], [1200, 'Cocktails after dark'], [1320, 'Fri & Sat, till midnight']];
    var nclip = hero.querySelector('.nclip'), nlay = nclip.firstElementChild, seamEl = hero.querySelector('.seam'), prog = hero.querySelector('.prog');
    var fade = window.matchMedia('(max-width: 760px)');
    var W = 0, G = 0, measure = function () { W = hero.clientWidth; G = parseFloat(getComputedStyle(hero.querySelector('.timeline')).left) || 0; };
    measure();
    var ticks = [].map.call(hero.querySelectorAll('.timeline span'), function (el) { return { el: el, f: parseFloat(el.style.left) / 100 }; });
    var lastLabel = '', lastT = '', cur = 500;
    var set = function (v, live) {
      cur = v;
      var p = Math.min(.985, Math.max(.015, v / 1020)), x = G + p * (W - 2 * G), m = 420 + v, f = fmt(m);
      if (fade.matches) {
        // phone: crossfade the whole image, mostly day before 4pm, mostly night after 7pm
        var n = Math.min(1, Math.max(0, (m - 900) / 240));
        nclip.style.opacity = n.toFixed(3);
      } else {
        nclip.style.opacity = '';
        nclip.style.transform = 'translate3d(' + (x - W) + 'px,0,0)';
        nlay.style.transform = 'translate3d(' + (W - x) + 'px,0,0)';
      }
      seamEl.style.transform = 'translate3d(' + x + 'px,0,0)';
      prog.style.transform = 'scaleX(' + p + ')';
      ticks.forEach(function (t) {
        if (t.w === undefined) { t.w = t.el.offsetWidth; t.a = t.el.classList.contains('tend') ? 1 : (t.f === 0 ? 0 : .5); }
        var c = G + t.f * (W - 2 * G), l = c - t.w * t.a, r = l + t.w, kx = x;
        t.el.classList.toggle('near', kx + 40 > l && kx - 40 < r);
      });
      var flip = p > .5;
      if (moment) moment.style.transform = 'translate3d(' + (flip ? x - 48 : x + 48) + 'px,0,0)' + (flip ? ' translateX(-100%)' : '');
      var tt = f.t + f.ap + (live ? 1 : 0);
      if (tt !== lastT) { lastT = tt; knobT.forEach(function (n) { n.textContent = f.t; }); knobS.forEach(function (n) { n.textContent = live && !open ? 'Preview' : f.ap + (live ? ' · now' : ''); }); }
      var label = moments[0][1];
      moments.forEach(function (x2) { if (m >= x2[0]) label = x2[1]; });
      if (label !== lastLabel && moment) { lastLabel = label; moment.lastChild.textContent = label; }
      hero.classList.toggle('flip', flip);
      range.setAttribute('aria-valuetext', f.t + ' ' + f.ap + ', ' + label);
    };
    window.addEventListener('resize', function () { measure(); set(cur, false); });
    // open: start at the real Gulfport time. closed: park at 8pm and label it a preview.
    var target = open ? Math.min(1019, Math.max(0, g.min - 420)) : 780;
    if (!open) {
      hero.classList.add('preview');
      if (moment) moment.firstChild.textContent = 'Preview the day · drag';
      knobS.forEach(function (n) { n.textContent = 'Preview'; });
    }
    range.value = target;
    if (reduce) set(target, true);
    else {
      var from = 40, dur = 2000, done = false, t0;
      var finish = function () { if (done) return; done = true; if (!hero.classList.contains('touched')) set(target, true); };
      set(from, false);
      setTimeout(function () {
        t0 = performance.now();
        (function step(now) {
          if (done || hero.classList.contains('touched')) return;
          var k = Math.min(1, ((now || performance.now()) - t0) / dur), e = k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
          if (k >= 1) return finish();
          set(from + (target - from) * e, false);
          requestAnimationFrame(step);
        })(t0);
        setTimeout(finish, dur + 120);
      }, 400);
    }
    range.addEventListener('input', function () {
      hero.classList.add('touched');
      set(+range.value, false);
    });
  }

  /* ---- header + dock ---- */
  var head = d.querySelector('.head'), dock = d.querySelector('.dock');
  var onScroll = function () {
    var y = window.scrollY;
    if (head) head.classList.toggle('solid', y > 40);
    if (dock) dock.classList.toggle('show', !hero || y > window.innerHeight * .6);
  };
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---- mobile drawer ---- */
  var drawer = d.getElementById('drawer'), burger = d.querySelector('.burger');
  if (drawer && burger) {
    var bg = [d.querySelector('.head'), d.getElementById('main'), d.querySelector('.foot'), d.querySelector('.dock'), d.querySelector('.skip')].filter(Boolean);
    var focusables = function () { return [].slice.call(drawer.querySelectorAll('a,button')); };
    var toggle = function (o) {
      drawer.classList.toggle('open', o);
      burger.setAttribute('aria-expanded', o);
      drawer.inert = !o;
      bg.forEach(function (el) { el.inert = o; });
      d.body.classList.toggle('locked', o);
      if (o) focusables()[1].focus(); else burger.focus();
    };
    drawer.inert = true;
    burger.addEventListener('click', function () { toggle(true); });
    drawer.querySelector('.close').addEventListener('click', function () { toggle(false); });
    drawer.addEventListener('click', function (e) { if (e.target.closest('a')) { bg.forEach(function (el) { el.inert = false; }); d.body.classList.remove('locked'); } });
    d.addEventListener('keydown', function (e) {
      if (!drawer.classList.contains('open')) return;
      if (e.key === 'Escape') return toggle(false);
      if (e.key === 'Tab') {
        var f = focusables(), first = f[0], last = f[f.length - 1];
        if (e.shiftKey && d.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && d.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });
  }

  /* ---- reserve chooser ---- */
  d.querySelectorAll('[data-cta="chooser-dinner"]').forEach(function (a) { a.href = OT_RESERVE; });
  d.querySelectorAll('[data-cta="chooser-brunch"]').forEach(function (a) { a.href = OT_BRUNCH; });
  var dlg = d.getElementById('reserve');
  if (dlg && dlg.showModal) {
    d.addEventListener('click', function (e) {
      var a = e.target.closest('[data-reserve]');
      if (!a) return;
      e.preventDefault();
      if (drawer && drawer.classList.contains('open')) drawer.querySelector('.close').click();
      dlg.showModal();
    });
    dlg.querySelector('.x').addEventListener('click', function () { dlg.close(); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
  }

  /* ---- OpenTable widget: load when the booking panel is near the screen ---- */
  var otMount = d.getElementById('ot-mount');
  var otTpl = d.getElementById('ot-widget-embed');
  if (otMount && otTpl) {
    var loadOt = function () {
      if (otMount.dataset.loaded) return;
      var proto = otTpl.content && otTpl.content.querySelector('script');
      if (!proto) return;
      otMount.dataset.loaded = '1';
      var s = d.createElement('script');
      s.async = false;
      s.src = proto.getAttribute('src');
      otMount.appendChild(s);
    };
    if ('IntersectionObserver' in window) {
      var otIo = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (!e.isIntersecting) return;
          loadOt();
          otIo.disconnect();
        });
      }, { rootMargin: '280px 0px' });
      otIo.observe(otMount);
    } else loadOt();
  }

  /* ---- marquee pause ---- */
  d.querySelectorAll('.marq button').forEach(function (b) {
    b.addEventListener('click', function () {
      var m = b.closest('.marq'), p = m.classList.toggle('paused');
      b.textContent = p ? 'Play' : 'Pause';
      b.setAttribute('aria-pressed', p);
    });
  });

  /* ---- reveals, porch lights, lazy video, menu tabs ---- */
  if ('IntersectionObserver' in window) {
    // content is visible by default; only items the observer reports as below the fold get hidden, then revealed
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        var el = e.target, porch = el.classList.contains('porch');
        if (e.isIntersecting) {
          el.classList.remove('pre', 'dim');
          io.unobserve(el);
        } else if (e.boundingClientRect.top > 0 && !el.dataset.seen) {
          el.classList.add(porch ? 'dim' : 'pre');
          el.dataset.seen = '1';
        } else el.dataset.seen = '1';
      });
    }, { rootMargin: '0px 0px -12% 0px' });
    d.querySelectorAll('.rv,.rvimg,.porch').forEach(function (el) { io.observe(el); });
    setTimeout(function () { d.querySelectorAll('.pre,.dim').forEach(function (el) { var r = el.getBoundingClientRect(); if (r.top < innerHeight && r.bottom > 0) el.classList.remove('pre', 'dim'); }); }, 4000);

    var vids = d.querySelectorAll('video[data-src]');
    var vio = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        var v = e.target;
        if (e.isIntersecting) {
          if (!v.src) { v.src = window.innerWidth < 700 ? v.getAttribute('data-src-tall') : v.getAttribute('data-src'); }
          if (!reduce && !v.dataset.paused) v.play().catch(function () {});
        } else v.pause();
      });
    }, { threshold: .2 });
    // start loops only once the visitor scrolls, so the first view shows the still poster
    if (vids.length) window.addEventListener('scroll', function () { vids.forEach(function (v) { vio.observe(v); }); }, { once: true, passive: true });

    var tabs = d.querySelectorAll('.tabs a');
    if (tabs.length) {
      var tio = new IntersectionObserver(function (es) {
        es.forEach(function (e) {
          if (!e.isIntersecting) return;
          tabs.forEach(function (t) { t.classList.toggle('on', t.getAttribute('href') === '#' + e.target.id); });
        });
      }, { rootMargin: '-40% 0px -55% 0px' });
      tabs.forEach(function (t) { var s = d.querySelector(t.getAttribute('href')); if (s) tio.observe(s); });
    }
  }
  d.querySelectorAll('.loopband button').forEach(function (b) {
    b.addEventListener('click', function () {
      var v = b.parentNode.querySelector('video');
      if (v.paused) { v.dataset.paused = ''; delete v.dataset.paused; if (!v.src) v.src = v.getAttribute('data-src'); v.play(); b.textContent = 'Pause video'; }
      else { v.pause(); v.dataset.paused = '1'; b.textContent = 'Play video'; }
    });
  });

  /* ---- event inquiry: compose an email draft ---- */
  var form = d.getElementById('inquiry');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var f = new FormData(form), lines = [];
      f.forEach(function (v, k) { if (v) lines.push(k + ': ' + v); });
      location.href = 'mailto:Sean@sipsoberbar.com?subject=' + encodeURIComponent('Private event inquiry: ' + (f.get('Occasion') || 'Sober Bar')) + '&body=' + encodeURIComponent(lines.join('\n'));
    });
  }
})();
