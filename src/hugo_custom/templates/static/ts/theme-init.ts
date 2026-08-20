(function () {
  try {
    let theme: "dark" | "light" | null = null;
    const saved = localStorage.getItem("hugo-custom-theme");
    if (saved === "dark" || saved === "light") {
      theme = saved;
    } else if (window.matchMedia("(prefers-color-scheme: dark)").matches) {
      theme = "dark";
    }
    document.documentElement.setAttribute("data-theme", theme || "light");
  } catch (e) {}
})();