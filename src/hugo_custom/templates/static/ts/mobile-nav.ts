(function () {
  const btn = document.getElementById("nav-toggle");
  const sidebar = document.getElementById("sidebar");
  const backdrop = document.getElementById("sidebar-backdrop");
  if (!btn || !sidebar || !backdrop) return;

  function getMq(): MediaQueryList {
    let bp = "1100px";
    try {
      const v = getComputedStyle(document.documentElement).getPropertyValue("--bp-mobile").trim();
      if (v) bp = v;
    } catch (e) {}
    return window.matchMedia(`(max-width: ${bp})`);
  }

  const MQ = getMq();

  function isMobile(): boolean {
    return MQ.matches;
  }

  function isOpen(): boolean {
    return sidebar!.classList.contains("open");
  }

  function sidebarWidth(): number {
    return sidebar!.getBoundingClientRect().width || 320;
  }

  function open(): void {
    sidebar!.classList.add("open");
    sidebar!.classList.remove("dragging");
    sidebar!.style.transform = "";
    backdrop!.classList.add("visible");
    backdrop!.style.opacity = "";
    document.body.classList.add("nav-open");
    btn!.setAttribute("aria-expanded", "true");
  }

  function close(): void {
    sidebar!.classList.remove("open", "dragging");
    sidebar!.style.transform = "";
    backdrop!.classList.remove("visible");
    backdrop!.style.opacity = "";
    document.body.classList.remove("nav-open");
    btn!.setAttribute("aria-expanded", "false");
  }

  function toggle(): void {
    if (isOpen()) close();
    else open();
  }

  btn.addEventListener("click", function () {
    toggle();
  });

  const closeBtn = document.getElementById("sidebar-close");
  if (closeBtn) {
    closeBtn.addEventListener("click", function () {
      close();
    });
  }

  backdrop.addEventListener("click", function () {
    close();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && isOpen()) {
      close();
      btn!.focus();
    }
  });

  // Close drawer after navigating via a sidebar link (mobile only).
  sidebar.addEventListener("click", function (e) {
    const target = e.target as Element | null;
    const link = target?.closest("a");
    if (link && isMobile() && isOpen()) {
      close();
    }
  });

  // When resizing to desktop, ensure the drawer is closed so the
  // desktop sticky sidebar layout takes over.
  function onViewportChange(): void {
    if (!isMobile() && isOpen()) {
      close();
    }
  }

  // `addEventListener("change")` is the modern API; fallback to `addListener` for older browsers.
  if (typeof MQ.addEventListener === "function") {
    MQ.addEventListener("change", onViewportChange);
  } else {
    // eslint-disable-next-line deprecation/deprecation
    (MQ as any).addListener(onViewportChange);
  }

  // ---- touch gestures: edge-swipe to open, drag to close, like a native app drawer ----

  const EDGE_ZONE = 24; // px from the left edge that can start an "open" swipe
  const DISMISS_RATIO = 0.35; // fraction of drawer width to drag before it snaps closed
  const DISMISS_VELOCITY = 0.5; // px/ms - a fast flick closes regardless of distance

  let tracking = false;
  let startedFromEdge = false;
  let startX = 0;
  let startY = 0;
  let lastX = 0;
  let lastT = 0;
  let velocity = 0;
  let axisLocked: "x" | "y" | null = null;

  function clamp(n: number, min: number, max: number): number {
    return Math.max(min, Math.min(max, n));
  }

  function setDragOffset(dx: number): void {
    const w = sidebarWidth();
    const offset = clamp(dx, -w, 0);
    sidebar!.style.transform = `translateX(${offset}px)`;
    const progress = 1 - Math.abs(offset) / w;
    backdrop!.style.opacity = String(clamp(progress, 0, 1));
  }

  function onTouchStart(e: TouchEvent): void {
    if (!isMobile()) return;
    if (e.touches.length !== 1) return;
    const t = e.touches[0];

    if (isOpen()) {
      // Only start a close-drag if the touch begins on the open drawer itself.
      if (!(e.target instanceof Node) || !sidebar!.contains(e.target)) return;
      tracking = true;
      startedFromEdge = false;
    } else {
      // Only start an open-drag if the touch begins near the left edge of the screen.
      if (t.clientX > EDGE_ZONE) return;
      tracking = true;
      startedFromEdge = true;
      sidebar!.classList.add("dragging");
      backdrop!.style.opacity = "0";
      sidebar!.style.transform = `translateX(-${sidebarWidth()}px)`;
    }

    startX = t.clientX;
    startY = t.clientY;
    lastX = t.clientX;
    lastT = e.timeStamp;
    velocity = 0;
    axisLocked = null;
  }

  function onTouchMove(e: TouchEvent): void {
    if (!tracking) return;
    const t = e.touches[0];
    const dx = t.clientX - startX;
    const dy = t.clientY - startY;

    if (!axisLocked) {
      if (Math.abs(dx) < 6 && Math.abs(dy) < 6) return;
      axisLocked = Math.abs(dx) > Math.abs(dy) ? "x" : "y";
      if (axisLocked === "y") {
        // Vertical scroll intent - let the browser handle it.
        tracking = false;
        if (startedFromEdge) close();
        return;
      }
    }

    if (axisLocked !== "x") return;

    const dt = e.timeStamp - lastT;
    if (dt > 0) velocity = (t.clientX - lastX) / dt;
    lastX = t.clientX;
    lastT = e.timeStamp;

    const w = sidebarWidth();
    const offset = startedFromEdge ? -w + Math.max(dx, 0) : Math.min(dx, 0);
    setDragOffset(offset);
    e.preventDefault();
  }

  function onTouchEnd(): void {
    if (!tracking) return;
    tracking = false;
    sidebar!.classList.remove("dragging");

    const w = sidebarWidth();
    const matrix = new DOMMatrixReadOnly(getComputedStyle(sidebar!).transform);
    const currentOffset = matrix.m41; // translateX in px
    const draggedOpenFraction = 1 - Math.abs(currentOffset) / w;

    const flickOpen = velocity > DISMISS_VELOCITY;
    const flickClose = velocity < -DISMISS_VELOCITY;

    let shouldOpen: boolean;
    if (flickOpen) shouldOpen = true;
    else if (flickClose) shouldOpen = false;
    else shouldOpen = draggedOpenFraction > DISMISS_RATIO;

    if (shouldOpen) open();
    else close();
  }

  document.addEventListener("touchstart", onTouchStart, { passive: true });
  document.addEventListener("touchmove", onTouchMove, { passive: false });
  document.addEventListener("touchend", onTouchEnd);
  document.addEventListener("touchcancel", onTouchEnd);
})();
