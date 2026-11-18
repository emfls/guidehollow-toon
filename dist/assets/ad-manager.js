(function () {
  const params = new URLSearchParams(window.location.search);
  const override = params.get("ad_mode");
  const AD_MODE = (override === "adsense" || override === "coupang") ? override : "coupang";
  window.GH_TOON_AD_MODE = AD_MODE;

  const COUPANG_FTC = "이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.";
  const ADSENSE_PUB = "ca-pub-8830524482034754";

  function esc(v) {
    return String(v || "").replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" }[c];
    });
  }

  function renderAdSenseSlot(container, layout) {
    const isArticle = layout === "in-article";
    container.innerHTML =
      '<div class="ad-disclosure">Advertisement</div>' +
      '<ins class="adsbygoogle" style="display:block;min-height:90px;text-align:center;" ' +
      'data-ad-client="' + ADSENSE_PUB + '" data-ad-slot="auto" ' +
      (isArticle ? 'data-ad-layout="in-article" data-ad-format="fluid" ' : 'data-ad-format="auto" data-full-width-responsive="true" ') +
      '></ins>';
    try { if (window.adsbygoogle) window.adsbygoogle.push({}); } catch (e) {}
  }

  function renderCoupangSlot(el) {
    const title = el.getAttribute("data-title") || "";
    const reason = el.getAttribute("data-reason") || "";
    const cta = el.getAttribute("data-cta") || "쿠팡 상품 보기";
    const url = el.getAttribute("data-url") || "https://shopping.guidehollow.com/";
    const badge = el.getAttribute("data-badge") || "상황 맞춤 추천";
    const guideUrl = el.getAttribute("data-guide-url") || "https://shopping.guidehollow.com/";
    const guideLabel = el.getAttribute("data-guide-label") || "구매 가이드";
    const variant = el.getAttribute("data-gh-slot-variant") || "banner";
    if (variant === "wing") {
      el.innerHTML =
        '<div class="ad-disclosure">' + esc(COUPANG_FTC) + '</div>' +
        '<div class="wing-badge">' + esc(badge) + '</div>' +
        '<div class="wing-title">' + esc(title) + '</div>' +
        '<div class="wing-reason">' + esc(reason) + '</div>' +
        '<a class="wing-cta" href="' + esc(url) + '" target="_blank" rel="noopener noreferrer sponsored">' + esc(cta) + ' ↗</a>' +
        '<a class="wing-guide" href="' + esc(guideUrl) + '" target="_blank" rel="noopener noreferrer">' + esc(guideLabel) + ' →</a>';
      return;
    }
    el.innerHTML =
      '<div class="ad-disclosure">' + esc(COUPANG_FTC) + '</div>' +
      '<div class="coupang-banner">' +
      '  <div style="font-size:12px;font-weight:800;color:#059669;">' + esc(badge) + '</div>' +
      '  <div style="font-size:16px;font-weight:800;color:#111111;">' + esc(title) + '</div>' +
      '  <div style="font-size:13.5px;color:#555555;">' + esc(reason) + '</div>' +
      '  <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:4px;">' +
      '    <a class="coupang-cta" href="' + esc(url) + '" target="_blank" rel="noopener noreferrer sponsored">' + esc(cta) + ' ↗</a>' +
      '    <a style="display:inline-flex;align-items:center;font-size:13px;font-weight:700;color:#2563eb;" href="' + esc(guideUrl) + '" target="_blank" rel="noopener noreferrer">' + esc(guideLabel) + ' →</a>' +
      '  </div>' +
      '</div>';
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (AD_MODE === "adsense") {
      if (!document.querySelector('script[src*="adsbygoogle.js"]')) {
        const s = document.createElement("script");
        s.async = true;
        s.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + ADSENSE_PUB;
        s.crossOrigin = "anonymous";
        document.head.appendChild(s);
      }
      document.querySelectorAll("[data-gh-ad-slot]").forEach(function (el) {
        renderAdSenseSlot(el, el.getAttribute("data-ad-layout") || "auto");
      });
    } else {
      document.querySelectorAll("[data-gh-ad-slot]").forEach(function (el) {
        if (!el.querySelector(".coupang-banner, .wing-cta")) {
          renderCoupangSlot(el);
        }
      });
    }
  });
})();
