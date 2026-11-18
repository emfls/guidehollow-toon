// Dual-Mode Ad Manager for GuideHollow 웹툰 (toon.guidehollow.com)
// Switch permanently via `python3 tools/build.py --ad-mode adsense` after AdSense approval,
// or preview live by appending `?ad_mode=adsense` to any URL.
(function () {
  const params = new URLSearchParams(window.location.search);
  const override = params.get("ad_mode");
  const AD_MODE = (override === "adsense" || override === "coupang") ? override : "coupang";
  window.GH_TOON_AD_MODE = AD_MODE;

  const COUPANG_FTC = "이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.";
  const ADSENSE_PUB = "ca-pub-8830524482034754";

  const CAROUSELS = {
    digital: { id: 1050468, label: "가전·디지털 인기 베스트" },
    living: { id: 1050469, label: "생활·수납 인기 베스트" },
    kitchen: { id: 1050470, label: "주방·새출발 인기 베스트" }
  };

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
    try {
      if (window.adsbygoogle) window.adsbygoogle.push({});
    } catch (e) {}
  }

  function ensureAdSenseScript() {
    if (document.querySelector('script[src*="adsbygoogle.js"]')) return;
    const s = document.createElement("script");
    s.async = true;
    s.src = "https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=" + ADSENSE_PUB;
    s.crossOrigin = "anonymous";
    document.head.appendChild(s);
  }

  function renderCoupangSlot(container) {
    const kind = container.dataset.adKind || "search";
    if (kind === "search") {
      container.innerHTML =
        '<p class="ad-disclosure">' + COUPANG_FTC + '</p>' +
        '<div class="coupang-search-wrap">' +
        '<iframe src="https://coupa.ng/cqZC1w" width="100%" height="75" frameborder="0" scrolling="no" referrerpolicy="unsafe-url" title="쿠팡 파트너스 상품 검색 위젯"></iframe>' +
        '</div>';
      return;
    }
    if (kind === "carousels") {
      container.innerHTML =
        '<p class="ad-disclosure">' + COUPANG_FTC + ' (고단가·생활 실속 비교 배너)</p>' +
        '<div class="carousel-grid">' +
        Object.values(CAROUSELS).map(function (c) {
          return '<div class="coupang-carousel-slot">' +
            '<iframe src="https://ads-partners.coupang.com/widgets.html?id=' + c.id + '&template=carousel&trackingCode=AF2560572&subId=ghshopping&width=320&height=320&tsource=" width="320" height="320" frameborder="0" scrolling="no" referrerpolicy="unsafe-url" loading="lazy" title="' + esc(c.label) + '"></iframe>' +
            '</div>';
        }).join("") +
        '</div>';
      return;
    }
    if (kind === "contextual") {
      const badge = container.dataset.badge || "생활 실속 추천 배너";
      const title = container.dataset.title || "쿠팡 파트너스 인기 추천 상품 보기";
      const reason = container.dataset.reason || "웹툰 주제와 관련된 실용 상품을 바로 비교해 보세요.";
      const url = container.dataset.url || "https://link.coupang.com/a/iG9mTjBUg8";
      const cta = container.dataset.cta || "쿠팡에서 가격 확인하기";
      const guideUrl = container.dataset.guideUrl || "https://shopping.guidehollow.com/";
      const guideLabel = container.dataset.guideLabel || "GuideHollow 구매 기준 보기";
      const wid = container.dataset.widgetId || "1050469";
      container.innerHTML =
        '<p class="ad-disclosure">' + COUPANG_FTC + '</p>' +
        '<div class="coupang-banner-card">' +
          '<div style="flex:1 1 280px;">' +
            '<small style="font-weight:800;color:#b45309;">' + esc(badge) + '</small>' +
            '<strong>' + esc(title) + '</strong>' +
            '<span>' + esc(reason) + '</span>' +
            '<div class="coupang-card-actions" style="margin-top:0.7rem;">' +
              '<a class="btn btn-coupang" href="' + esc(url) + '" target="_blank" rel="noopener noreferrer sponsored">' + esc(cta) + ' →</a>' +
              '<a class="btn" href="' + esc(guideUrl) + '" target="_blank" rel="noopener noreferrer">' + esc(guideLabel) + '</a>' +
            '</div>' +
          '</div>' +
          '<div class="coupang-carousel-slot" style="flex:0 0 320px;max-width:100%;">' +
            '<iframe src="https://ads-partners.coupang.com/widgets.html?id=' + esc(wid) + '&template=carousel&trackingCode=AF2560572&subId=ghshopping&width=320&height=320&tsource=" width="320" height="320" frameborder="0" scrolling="no" referrerpolicy="unsafe-url" loading="lazy" title="쿠팡 추천 캐러셀 배너"></iframe>' +
          '</div>' +
        '</div>';
    }
  }

  function mountAllAds() {
    const slots = document.querySelectorAll("[data-gh-ad-slot]");
    if (!slots.length) return;
    if (AD_MODE === "adsense") {
      ensureAdSenseScript();
      slots.forEach(function (el) {
        renderAdSenseSlot(el, el.dataset.adLayout || "auto");
      });
    } else {
      slots.forEach(renderCoupangSlot);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountAllAds);
  } else {
    mountAllAds();
  }
})();
