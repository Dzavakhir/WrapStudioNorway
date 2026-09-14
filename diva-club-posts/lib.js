/* Shared runtime for every variant template.
   Reads ?r=9x16|4x5|1x1 from the URL and stamps it on <html data-r="...">,
   then signals readiness once webfonts + images have finished loading so the
   renderer never screenshots a half-painted canvas. */
(function () {
  var params = new URLSearchParams(location.search);
  var r = params.get("r") || "4x5";
  if (["9x16", "4x5", "1x1"].indexOf(r) === -1) r = "4x5";
  document.documentElement.setAttribute("data-r", r);

  window.DIVA_READY = false;
  function markReady() { window.DIVA_READY = true; }

  window.addEventListener("load", function () {
    var imgs = Array.prototype.slice.call(document.images);
    var pending = imgs.filter(function (i) { return !i.complete; });
    Promise.all([
      document.fonts ? document.fonts.ready : Promise.resolve(),
      Promise.all(pending.map(function (i) {
        return new Promise(function (res) { i.addEventListener("load", res); i.addEventListener("error", res); });
      }))
    ]).then(function () { requestAnimationFrame(function () { requestAnimationFrame(markReady); }); });
  });
})();
