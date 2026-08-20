(function () {
  document.querySelectorAll<HTMLElement>("pre > code").forEach(function (code) {
    const pre = code.parentElement;
    if (!pre) return;
    if (pre.querySelector(".code-copy-btn")) return;
    const btn = document.createElement("button");
    btn.className = "code-copy-btn";
    btn.type = "button";
    btn.textContent = "Copy";
    btn.addEventListener("click", function () {
      navigator.clipboard.writeText(code.innerText).then(function () {
        btn.textContent = "Copied";
        setTimeout(function () {
          btn.textContent = "Copy";
        }, 1500);
      });
    });
    pre.appendChild(btn);
  });
})();