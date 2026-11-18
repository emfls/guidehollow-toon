(function () {
  const tabs = document.querySelectorAll(".nv-sub-btn");
  const cards = document.querySelectorAll("[data-genre-item]");
  const searchInput = document.getElementById("wt-search-input");

  function applyFilter() {
    const activeBtn = document.querySelector(".nv-sub-btn.is-active");
    const target = activeBtn ? activeBtn.getAttribute("data-genre") : "all";
    const q = searchInput ? searchInput.value.trim().toLowerCase() : "";
    cards.forEach(function (card) {
      const g = card.getAttribute("data-genre-item") || "";
      const txt = (card.textContent || "").toLowerCase();
      const matchGenre = (target === "all" || target === g);
      const matchSearch = (!q || txt.includes(q));
      card.style.display = (matchGenre && matchSearch) ? "" : "none";
    });
    const newGrid = document.querySelector(".new-grid");
    const newHead = document.getElementById("new-sec-head");
    if (newGrid && newHead) {
      const visNew = Array.from(newGrid.querySelectorAll("[data-genre-item]")).filter(el => el.style.display !== "none").length;
      newGrid.style.display = visNew ? "" : "none";
      newHead.style.display = visNew ? "" : "none";
    }
    const wtGrid = document.querySelector(".wt-grid");
    const emptyMsg = document.getElementById("wt-empty-msg");
    if (wtGrid && emptyMsg) {
      const visWt = Array.from(wtGrid.querySelectorAll("[data-genre-item]")).filter(el => el.style.display !== "none").length;
      emptyMsg.style.display = visWt ? "none" : "block";
    }
  }

  tabs.forEach(function (btn) {
    btn.addEventListener("click", function () {
      tabs.forEach(function (t) { t.classList.remove("is-active"); });
      btn.classList.add("is-active");
      applyFilter();
    });
  });
  if (searchInput) {
    searchInput.addEventListener("input", applyFilter);
  }

  const fill = document.getElementById("read-progress-fill");
  const canvasEl = document.querySelector(".comic-canvas");
  if (fill) {
    window.addEventListener("scroll", function () {
      if (canvasEl) {
        const rect = canvasEl.getBoundingClientRect();
        const total = Math.max(1, canvasEl.offsetHeight - window.innerHeight);
        const passed = Math.max(0, -rect.top);
        fill.style.width = Math.min(100, Math.round((passed / total) * 100)) + "%";
      } else {
        const docH = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
        fill.style.width = Math.min(100, Math.max(0, Math.round((window.scrollY / docH) * 100))) + "%";
      }
    }, { passive: true });
  }
})();
