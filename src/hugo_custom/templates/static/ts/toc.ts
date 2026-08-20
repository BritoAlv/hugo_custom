interface TocItem {
  link: HTMLAnchorElement;
  el: HTMLElement;
}

(function () {
  const rail = document.querySelector<HTMLElement>(".toc-rail");
  if (!rail) return;
  if (getComputedStyle(rail).display === "none") return;

  const links = Array.prototype.slice.call(
    rail.querySelectorAll('a[href^="#"]')
  ) as HTMLAnchorElement[];
  const items: TocItem[] = [];
  links.forEach(function (link) {
    const href = link.getAttribute("href");
    if (!href) return;
    const el = document.getElementById(href.slice(1));
    if (el) items.push({ link: link, el: el });
  });
  if (!items.length) return;

  let active: TocItem | null = null;

  const reveal = (link: HTMLAnchorElement): void => {
    const railRect = rail.getBoundingClientRect();
    const linkRect = link.getBoundingClientRect();
    if (linkRect.top < railRect.top) {
      rail.scrollTop -= railRect.top - linkRect.top;
    } else if (linkRect.bottom > railRect.bottom) {
      rail.scrollTop += linkRect.bottom - railRect.bottom;
    }
  };

  const setActive = (item: TocItem | null): void => {
    links.forEach(function (link) {
      link.classList.remove("active");
    });
    if (item) {
      item.link.classList.add("active");
      reveal(item.link);
    }
  };

  const topmostInBand = (entries: IntersectionObserverEntry[]): TocItem | null => {
    const inBand = entries
      .filter(function (e) {
        return e.isIntersecting;
      })
      .sort(function (a, b) {
        return a.boundingClientRect.top - b.boundingClientRect.top;
      });
    if (!inBand.length) return null;
    const id = inBand[0].target.id;
    let hit: TocItem | null = null;
    items.forEach(function (item) {
      if (item.el.id === id) hit = item;
    });
    return hit;
  }

  if (window.IntersectionObserver) {
    const io = new IntersectionObserver(
      function (entries) {
        const next = topmostInBand(entries);
        if (next && next !== active) {
          active = next;
          setActive(next);
        }
      },
      { rootMargin: "0px 0px -75% 0px" }
    );
    items.forEach(function (item) {
      io.observe(item.el);
    });
  } else {
    let ticking = false;
    window.addEventListener(
      "scroll",
      function () {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(function () {
          ticking = false;
          let next: TocItem | null = null;
          items.forEach(function (item) {
            if (item.el.getBoundingClientRect().top <= 53) next = item;
          });
          if (next && next !== active) {
            active = next;
            setActive(next);
          }
        });
      },
      { passive: true }
    );
  }
})();