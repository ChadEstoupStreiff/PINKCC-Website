document.addEventListener("DOMContentLoaded", () => {
  const tabs = document.querySelectorAll(".works-tab");
  const panels = document.querySelectorAll(".works-panel");

  if (!tabs.length) return;

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const targetId = tab.dataset.target;

      // update tabs
      tabs.forEach((t) => {
        t.classList.toggle("active", t === tab);
        t.setAttribute("aria-selected", t === tab ? "true" : "false");
      });

      // update panels
      panels.forEach((panel) => {
        panel.classList.toggle("active", panel.id === targetId);
      });
    });
  });
});