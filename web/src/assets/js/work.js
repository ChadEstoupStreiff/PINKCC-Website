document.addEventListener("DOMContentLoaded", () => {
  const tabs = document.querySelectorAll(".works-tab");
  const panels = document.querySelectorAll(".works-panel");

  if (!tabs.length) return;

  // pick a random tab
  const randomIndex = Math.floor(Math.random() * tabs.length);
  const randomTab = tabs[randomIndex];
  const targetId = randomTab.dataset.target;

  // activate it
  tabs.forEach((t, i) => {
    const isActive = i === randomIndex;
    t.classList.toggle("active", isActive);
    t.setAttribute("aria-selected", isActive ? "true" : "false");
  });

  panels.forEach((panel) => {
    panel.classList.toggle("active", panel.id === targetId);
  });

  // normal click handling
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const targetId = tab.dataset.target;

      tabs.forEach((t) => {
        t.classList.toggle("active", t === tab);
        t.setAttribute("aria-selected", t === tab ? "true" : "false");
      });

      panels.forEach((panel) => {
        panel.classList.toggle("active", panel.id === targetId);
      });
    });
  });
});