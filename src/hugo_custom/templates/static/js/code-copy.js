(function () {
  document.querySelectorAll("pre > code").forEach(function (code) {
    var pre = code.parentNode;
    if (pre.querySelector(".code-copy-btn")) return;
    var btn = document.createElement("button");
    btn.className = "code-copy-btn";
    btn.type = "button";
    btn.textContent = "Copy";
    btn.addEventListener("click", function () {
      navigator.clipboard.writeText(code.innerText).then(function () {
        btn.textContent = "Copied";
        setTimeout(function () { btn.textContent = "Copy"; }, 1500);
      });
    });
    pre.appendChild(btn);
  });
})();