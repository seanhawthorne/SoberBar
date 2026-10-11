(function () {
  var header = document.querySelector('.site-header');
  var burger = document.getElementById('burger');
  var drawer = document.getElementById('drawer');
  var sticky = document.querySelector('.sticky');
  var heroCta = document.querySelector('[data-hero-cta]');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function setHeader() {
    if (!header) return;
    header.classList.toggle('is-shrunk', window.scrollY > 120);
  }
  setHeader();
  window.addEventListener('scroll', setHeader, { passive: true });

  if (burger && drawer) {
    burger.addEventListener('click', function () {
      var open = drawer.classList.toggle('is-open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
      burger.textContent = open ? 'Close' : 'Menu';
    });
    drawer.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        drawer.classList.remove('is-open');
        burger.setAttribute('aria-expanded', 'false');
        burger.textContent = 'Menu';
      });
    });
  }

  if (sticky) {
    var show = function (on) { sticky.classList.toggle('is-on', on); };
    if (!heroCta || window.matchMedia('(min-width: 768px)').matches) {
      if (window.matchMedia('(max-width: 767px)').matches && !heroCta) show(true);
    }
    if (heroCta && 'IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        var visible = entries[0].isIntersecting;
        show(!visible && window.matchMedia('(max-width: 767px)').matches);
      }, { threshold: 0.2 });
      io.observe(heroCta);
    }
  }

  if (!reduce && 'IntersectionObserver' in window) {
    document.querySelectorAll('.reveal').forEach(function (el) {
      el.style.animationPlayState = 'paused';
      var io = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) {
          el.style.animationPlayState = 'running';
          io.disconnect();
        }
      }, { threshold: 0.15 });
      io.observe(el);
    });
  }

  var chips = document.querySelectorAll('.chips a');
  if (chips.length && 'IntersectionObserver' in window) {
    var ticking = false;
    var current = chips[0];
    var secs = [];
    chips.forEach(function (a) {
      var id = a.getAttribute('href').slice(1);
      var sec = document.getElementById(id);
      if (sec) secs.push({ a: a, sec: sec });
    });
    function mark() {
      ticking = false;
      var y = window.scrollY + 120;
      var active = secs[0];
      secs.forEach(function (item) {
        if (item.sec.offsetTop <= y) active = item;
      });
      if (active && active.a !== current) {
        current.classList.remove('is-active');
        active.a.classList.add('is-active');
        current = active.a;
      }
    }
    chips[0].classList.add('is-active');
    window.addEventListener('scroll', function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(mark);
    }, { passive: true });
  }
})();
