(function () {
  var sidebar = document.querySelector(".sidebar");
  if (!sidebar) return;

  var KEY = "hugo-custom-sidebar-open";

  function loadState() {
    try {
      return JSON.parse(localStorage.getItem(KEY)) || {};
    } catch (e) {
      return {};
    }
  }

  function saveState(state) {
    try {
      localStorage.setItem(KEY, JSON.stringify(state));
    } catch (e) {}
  }

  function labelPath(section) {
    var parts = [];
    var node = section;
    while (node && node.classList.contains("sidebar-section")) {
      var label = node.querySelector(".sidebar-section-label");
      if (label) parts.unshift(label.textContent.trim());
      node = node.parentElement.closest(".sidebar-section");
    }
    return parts.join("/");
  }

  function setOpen(section, open) {
    section.classList.toggle("collapsed", !open);
    var btn = section.querySelector(":scope > .sidebar-section-toggle");
    if (btn) btn.setAttribute("aria-expanded", open ? "true" : "false");
  }

  var state = loadState();

  sidebar.querySelectorAll(".sidebar-section").forEach(function (section) {
    var key = labelPath(section);
    setOpen(section, key in state ? !!state[key] : false);
  });

  var active = sidebar.querySelector(".sidebar-item a.active");
  if (active) {
    var li = active.closest(".sidebar-section");
    while (li) {
      setOpen(li, true);
      state[labelPath(li)] = true;
      li = li.parentElement.closest(".sidebar-section");
    }
    saveState(state);
  }

  sidebar.addEventListener("click", function (e) {
    var btn = e.target.closest(".sidebar-section-toggle");
    if (!btn) return;
    var section = btn.closest(".sidebar-section");
    if (!section) return;
    var open = section.classList.contains("collapsed");
    setOpen(section, open);
    state[labelPath(section)] = open;
    saveState(state);
  });
})();