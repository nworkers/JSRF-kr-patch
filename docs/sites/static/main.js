// JSRF Korean patch site (issue #23): before/after sliders and command tabs.
(function () {
  "use strict";

  // Before/after: load the two images; until both exist the stage keeps its placeholder look.
  document.querySelectorAll(".compare").forEach(function (fig) {
    var stage = fig.querySelector(".compare-stage");
    var before = fig.querySelector(".pane-before");
    var after = fig.querySelector(".pane-after");
    var loaded = 0;
    [[before, fig.dataset.before], [after, fig.dataset.after]].forEach(function (pair) {
      var img = new Image();
      img.onload = function () {
        pair[0].style.backgroundImage = "url('" + pair[1] + "')";
        loaded += 1;
        if (loaded === 2) fig.classList.add("is-ready");
      };
      img.onerror = function () { fig.classList.add("is-missing"); };
      img.src = pair[1];
    });

    function set(pct) {
      pct = Math.max(0, Math.min(100, pct));
      stage.style.setProperty("--pos", pct + "%");
      stage.setAttribute("aria-valuenow", String(Math.round(pct)));
    }
    function fromEvent(e) {
      var r = stage.getBoundingClientRect();
      set(((e.clientX - r.left) / r.width) * 100);
    }
    var dragging = false;
    stage.addEventListener("pointerdown", function (e) {
      dragging = true;
      stage.setPointerCapture(e.pointerId);
      fromEvent(e);
    });
    stage.addEventListener("pointermove", function (e) { if (dragging) fromEvent(e); });
    stage.addEventListener("pointerup", function () { dragging = false; });
    stage.addEventListener("pointercancel", function () { dragging = false; });
    stage.addEventListener("keydown", function (e) {
      var now = Number(stage.getAttribute("aria-valuenow"));
      if (e.key === "ArrowLeft") { set(now - 5); e.preventDefault(); }
      if (e.key === "ArrowRight") { set(now + 5); e.preventDefault(); }
      if (e.key === "Home") { set(0); e.preventDefault(); }
      if (e.key === "End") { set(100); e.preventDefault(); }
    });
  });

  // Original-language switch (English mode / Japanese build) for the "before" pane.
  document.querySelectorAll(".compare-switch").forEach(function (group) {
    var fig = group.closest(".compare");
    var pane = fig.querySelector(".pane-before");
    var label = fig.querySelector("[data-before-label]");
    group.querySelectorAll("button").forEach(function (btn) {
      btn.addEventListener("click", function () {
        group.querySelectorAll("button").forEach(function (b) { b.setAttribute("aria-pressed", String(b === btn)); });
        pane.style.backgroundImage = "url('" + btn.dataset.beforeSrc + "')";
        if (label) label.textContent = btn.dataset.label;
      });
    });
  });

  // Command tabs.
  document.querySelectorAll("[data-tabs]").forEach(function (box) {
    var buttons = box.querySelectorAll("[data-tab]");
    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        buttons.forEach(function (b) { b.setAttribute("aria-selected", String(b === btn)); });
        box.querySelectorAll("[data-panel]").forEach(function (p) {
          p.hidden = p.dataset.panel !== btn.dataset.tab;
        });
      });
    });
  });
})();
