(function () {
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var porch = document.querySelector(".porch-lit");
  if (porch) {
    if (reduce || !("IntersectionObserver" in window)) porch.classList.add("is-on");
    else {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) entry.target.classList.add("is-on");
        });
      }, { threshold: 0.35 }).observe(porch);
    }
  }
  if (!reduce && "IntersectionObserver" in window) {
    document.querySelectorAll(".drink").forEach(function (el) {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          entry.target.classList.toggle("is-in", entry.isIntersecting);
        });
      }, { threshold: 0.45 }).observe(el);
    });
  }
  var video = document.getElementById("heroVideo");
  var videoBtn = document.getElementById("videoPause");
  if (video && !reduce) {
    var phone = window.matchMedia("(max-width: 800px)").matches;
    var base = phone ? "/video/bar-phone" : "/video/bar-desktop";
    video.innerHTML = '<source src="' + base + '.webm" type="video/webm"><source src="' + base + '.mp4" type="video/mp4">';
    var start = function () {
      var play = video.play();
      if (play && play.then) play.then(function () { video.classList.add("is-playing"); if (videoBtn) videoBtn.hidden = false; }).catch(function () {});
    };
    if (document.readyState === "complete") start();
    else window.addEventListener("load", start);
    if (videoBtn) {
      videoBtn.addEventListener("click", function () {
        if (video.paused) {
          video.play();
          videoBtn.textContent = "Pause video";
          videoBtn.setAttribute("aria-pressed", "false");
        } else {
          video.pause();
          videoBtn.textContent = "Play video";
          videoBtn.setAttribute("aria-pressed", "true");
        }
      });
    }
  }
  document.querySelectorAll("img[data-src]").forEach(function (img) {
    var load = function () {
      var pic = img.parentNode;
      if (pic && pic.querySelectorAll) {
        pic.querySelectorAll("source[data-srcset]").forEach(function (source) {
          source.srcset = source.getAttribute("data-srcset");
        });
      }
      if (img.getAttribute("data-srcset")) img.srcset = img.getAttribute("data-srcset");
      img.src = img.getAttribute("data-src");
      img.removeAttribute("data-src");
    };
    if (!("IntersectionObserver" in window)) load();
    else {
      new IntersectionObserver(function (entries, obs) {
        if (entries.some(function (entry) { return entry.isIntersecting; })) {
          load();
          obs.disconnect();
        }
      }, { rootMargin: "0px" }).observe(img);
    }
  });
  document.querySelectorAll(".door").forEach(function (door) {
    door.addEventListener("pointerdown", function () { door.classList.add("is-open"); });
    door.addEventListener("pointerup", function () { door.classList.remove("is-open"); });
    door.addEventListener("pointercancel", function () { door.classList.remove("is-open"); });
    door.addEventListener("pointerleave", function () { door.classList.remove("is-open"); });
  });
  var marquee = document.getElementById("marquee");
  var marqueeBtn = document.getElementById("marqueePause");
  if (marquee && marqueeBtn) {
    if (reduce) marquee.classList.add("is-paused");
    marqueeBtn.addEventListener("click", function () {
      var paused = marquee.classList.toggle("is-paused");
      marqueeBtn.setAttribute("aria-pressed", paused ? "true" : "false");
      marqueeBtn.textContent = paused ? "Play" : "Pause";
    });
  }
})();
