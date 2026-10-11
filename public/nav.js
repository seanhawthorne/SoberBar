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
