(function () {
  const params = new URLSearchParams(window.location.search);
  const override = params.get("ad_mode");
  const AD_MODE = (override === "adsense" || override === "coupang") ? override : "coupang";
  window.GH_TOON_AD_MODE = AD_MODE;

  const ADSENSE_PUB = "ca-pub-8830524482034754";

  function renderAdSenseSlot(container, layout) {
    const isArticle = layout === "in-article";
    container.innerHTML =
      '<div style="font-size:11px;color:#595959;margin-bottom:6px;">Advertisement</div>' +
      '<ins class="adsbygoogle" style="display:block;min-height:90px;text-align:center;" ' +
      'data-ad-client="' + ADSENSE_PUB + '" data-ad-slot="auto" ' +
      (isArticle ? 'data-ad-layout="in-article" data-ad-format="fluid" ' : 'data-ad-format="auto" data-full-width-responsive="true" ') +
      '></ins>';
    try { if (window.adsbygoogle) window.adsbygoogle.push({}); } catch (e) {}
  }

  function renderCoupangSlot(el) {
    const widgetId = String(el.getAttribute("data-widget-id") || "1044909").replace(/[^0-9]/g, "") || "1044909";
    el.innerHTML =
      '<div class="cp-dyn-desktop"><iframe src="https://ads-partners.coupang.com/widgets.html?id=' + widgetId + '&template=carousel&trackingCode=AF2560572&subId=ghshopping&width=680&height=140&tsource=" width="680" height="140" frameborder="0" scrolling="no" referrerpolicy="unsafe-url" title="쿠팡 파트너스 다이나믹 배너"></iframe></div>' +
      '<div class="cp-dyn-mobile"><iframe src="https://ads-partners.coupang.com/widgets.html?id=1050469&template=carousel&trackingCode=AF2560572&subId=ghshopping&width=320&height=320&tsource=" width="320" height="320" frameborder="0" scrolling="no" referrerpolicy="unsafe-url" title="쿠팡 파트너스 모바일 다이나믹 배너"></iframe></div>';
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
        if (!el.querySelector("iframe, a[href*='link.coupang.com']")) {
          renderCoupangSlot(el);
        }
      });
    }
  });
})();
