(function () {
  const openers = document.querySelectorAll(".open-modal");
  const close = (m) => {
    m.classList.remove("open");
    document.body.classList.remove("modal-open");
  };
  openers.forEach((btn) => {
    btn.addEventListener("click", () => {
      const sel = btn.dataset.target;
      const m = document.querySelector(sel);
      if (!m) return;
      m.classList.add("open");
      document.body.classList.add("modal-open");
      m.querySelector(".modal-close").focus();
      // close handlers
      m.querySelector(".modal-close").onclick = () => close(m);
      m.onclick = (e) => {
        if (e.target === m) close(m);
      };
      window.addEventListener("keydown", function esc(e) {
        if (e.key === "Escape") {
          close(m);
          window.removeEventListener("keydown", esc);
        }
      });
    });
  });
})();
