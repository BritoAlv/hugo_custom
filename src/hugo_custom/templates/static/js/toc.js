(function () {
  var rail = document.querySelector(".toc-rail");
  if (!rail) return;
  if (getComputedStyle(rail).display === "none") return;

  var links = Array.prototype.slice.call(rail.querySelectorAll('a[href^="#"]'));
  var items = [];
  links.forEach(function (link) {
    var el = document.getElementById(link.getAttribute("href").slice(1));
    if (el) items.push({ link: link, el: el });
  });
  if (!items.length) return;

  var active = null;

  function reveal(link) {
    var railRect = rail.getBoundingClientRect();
    var linkRect = link.getBoundingClientRect();
    if (linkRect.top < railRect.top) {
      rail.scrollTop -= railRect.top - linkRect.top;
    } else if (linkRect.bottom > railRect.bottom) {
      rail.scrollTop += linkRect.bottom - railRect.bottom;
    }
  }

  function setActive(item) {
    links.forEach(function (link) { link.classList.remove("active"); });
    if (item) {
      item.link.classList.add("active");
      reveal(item.link);
    }
  }

  function topmostInBand(els) {
    var inBand = els
      .filter(function (e) { return e.isIntersecting; })
      .sort(function (a, b) {
        return a.boundingClientRect.top - b.boundingClientRect.top;
      });
    if (!inBand.length) return null;
    var id = inBand[0].target.id;
    var hit = null;
    items.forEach(function (item) {
      if (item.el.id === id) hit = item;
    });
    return hit;
  }

  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      var next = topmostInBand(entries);
      if (next && next !== active) {
        active = next;
        setActive(next);
      }
    }, { rootMargin: "0px 0px -75% 0px" });
    items.forEach(function (item) { io.observe(item.el); });
  } else {
    var ticking = false;
    window.addEventListener("scroll", function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(function () {
        ticking = false;
        var next = null;
        items.forEach(function (item) {
          if (item.el.getBoundingClientRect().top <= 53) next = item;
        });
        if (next && next !== active) {
          active = next;
          setActive(next);
        }
      });
    }, { passive: true });
  }
})();