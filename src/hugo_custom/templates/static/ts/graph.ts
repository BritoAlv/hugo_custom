interface GraphNode {
  id: string;
  label: string;
  kind: string;
  degree: number;
}

interface GraphLink {
  source: string;
  target: string;
}

interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface GraphParams {
  data?: { url?: string; label?: string; kind?: string; value?: number };
  dataType?: string;
}

(function () {
  const container = document.getElementById("graph-container");
  if (!container) return;
  const el: HTMLElement = container;
  const counts = document.getElementById("graph-counts");
  const resetBtn = document.getElementById("graph-reset") as HTMLButtonElement | null;
  const kindInputs = Array.from(
    document.querySelectorAll<HTMLInputElement>(".graph-kind")
  );
  const message = document.createElement("div");
  message.className = "graph-message";
  message.hidden = true;
  el.appendChild(message);

  let chart: echarts.ECharts | null = null;
  let allNodes: GraphNode[] = [];
  let allLinks: GraphLink[] = [];

  function cssVar(name: string, fallback: string): string {
    const value = getComputedStyle(document.documentElement)
      .getPropertyValue(name)
      .trim();
    return value || fallback;
  }

  function readPalette(): Record<string, string> {
    return {
      link: cssVar("--graph-link", "#c9cdd4"),
      label: cssVar("--graph-label", "#4b5563"),
      md: cssVar("--graph-md", "#2b6cb0"),
      nb: cssVar("--graph-nb", "#805ad5"),
      code: cssVar("--graph-code", "#d69e2e"),
      file: cssVar("--graph-file", "#6b7280"),
    };
  }

  function radiusOf(node: GraphNode): number {
    return (4 + Math.sqrt(Math.max(0, node.degree)) * 2.2) * 2;
  }

  function activeKinds(): Set<string> {
    return new Set(kindInputs.filter((i) => i.checked).map((i) => i.value));
  }

  function optionFor(data: GraphNode[], links: GraphLink[]): unknown {
    const palette = readPalette();
    return {
      backgroundColor: "transparent",
      tooltip: {
        formatter: (params: GraphParams) => {
          if (params.dataType === "edge") return "";
          const d = params.data;
          if (!d || !d.label) return "";
          return `<strong>${d.label}</strong><br>${d.kind || ""} · ${
            d.value ?? 0
          } link${(d.value ?? 0) === 1 ? "" : "s"}`;
        },
      },
      series: [
        {
          type: "graph",
          layout: "force",
          draggable: true,
          roam: true,
          focusNodeAdjacency: true,
          force: {
            repulsion: 220,
            edgeLength: 90,
            gravity: 0.12,
            friction: 0.6,
            layoutAnimation: true,
          },
          label: { show: false },
          emphasis: {
            label: {
              show: true,
              position: "top",
              distance: 6,
              fontSize: 11,
              color: palette.label,
            },
          },
          edgeSymbol: ["none", "arrow"],
          edgeSymbolSize: [0, 8],
          lineStyle: {
            color: palette.link,
            width: 1.2,
            curveness: 0.05,
            opacity: 0.6,
          },
          data: data.map((n) => ({
            id: n.id,
            name: n.label,
            value: n.degree,
            category: n.kind,
            symbolSize: radiusOf(n),
            url: n.id,
            itemStyle: { color: palette[n.kind] || palette.file },
          })),
          links: links.map((l) => ({ source: l.source, target: l.target })),
        },
      ],
    };
  }

  function render(): void {
    const kinds = activeKinds();
    const visible = allNodes.filter((n) => kinds.has(n.kind));
    const visibleIds = new Set(visible.map((n) => n.id));
    const visibleLinks = allLinks.filter(
      (l) => visibleIds.has(l.source) && visibleIds.has(l.target)
    );
    if (!chart) {
      chart = echarts.init(el);
      chart.on("click", (params: unknown) => {
        const p = params as GraphParams;
        const url = p.data && p.data.url;
        if (url) window.location.href = url;
      });
    }
    chart.setOption(optionFor(visible, visibleLinks), { notMerge: true });
    if (counts) {
      counts.textContent = `${visible.length} nodes · ${visibleLinks.length} links`;
    }
  }

  function resetView(): void {
    render();
  }

  kindInputs.forEach((input) => {
    input.addEventListener("change", render);
  });

  resetBtn?.addEventListener("click", resetView);

  const resizeObserver = new ResizeObserver(() => {
    if (chart) chart.resize();
  });
  resizeObserver.observe(el);

  const themeObserver = new MutationObserver(() => {
    if (chart) {
      chart.dispose();
      chart = null;
      render();
    }
  });
  themeObserver.observe(document.documentElement, {
    attributes: true,
    attributeFilter: ["data-theme"],
  });

  function load(): void {
    fetch(el.dataset.graph || "js/graph-data.json")
      .then((r) => {
        if (!r.ok) throw new Error(String(r.status));
        return r.json();
      })
      .then((data) => {
        allNodes = (data.nodes as GraphNode[]) || [];
        allLinks = (data.links as GraphLink[]) || [];
        if (!allNodes.length) {
          message.textContent = "No content yet — nothing to show in the graph.";
          message.hidden = false;
          return;
        }
        render();
      })
      .catch((err: unknown) => {
        console.error("graph data failed to load:", err);
        message.textContent = "Graph data could not be loaded.";
        message.hidden = false;
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", load);
  } else {
    load();
  }
})();