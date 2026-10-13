(function () {
  var burger = document.getElementById("siteBurger");
  var menu = document.getElementById("siteMenu");
  if (!burger || !menu) return;

  function setOpen(open) {
    menu.classList.toggle("is-open", open);
    burger.setAttribute("aria-expanded", open ? "true" : "false");
    burger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    burger.textContent = open ? "✕" : "☰";
  }

  burger.addEventListener("click", function () {
    setOpen(!menu.classList.contains("is-open"));
  });
  menu.querySelectorAll("a").forEach(function (link) {
    link.addEventListener("click", function () { setOpen(false); });
  });
  window.matchMedia("(min-width: 1101px)").addEventListener("change", function (event) {
    if (event.matches) setOpen(false);
  });
})();

(function () {
  var nodes = document.querySelectorAll(".rise");
  if (!nodes.length || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  if (!("IntersectionObserver" in window)) return;

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      entry.target.classList.add("is-in");
      io.unobserve(entry.target);
    });
  }, { threshold: 0.2, rootMargin: "0px 0px -10% 0px" });

  nodes.forEach(function (el) {
    var top = el.getBoundingClientRect().top;
    if (top < window.innerHeight * 0.9 && top > -el.offsetHeight) return;
    io.observe(el);
  });
})();

(function () {
  var nav = document.querySelector(".menu-jumps");
  if (!nav || !("IntersectionObserver" in window)) return;
  var links = Array.prototype.slice.call(nav.querySelectorAll("a[href^='#']"));
  var sections = links.map(function (link) {
    return document.getElementById(link.getAttribute("href").slice(1));
  }).filter(Boolean);
  if (!sections.length) return;

  var current = "";
  var pinned = "";
  var pinArrived = false;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function setCurrent(id) {
    if (!id || id === current) return;
    current = id;
    links.forEach(function (link) {
      var on = link.getAttribute("href") === "#" + id;
      if (on) link.setAttribute("aria-current", "true");
      else link.removeAttribute("aria-current");
    });
    var active = nav.querySelector("[aria-current='true']");
    if (active && nav.scrollWidth > nav.clientWidth) {
      var left = active.offsetLeft - (nav.clientWidth - active.offsetWidth) / 2;
      nav.scrollTo({ left: Math.max(0, left), behavior: reduceMotion ? "auto" : "smooth" });
    }
  }

  links.forEach(function (link) {
    link.addEventListener("click", function () {
      pinned = link.getAttribute("href").slice(1);
      pinArrived = false;
      setCurrent(pinned);
    });
  });

  function band() {
    return {
      top: window.innerWidth < 761 ? 150 : 80,
      bottom: Math.max(280, window.innerHeight * 0.62)
    };
  }

  function pick() {
    var zone = band();
    if (pinned) {
      setCurrent(pinned);
      var pinnedBox = document.getElementById(pinned).getBoundingClientRect();
      var inZone = pinnedBox.bottom > zone.top && pinnedBox.top < zone.bottom;
      if (inZone) pinArrived = true;
      else if (pinArrived) pinned = "";
      if (pinned) return;
    }
    var hits = [];
    sections.forEach(function (section) {
      var box = section.getBoundingClientRect();
      if (box.bottom <= zone.top || box.top >= zone.bottom) return;
      var visibleTop = Math.max(box.top, zone.top);
      var visibleBottom = Math.min(box.bottom, zone.bottom);
      hits.push({
        id: section.id,
        height: Math.max(0, visibleBottom - visibleTop),
        total: box.height
      });
    });
    if (!hits.length) {
      var passed = null;
      sections.forEach(function (section) {
        var box = section.getBoundingClientRect();
        if (box.top > zone.top) return;
        if (!passed || box.bottom > passed.bottom) passed = { id: section.id, bottom: box.bottom };
      });
      setCurrent(passed ? passed.id : sections[0].id);
      return;
    }
    var tallest = hits.reduce(function (max, item) { return Math.max(max, item.height); }, 0);
    var tied = hits.filter(function (item) { return tallest - item.height < 12; });
    tied.sort(function (a, b) { return b.total - a.total; });
    setCurrent(tied[0].id);
  }

  var spy = new IntersectionObserver(function () { pick(); }, {
    rootMargin: "-12% 0px -55% 0px",
    threshold: [0, 0.25, 0.6]
  });
  sections.forEach(function (section) { spy.observe(section); });
  window.addEventListener("scroll", pick, { passive: true });
  pick();
})();
