(function () {
  const SCENE_PALETTES = {
    "오피스": { bgTop: "#e2e8f0", bgBot: "#cbd5e1", accent: "#0f766e", shirt: "#1e3a8a", hair: "#1e293b", skin: "#fde6d8" },
    "톡방·메신저": { bgTop: "#fef08a", bgBot: "#fde047", accent: "#0369a1", shirt: "#0f766e", hair: "#0f172a", skin: "#fee5d6" },
    "주차장·도로": { bgTop: "#1e293b", bgBot: "#334155", accent: "#f59e0b", shirt: "#475569", hair: "#0f172a", skin: "#fbd9c7" },
    "예식장·카페": { bgTop: "#fce7f3", bgBot: "#fbcfe8", accent: "#be185d", shirt: "#9d174d", hair: "#312e81", skin: "#fdece2" },
    "미스터리야간": { bgTop: "#0f172a", bgBot: "#1e1b4b", accent: "#c084fc", shirt: "#312e81", hair: "#020617", skin: "#e2e8f0" },
    "법원·계약서": { bgTop: "#ecfeff", bgBot: "#cffafe", accent: "#0e7490", shirt: "#111827", hair: "#1f2937", skin: "#fde5d7" }
  };

  let episodes = [];
  const state = {
    activeIdx: 0,
    aspect: "grid4",
    shortsIdx: 0,
    title: "퇴근 5분 전 주말 출근 강요한 팀장님, 노동청 진정서 한 장에 태세 전환한 썰",
    watermark: "toon.guidehollow.com",
    showAiLabel: true,
    hashtags: ["#썰툰", "#사이다썰", "#GuideHollow썰툰"],
    panels: []
  };

  const els = {};
  function q(id) { return document.getElementById(id); }
  function toast(msg) { if (els.toast) els.toast.textContent = msg; }
  function esc(v) {
    return String(v || "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }

  function wrapLines(ctx, text, maxW, maxLines) {
    const words = String(text || "").split(/\s+/);
    const lines = [];
    let cur = "";
    for (const w of words) {
      const cand = cur ? cur + " " + w : w;
      if (ctx.measureText(cand).width <= maxW) {
        cur = cand;
      } else {
        if (cur) lines.push(cur);
        if (ctx.measureText(w).width > maxW) {
          let chunk = "";
          for (const ch of w) {
            if (ctx.measureText(chunk + ch).width > maxW && chunk) {
              lines.push(chunk);
              chunk = ch;
            } else {
              chunk += ch;
            }
          }
          cur = chunk;
        } else {
          cur = w;
        }
      }
    }
    if (cur) lines.push(cur);
    if (maxLines && lines.length > maxLines) {
      const cut = lines.slice(0, maxLines);
      cut[maxLines - 1] = cut[maxLines - 1].slice(0, Math.max(2, cut[maxLines - 1].length - 1)) + "…";
      return cut;
    }
    return lines;
  }

  function rrect(ctx, x, y, w, h, r) {
    const rad = Math.min(r, w / 2, h / 2);
    ctx.beginPath();
    ctx.moveTo(x + rad, y);
    ctx.arcTo(x + w, y, x + w, y + h, rad);
    ctx.arcTo(x + w, y + h, x, y + h, rad);
    ctx.arcTo(x, y + h, x, y, rad);
    ctx.arcTo(x, y, x + w, y, rad);
    ctx.closePath();
  }

  function drawChar(ctx, cx, cy, scale, expr, pal) {
    ctx.save();
    ctx.translate(cx, cy);
    ctx.scale(scale, scale);
    ctx.fillStyle = pal.shirt;
    rrect(ctx, -46, 28, 92, 62, 24);
    ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = "#0f172a"; ctx.stroke();
    ctx.fillStyle = pal.skin; ctx.fillRect(-10, 14, 20, 18);
    ctx.fillStyle = pal.hair; ctx.beginPath(); ctx.arc(0, -14, 34, Math.PI * 0.9, Math.PI * 2.1); ctx.fill();
    ctx.fillStyle = pal.skin; ctx.beginPath(); ctx.ellipse(0, -8, 29, 32, 0, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
    ctx.fillStyle = pal.hair;
    ctx.beginPath();
    ctx.moveTo(-30, -16); ctx.quadraticCurveTo(-10, -44, 0, -40); ctx.quadraticCurveTo(18, -44, 30, -16);
    ctx.quadraticCurveTo(14, -28, 0, -20); ctx.quadraticCurveTo(-14, -28, -30, -16); ctx.fill();
    ctx.strokeStyle = "#0f172a"; ctx.fillStyle = "#0f172a"; ctx.lineWidth = 2.8;
    if (expr === "사이다미소") {
      ctx.beginPath(); ctx.arc(-11, -9, 5, Math.PI, 0); ctx.stroke();
      ctx.beginPath(); ctx.arc(11, -9, 5, Math.PI, 0); ctx.stroke();
      ctx.beginPath(); ctx.arc(0, 3, 9, 0.1 * Math.PI, 0.9 * Math.PI); ctx.stroke();
    } else if (expr === "분노") {
      ctx.beginPath(); ctx.moveTo(-18, -20); ctx.lineTo(-5, -14); ctx.moveTo(18, -20); ctx.lineTo(5, -14); ctx.stroke();
      ctx.beginPath(); ctx.arc(-11, -10, 3.2, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(11, -10, 3.2, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.ellipse(0, 8, 9, 6, 0, 0, Math.PI * 2); ctx.stroke();
    } else if (expr === "각성") {
      ctx.fillStyle = "#fff"; ctx.fillRect(-19, -15, 15, 9); ctx.fillRect(4, -15, 15, 9);
      ctx.strokeRect(-19, -15, 15, 9); ctx.strokeRect(4, -15, 15, 9);
      ctx.beginPath(); ctx.moveTo(-7, 7); ctx.quadraticCurveTo(3, 12, 11, 4); ctx.stroke();
    } else {
      ctx.beginPath(); ctx.arc(-11, -10, 3.2, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(11, -10, 3.2, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.moveTo(-8, 7); ctx.lineTo(8, 7); ctx.stroke();
    }
    ctx.restore();
  }

  function drawPanel(ctx, x, y, w, h, p, sc) {
    const pal = SCENE_PALETTES[p.scene] || SCENE_PALETTES["오피스"];
    ctx.save();
    rrect(ctx, x, y, w, h, 14);
    const g = ctx.createLinearGradient(x, y, x, y + h);
    g.addColorStop(0, pal.bgTop); g.addColorStop(1, pal.bgBot);
    ctx.fillStyle = g; ctx.fill();
    ctx.lineWidth = 4; ctx.strokeStyle = "#0f172a"; ctx.stroke(); ctx.clip();

    const narH = Math.round(52 * sc);
    ctx.fillStyle = "#0f172a"; ctx.fillRect(x, y, w, narH);
    ctx.fillStyle = "#64d8d0"; ctx.font = "800 " + Math.round(13 * sc) + 'px "Noto Sans KR",sans-serif';
    ctx.textBaseline = "middle";
    ctx.fillText("#" + p.panelNumber + " " + (p.stage || ""), x + 12 * sc, y + 17 * sc);
    ctx.fillStyle = "#fff"; ctx.font = "700 " + Math.round(13.5 * sc) + 'px "Noto Sans KR",sans-serif';
    const nLines = wrapLines(ctx, p.narration, w - 24 * sc, 1);
    ctx.fillText(nLines[0] || "", x + 12 * sc, y + 38 * sc);

    if (p.sfx) {
      ctx.save(); ctx.translate(x + w - 48 * sc, y + narH + 28 * sc); ctx.rotate(-0.1);
      ctx.fillStyle = "#fef08a"; ctx.strokeStyle = "#b45309"; ctx.lineWidth = 2.4;
      rrect(ctx, -38 * sc, -14 * sc, 76 * sc, 28 * sc, 7); ctx.fill(); ctx.stroke();
      ctx.fillStyle = "#b91c1c"; ctx.font = "900 " + Math.round(14 * sc) + 'px "Noto Sans KR",sans-serif';
      ctx.textAlign = "center"; ctx.fillText(p.sfx, 0, 1); ctx.restore();
    }

    drawChar(ctx, x + w * 0.24, y + h * 0.72, sc * 0.96, p.expression, pal);
    const bx = x + w * 0.37, bw = w * 0.59, by = y + narH + 38 * sc, bh = h - (by - y) - 18 * sc;
    ctx.fillStyle = p.bubbleType === "외침(사이다)" ? "#fffbeb" : "#fff";
    ctx.strokeStyle = p.bubbleType === "외침(사이다)" ? "#b91c1c" : "#0f172a";
    ctx.lineWidth = 3; rrect(ctx, bx, by, bw, bh, 16); ctx.fill(); ctx.stroke();

    ctx.fillStyle = pal.accent; ctx.font = "800 " + Math.round(13 * sc) + 'px "Noto Sans KR",sans-serif';
    ctx.textBaseline = "top"; ctx.fillText(p.speaker || "화자", bx + 14 * sc, by + 11 * sc);
    ctx.fillStyle = "#0f172a"; ctx.font = "700 " + Math.round(16 * sc) + 'px "Noto Sans KR",sans-serif';
    wrapLines(ctx, p.dialogue, bw - 26 * sc, 5).forEach((ln, idx) => {
      ctx.fillText(ln, bx + 14 * sc, by + (33 + idx * 23) * sc);
    });
    ctx.restore();
  }

  function renderCanvas() {
    if (!els.canvas || !state.panels.length) return;
    const ctx = els.canvas.getContext("2d");
    const panels = state.panels;
    if (state.aspect === "grid4") {
      els.canvas.width = 1080; els.canvas.height = 1080;
      els.pager.classList.remove("is-visible");
      ctx.fillStyle = "#f8fafc"; ctx.fillRect(0, 0, 1080, 1080);
      ctx.fillStyle = "#0f172a"; ctx.fillRect(0, 0, 1080, 118);
      ctx.fillStyle = "#64d8d0"; ctx.font = '800 20px "Noto Sans KR",sans-serif'; ctx.textBaseline = "top";
      ctx.fillText("GuideHollow 4컷 썰툰 · " + state.watermark, 34, 18);
      ctx.fillStyle = "#fff"; ctx.font = '800 28px "Noto Sans KR",sans-serif';
      wrapLines(ctx, state.title, 1010, 2).forEach((ln, i) => ctx.fillText(ln, 34, 48 + i * 32));
      const idx4 = panels.length >= 6 ? [0, 1, 3, 5] : [0, 1, 2, 3];
      const pos = [[28, 136], [550, 136], [28, 586], [550, 586]];
      idx4.forEach((pIdx, s) => { if (panels[pIdx]) drawPanel(ctx, pos[s][0], pos[s][1], 502, 430, panels[pIdx], 1.12); });
      if (state.showAiLabel) {
        ctx.fillStyle = "#334155"; ctx.font = '600 17px "Noto Sans KR",sans-serif';
        ctx.fillText("AI 연출·브라우저 제작(toon.guidehollow.com)", 28, 1040);
      }
    } else if (state.aspect === "webtoon6") {
      els.canvas.width = 800; els.canvas.height = 2400;
      els.pager.classList.remove("is-visible");
      ctx.fillStyle = "#f8fafc"; ctx.fillRect(0, 0, 800, 2400);
      ctx.fillStyle = "#0f172a"; ctx.fillRect(0, 0, 800, 150);
      ctx.fillStyle = "#64d8d0"; ctx.font = '800 20px "Noto Sans KR",sans-serif'; ctx.textBaseline = "top";
      ctx.fillText("6컷 세로 웹툰 · " + state.watermark, 28, 20);
      ctx.fillStyle = "#fff"; ctx.font = '800 28px "Noto Sans KR",sans-serif';
      wrapLines(ctx, state.title, 744, 2).forEach((ln, i) => ctx.fillText(ln, 28, 54 + i * 36));
      panels.slice(0, 6).forEach((p, idx) => drawPanel(ctx, 28, 174 + idx * 360, 744, 340, p, 1.05));
      if (state.showAiLabel) {
        ctx.fillStyle = "#334155"; ctx.font = '600 18px "Noto Sans KR",sans-serif';
        ctx.fillText("AI 연출·브라우저 제작(toon.guidehollow.com)", 28, 2354);
      }
    } else {
      els.canvas.width = 1080; els.canvas.height = 1920;
      els.pager.classList.add("is-visible");
      const s = Math.max(0, Math.min(state.shortsIdx, panels.length - 1));
      els.counter.textContent = (s + 1) + " / " + panels.length + " 컷";
      ctx.fillStyle = "#0f172a"; ctx.fillRect(0, 0, 1080, 1920);
      ctx.fillStyle = "#facc15"; rrect(ctx, 48, 120, 984, 210, 24); ctx.fill();
      ctx.fillStyle = "#0f172a"; ctx.font = '900 38px "Noto Sans KR",sans-serif'; ctx.textBaseline = "top";
      wrapLines(ctx, state.title, 920, 3).forEach((ln, i) => ctx.fillText(ln, 80, 150 + i * 54));
      drawPanel(ctx, 48, 370, 984, 1180, panels[s], 1.9);
      ctx.fillStyle = "#64d8d0"; ctx.font = '800 30px "Noto Sans KR",sans-serif';
      ctx.fillText(state.watermark + " · " + (s + 1) + "/" + panels.length + "컷", 60, 1610);
      if (state.showAiLabel) {
        ctx.fillStyle = "#cbd5e1"; ctx.font = '600 24px "Noto Sans KR",sans-serif';
        ctx.fillText("AI 연출·브라우저 제작(toon.guidehollow.com)", 60, 1665);
      }
    }
  }

  function syncInputs() {
    const p = state.panels[state.activeIdx] || state.panels[0];
    if (!p) return;
    els.epTitle.value = state.title;
    els.watermark.value = state.watermark;
    els.aiCheck.checked = state.showAiLabel;
    els.pStage.value = p.stage || "";
    els.pSpeaker.value = p.speaker || "";
    els.pScene.value = p.scene || "오피스";
    els.pExpr.value = p.expression || "사이다미소";
    els.pBubble.value = p.bubbleType || "일반";
    els.pSfx.value = p.sfx || "두둥!";
    els.pNarr.value = p.narration || "";
    els.pDial.value = p.dialogue || "";
    els.ptabs.innerHTML = state.panels.map((item, idx) =>
      '<button type="button" class="ptab ' + (idx === state.activeIdx ? 'is-active' : '') + '" data-idx="' + idx + '">' + (idx + 1) + '컷</button>'
    ).join("");
    els.ptabs.querySelectorAll(".ptab").forEach((b) => {
      b.addEventListener("click", () => {
        state.activeIdx = Number(b.dataset.idx);
        state.shortsIdx = state.activeIdx;
        syncInputs();
        renderCanvas();
      });
    });
  }

  function loadEp(ep) {
    state.title = ep.title;
    state.panels = JSON.parse(JSON.stringify(ep.panels));
    state.hashtags = ep.hashtags ? [...ep.hashtags] : ["#썰툰", "#GuideHollow"];
    state.activeIdx = 0;
    state.shortsIdx = 0;
    document.querySelectorAll(".preset-btn").forEach((b) => b.classList.toggle("is-selected", b.dataset.ep === ep.id));
    syncInputs();
    renderCanvas();
  }

  function buildFromIdea(ideaRaw) {
    const idea = (ideaRaw || "").trim();
    if (!idea) { toast("한 줄 사연을 먼저 입력해 주세요!"); return; }
    const sIdea = idea.length > 42 ? idea.slice(0, 42) + "…" : idea;
    state.title = sIdea + " — 증거 하나로 통쾌하게 역전한 썰";
    state.panels = [
      { panelNumber: 1, stage: "기(3초 훅)", scene: "오피스", expression: "사이다미소", bubbleType: "외침(사이다)", sfx: "두둥!", speaker: "주인공(나)", narration: "3초 훅 · " + sIdea, dialogue: "마지막 증거 한 장에 상대 태도가 180도 바뀌었습니다." },
      { panelNumber: 2, stage: "승(고구마)", scene: "톡방·메신저", expression: "억울", bubbleType: "일반", sfx: "실화냐?!", speaker: "상대방", narration: "발단 · 처음엔 웃어넘기려던 선 넘은 행동.", dialogue: "증거도 없으면서 괜히 예민하게 구시네 ㅋㅋ" },
      { panelNumber: 3, stage: "승(고구마 심화)", scene: "오피스", expression: "분노", bubbleType: "속마음", sfx: "삐빅-", speaker: "주인공(나)", narration: "감정 싸움 대신 기록을 남기기로 결심한 순간.", dialogue: "'말로 해선 안 통한다. 시간대별 영수증과 대화 원본을 다 모은다.'" },
      { panelNumber: 4, stage: "전(결정적 증거)", scene: "법원·계약서", expression: "각성", bubbleType: "나레이션박스", sfx: "두둥!", speaker: "증거 정리", narration: "반전의 시작 · CCTV·원본 영수증·접수번호 완비.", dialogue: "날짜, 시간, 금액 오차 없이 공식 자료 정리 완료!" },
      { panelNumber: 5, stage: "전(반격)", scene: "오피스", expression: "당황", bubbleType: "외침(사이다)", sfx: "참교육!", speaker: "상대방", narration: "공식 증거를 보여주자 순식간에 바뀐 목소리.", dialogue: "어?! 그걸 다 저장해 뒀어요?? 좋게 해결해요 제발!!" },
      { panelNumber: 6, stage: "결(사이다)", scene: "오피스", expression: "사이다미소", bubbleType: "외침(사이다)", sfx: "사이다!", speaker: "주인공(나)", narration: "완벽한 마무리 · 손해 0원 & 깔끔한 정산 완료.", dialogue: "억울할 땐 화내기보다 '기록 남기기'가 제일 강합니다!" }
    ];
    state.activeIdx = 0; state.shortsIdx = 0;
    syncInputs(); renderCanvas();
    toast("입력한 사연으로 6컷 대본과 이미지를 생성했습니다!");
  }

  async function init() {
    els.canvas = q("ssultoonCanvas");
    els.pager = q("shortsPager");
    els.counter = q("slideCounter");
    els.toast = q("statusToast");
    els.epTitle = q("episodeTitleInput");
    els.watermark = q("watermarkInput");
    els.aiCheck = q("aiLabelCheck");
    els.ptabs = q("panelTabs");
    els.pStage = q("panelStage");
    els.pSpeaker = q("panelSpeaker");
    els.pScene = q("panelScene");
    els.pExpr = q("panelExpression");
    els.pBubble = q("panelBubble");
    els.pSfx = q("panelSfx");
    els.pNarr = q("panelNarration");
    els.pDial = q("panelDialogue");

    const strip = q("presetStrip");
    try {
      const r = await fetch("/assets/episodes.json");
      if (r.ok) episodes = await r.json();
    } catch (e) {}
    if (!episodes.length && window.__FALLBACK_EPISODES__) episodes = window.__FALLBACK_EPISODES__;

    if (strip && episodes.length) {
      strip.innerHTML = episodes.slice(0, 6).map((ep) =>
        '<button type="button" class="preset-btn" data-ep="' + esc(ep.id) + '">' + esc(ep.emoji) + " " + esc(ep.genre) + "</button>"
      ).join("");
      strip.querySelectorAll(".preset-btn").forEach((b) => {
        b.addEventListener("click", () => {
          const found = episodes.find((x) => x.id === b.dataset.ep);
          if (found) loadEp(found);
        });
      });
    }

    const reqEp = new URLSearchParams(window.location.search).get("ep");
    const first = episodes.find((x) => x.id === reqEp) || episodes[0];
    if (first) loadEp(first);

    q("autoBuildBtn").addEventListener("click", () => buildFromIdea(q("storyIdeaInput").value));
    els.epTitle.addEventListener("input", () => { state.title = els.epTitle.value; renderCanvas(); });
    els.watermark.addEventListener("input", () => { state.watermark = els.watermark.value; renderCanvas(); });
    els.aiCheck.addEventListener("change", () => { state.showAiLabel = els.aiCheck.checked; renderCanvas(); });

    const upd = () => {
      const p = state.panels[state.activeIdx];
      if (!p) return;
      p.stage = els.pStage.value; p.speaker = els.pSpeaker.value;
      p.scene = els.pScene.value; p.expression = els.pExpr.value;
      p.bubbleType = els.pBubble.value; p.sfx = els.pSfx.value;
      p.narration = els.pNarr.value; p.dialogue = els.pDial.value;
      syncInputs(); renderCanvas();
    };
    [els.pStage, els.pSpeaker, els.pScene, els.pExpr, els.pBubble, els.pSfx, els.pNarr, els.pDial].forEach((n) => {
      n.addEventListener("input", upd); n.addEventListener("change", upd);
    });

    document.querySelectorAll(".abtn").forEach((b) => {
      b.addEventListener("click", () => {
        state.aspect = b.dataset.aspect;
        document.querySelectorAll(".abtn").forEach((x) => x.classList.toggle("is-active", x === b));
        renderCanvas();
      });
    });

    q("prevSlideBtn").addEventListener("click", () => {
      state.shortsIdx = (state.shortsIdx - 1 + state.panels.length) % state.panels.length;
      state.activeIdx = state.shortsIdx;
      syncInputs(); renderCanvas();
    });
    q("nextSlideBtn").addEventListener("click", () => {
      state.shortsIdx = (state.shortsIdx + 1) % state.panels.length;
      state.activeIdx = state.shortsIdx;
      syncInputs(); renderCanvas();
    });

    q("downloadPngBtn").addEventListener("click", () => {
      renderCanvas();
      const a = document.createElement("a");
      a.download = "guidehollow-ssultoon-" + state.aspect + ".png";
      a.href = els.canvas.toDataURL("image/png");
      a.click();
      toast("고화질 PNG 썰툰 이미지를 기기에 저장했습니다.");
    });

    q("copyScriptBtn").addEventListener("click", () => {
      const txt = [state.title, "", ...state.panels.map((p) => `[${p.panelNumber}컷] ${p.narration} | ${p.speaker}: ${p.dialogue}`), "", state.hashtags.join(" ")].join("\n");
      navigator.clipboard?.writeText(txt);
      toast("쇼츠·블로그 대본과 해시태그가 복사되었습니다!");
    });
  }

  document.addEventListener("DOMContentLoaded", init);
})();
