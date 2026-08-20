(function () {
  const sidebar = document.querySelector<HTMLElement>(".sidebar");
  if (!sidebar) return;

  const KEY = "hugo-custom-sidebar-open";

  function loadState(): Record<string, boolean> {
    try {
      const parsed: unknown = JSON.parse(localStorage.getItem(KEY) || "{}");
      return typeof parsed === "object" && parsed !== null ? (parsed as Record<string, boolean>) : {};
    } catch (e) {
      return {};
    }
  }

  function saveState(state: Record<string, boolean>): void {
    try {
      localStorage.setItem(KEY, JSON.stringify(state));
    } catch (e) {}
  }

  function labelPath(section: Element): string {
    const parts: string[] = [];
    let node: Element | null = section;
    while (node && node.classList.contains("sidebar-section")) {
      const label = node.querySelector(".sidebar-section-label");
      const text = label ? label.textContent?.trim() : null;
      if (text) parts.unshift(text);
      node = node.parentElement?.closest(".sidebar-section") ?? null;
    }
    return parts.join("/");
  }

  function setOpen(section: Element, open: boolean): void {
    section.classList.toggle("collapsed", !open);
    const btn = section.querySelector<HTMLElement>(":scope > .sidebar-section-toggle");
    if (btn) btn.setAttribute("aria-expanded", open ? "true" : "false");
  }

  const state = loadState();

  sidebar.querySelectorAll(".sidebar-section").forEach(function (section) {
    const key = labelPath(section);
    setOpen(section, key in state ? !!state[key] : false);
  });

  const active = sidebar.querySelector<HTMLAnchorElement>(".sidebar-item a.active");
  if (active) {
    let li = active.closest(".sidebar-section");
    while (li) {
      setOpen(li, true);
      state[labelPath(li)] = true;
      li = li.parentElement?.closest(".sidebar-section") ?? null;
    }
    saveState(state);
  }

  sidebar.addEventListener("click", function (e) {
    const target = e.target as Element | null;
    const btn = target?.closest(".sidebar-section-toggle");
    if (!btn) return;
    const section = btn.closest(".sidebar-section");
    if (!section) return;
    const open = section.classList.contains("collapsed");
    setOpen(section, open);
    state[labelPath(section)] = open;
    saveState(state);
  });
})();