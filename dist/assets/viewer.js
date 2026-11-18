(function () {
  // Genre Filter on Home / Studio
  const tabs = document.querySelectorAll(".nv-tab-btn");
  const cards = document.querySelectorAll("[data-genre-item]");
  tabs.forEach(function (btn) {
    btn.addEventListener("click", function () {
      const target = btn.getAttribute("data-genre") || "all";
      tabs.forEach(function (t) { t.classList.remove("is-active"); });
      btn.classList.add("is-active");
      cards.forEach(function (card) {
        const g = card.getAttribute("data-genre-item") || "";
        card.style.display = (target === "all" || target === g) ? "" : "none";
      });
    });
  });

  // Reading Progress + Cut Counter on Episode Page
  const fill = document.getElementById("read-progress-fill");
  const cutLabel = document.getElementById("cut-float-counter");
  const cuts = Array.from(document.querySelectorAll(".comic-cut"));
  if (fill || cutLabel) {
    window.addEventListener("scroll", function () {
      const docH = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      const pct = Math.min(100, Math.max(0, Math.round((window.scrollY / docH) * 100)));
      if (fill) fill.style.width = pct + "%";
      if (cutLabel && cuts.length) {
        const mid = window.scrollY + window.innerHeight * 0.4;
        let current = 1;
        cuts.forEach(function (c, i) {
          if (c.offsetTop <= mid) current = i + 1;
        });
        cutLabel.textContent = current + " / " + cuts.length + "컷";
      }
    }, { passive: true });
  }

  // Light / Dark Mode Toggle
  const modeBtn = document.getElementById("toggle-theme-btn");
  if (modeBtn) {
    modeBtn.addEventListener("click", function () {
      document.body.classList.toggle("light-mode");
      modeBtn.textContent = document.body.classList.contains("light-mode") ? "🌙 다크" : "☀️ 라이트";
    });
  }

  // Star Rating Feedback
  const rateMsg = document.getElementById("star-msg");
  document.querySelectorAll(".star-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      const val = btn.getAttribute("data-star") || "5";
      if (rateMsg) rateMsg.textContent = "별점 " + val + "점 참여가 반영되었습니다! 감사합니다.";
    });
  });

  // Interactive Reader Comment Append
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
      item.innerHTML = '<div style="font-size:13px;font-weight:800;margin-bottom:4px;"><span class="best-pill" style="background:#00dc64;color:#052e16;">NEW</span>방금 남긴 댓글</div><div style="font-size:14px;"></div>';
      item.querySelector("div:last-child").textContent = txt;
      cList.prepend(item);
      cInput.value = "";
    });
  }
})();
