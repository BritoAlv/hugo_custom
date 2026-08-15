(function () {
  var input = document.getElementById("search-input");
  if (!input) return;
  var results = document.getElementById("search-results");
  var index = [];
  var loaded = false;

  function load() {
    return fetch(input.dataset.index || "/index.json")
      .then(function (r) { return r.json(); })
      .then(function (data) { index = data; loaded = true; })
      .catch(function () {});
  }

  input.addEventListener("input", function () {
    var q = input.value.trim().toLowerCase();
    results.innerHTML = "";
    if (!q) {
      results.hidden = true;
      return;
    }
    var hits = index.filter(function (p) {
      var hay = (p.title || "") + " " + (p.summary || "") + " " + (p.tags || []).join(" ");
      return hay.toLowerCase().indexOf(q) !== -1;
    }).slice(0, 10);
    if (!hits.length) {
      var none = document.createElement("div");
      none.className = "search-result";
      none.textContent = "No results";
      results.appendChild(none);
    } else {
      hits.forEach(function (p) {
        var a = document.createElement("a");
        a.className = "search-result";
        a.href = p.url;
        var title = document.createElement("span");
        title.className = "search-title";
        title.textContent = p.title || p.url;
        a.appendChild(title);
        results.appendChild(a);
      });
    }
    results.hidden = false;
  });

  document.addEventListener("click", function (e) {
    if (!e.target.closest(".search-box")) results.hidden = true;
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", load);
  } else {
    load();
  }
})();