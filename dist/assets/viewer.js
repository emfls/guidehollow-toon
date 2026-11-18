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
  if (fill) {
    window.addEventListener("scroll", function () {
      const docH = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      fill.style.width = Math.min(100, Math.max(0, Math.round((window.scrollY / docH) * 100))) + "%";
    }, { passive: true });
  }

  const rateMsg = document.getElementById("star-msg");
  document.querySelectorAll(".star-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const val = btn.getAttribute("data-star") || "10";
      if (rateMsg) rateMsg.textContent = "별점 " + val + "점 참여가 반영되었습니다!";
    });
  });

  const cForm = document.getElementById("reader-comment-form");
  const cInput = document.getElementById("reader-comment-input");
  const cList = document.getElementById("comment-list");
  if (cForm && cInput && cList) {
    cForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const txt = cInput.value.trim();
      if (!txt) return;
      const item = document.createElement("div");
      item.className = "comment-item";
      item.innerHTML = '<div style="font-size:13px;font-weight:800;margin-bottom:4px;"><span class="best-pill" style="color:#059669;border-color:#059669;">NEW</span>방금 남긴 댓글</div><div style="font-size:14px;"></div>';
      item.querySelector("div:last-child").textContent = txt;
      cList.prepend(item);
      cInput.value = "";
    });
  }
})();
