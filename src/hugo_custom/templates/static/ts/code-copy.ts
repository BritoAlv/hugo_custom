(function () {
  document.querySelectorAll<HTMLElement>("pre > code").forEach(function (code) {
    const pre = code.parentElement;
    if (!pre) return;
    if (pre.querySelector(".code-copy-btn")) return;

    // Anchor the button to a wrapper instead of the scrolling <pre>, so
    // horizontal code scroll leaves the button fixed in place.
    let wrap: HTMLElement;
    const parent = pre.parentElement;
    if (parent && parent.classList.contains("code-wrap")) {
      if (parent.querySelector(".code-copy-btn")) return;
      wrap = parent;
    } else {
      wrap = document.createElement("div");
      wrap.className = "code-wrap";
      pre.replaceWith(wrap);
      wrap.appendChild(pre);
    }

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
    wrap.appendChild(btn);
  });
})();