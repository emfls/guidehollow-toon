(function () {
  function initViewer() {
    var stage = document.getElementById("webtoonStage");
    var toggle = document.getElementById("themeToggleBtn");
    if (stage && toggle) {
      toggle.addEventListener("click", function () {
        var isLight = stage.classList.toggle("is-light");
        toggle.textContent = isLight ? "🌙 다크 뷰어" : "☀️ 라이트 뷰어";
      });
    }
    var rateBtn = document.getElementById("rateUpBtn");
    var starScore = document.getElementById("starScoreVal");
    if (rateBtn && starScore) {
      rateBtn.addEventListener("click", function () {
        if (rateBtn.dataset.voted === "1") return;
        rateBtn.dataset.voted = "1";
        starScore.textContent = "9.98 (별점 참여 완료!)";
        rateBtn.textContent = "⭐ 별점 반영됨";
      });
    }
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initViewer);
  } else {
    initViewer();
  }
})();
