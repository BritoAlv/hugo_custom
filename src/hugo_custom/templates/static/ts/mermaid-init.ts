(function () {
  const mermaidApi = (window as unknown as { mermaid?: Record<string, unknown> }).mermaid;
  if (typeof mermaidApi === "undefined") return;

  let seq = 0;
  let lastDark: boolean;

  function isDark(): boolean {
    const attr = document.documentElement.getAttribute("data-theme");
    if (attr === "dark" || attr === "light") return attr === "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  }

  function renderAll(): void {
    const m = (window as unknown as {
      mermaid: {
        initialize: (config: Record<string, unknown>) => void;
        render: (id: string, source: string) => Promise<{ svg: string }>;
      };
    }).mermaid;
    m.initialize({ startOnLoad: false, theme: isDark() ? "dark" : "default" });
    const pending = Array.from(document.querySelectorAll<HTMLElement>("pre.mermaid"));
    for (const el of pending) {
      if (!el.dataset.mermaidSource) {
        el.dataset.mermaidSource = el.textContent || "";
      }
      el.innerHTML = "";
      el.classList.remove("rendered", "mermaid-error");
    }
    for (const el of pending) {
      const source = el.dataset.mermaidSource || "";
      if (!source.trim()) continue;
      m.render("mermaid-diagram-" + seq++, source)
        .then(({ svg }) => {
          el.innerHTML = svg;
          el.classList.add("rendered");
        })
        .catch((err: unknown) => {
          console.error("mermaid render failed:", err);
          el.classList.add("mermaid-error");
        });
    }
  }

  function applyTheme(): void {
    renderAll();
  }

  lastDark = isDark();
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", renderAll);
  } else {
    renderAll();
  }

  const observer = new MutationObserver(() => {
    const dark = isDark();
    if (dark !== lastDark) {
      lastDark = dark;
      applyTheme();
    }
  });
  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-theme"],
  });
})();