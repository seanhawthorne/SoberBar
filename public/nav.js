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
      nav.scrollTo({ left: Math.max(0, left), behavior: "smooth" });
    }
  }

  function pick() {
    var line = window.innerWidth < 761 ? 150 : 108;
    var hit = null;
    sections.forEach(function (section) {
      var box = section.getBoundingClientRect();
      if (box.top <= line && box.bottom > line) {
        if (!hit || box.left < hit.left - 8) hit = { id: section.id, left: box.left };
      }
    });
    setCurrent(hit ? hit.id : sections[0].id);
  }

  var spy = new IntersectionObserver(function () { pick(); }, {
    rootMargin: "-12% 0px -55% 0px",
    threshold: [0, 0.25, 0.6]
  });
  sections.forEach(function (section) { spy.observe(section); });
  window.addEventListener("scroll", pick, { passive: true });
  pick();
})();
