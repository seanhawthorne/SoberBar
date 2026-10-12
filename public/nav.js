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

  function show(el) { el.classList.add("is-in"); }

  nodes.forEach(function (el) {
    if (el.getBoundingClientRect().top < window.innerHeight * 0.92) show(el);
  });
  document.documentElement.classList.add("js-rise");

  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      show(entry.target);
      io.unobserve(entry.target);
    });
  }, { threshold: 0.18, rootMargin: "0px 0px -8% 0px" });

  nodes.forEach(function (el) {
    if (!el.classList.contains("is-in")) io.observe(el);
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

  var spy = new IntersectionObserver(function (entries) {
    var visible = entries.filter(function (entry) { return entry.isIntersecting; });
    if (!visible.length) return;
    visible.sort(function (a, b) { return b.intersectionRatio - a.intersectionRatio; });
    setCurrent(visible[0].target.id);
  }, { rootMargin: "-28% 0px -55% 0px", threshold: [0, 0.2, 0.5, 0.8] });

  sections.forEach(function (section) { spy.observe(section); });
  setCurrent(sections[0].id);
})();
