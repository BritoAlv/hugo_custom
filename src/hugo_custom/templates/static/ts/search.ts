interface IndexItem {
  title?: string;
  summary?: string;
  tags?: string[];
  url: string;
}

(function () {
  const input = document.getElementById("search-input") as HTMLInputElement | null;
  if (!input) return;
  const results = document.getElementById("search-results");
  if (!results) return;
  let index: IndexItem[] = [];

  const load = (): void => {
    fetch(input.dataset.index || "/index.json")
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        index = data as IndexItem[];
      })
      .catch(function () {});
  };

  input.addEventListener("input", function () {
    const q = input.value.trim().toLowerCase();
    results.innerHTML = "";
    if (!q) {
      results.hidden = true;
      return;
    }
    const hits = index
      .filter(function (p) {
        const hay =
          (p.title || "") + " " + (p.summary || "") + " " + (p.tags || []).join(" ");
        return hay.toLowerCase().indexOf(q) !== -1;
      })
      .slice(0, 10);
    if (!hits.length) {
      const none = document.createElement("div");
      none.className = "search-result";
      none.textContent = "No results";
      results.appendChild(none);
    } else {
      hits.forEach(function (p) {
        const a = document.createElement("a");
        a.className = "search-result";
        a.href = p.url;
        const title = document.createElement("span");
        title.className = "search-title";
        title.textContent = p.title || p.url;
        a.appendChild(title);
        results.appendChild(a);
      });
    }
    results.hidden = false;
  });

  document.addEventListener("click", function (e) {
    const target = e.target as Element | null;
    if (!target || !target.closest(".search-box")) results.hidden = true;
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", load);
  } else {
    load();
  }
})();