/*
 * Prevents the "unstyled page flashes first, then the real page" glitch.
 *
 * The exported HTML has an empty <body>, so React cannot hydrate it. It
 * discards the whole <html> element and builds a new one, including a fresh
 * <link rel="stylesheet">. For a moment the new content is on screen before
 * that stylesheet has loaded, which is the flash.
 *
 * This script watches for the <html> element being replaced and keeps the new
 * one invisible until its stylesheet is ready (with a safety timeout).
 * It must load in <head>, before the Remix entry script.
 */
(function () {
  var original = document.documentElement;
  var MAX_WAIT_MS = 2500;

  function stylesReady(html) {
    var links = html.querySelectorAll('link[rel="stylesheet"][href*="/assets/"]');
    if (!links.length) return false;
    for (var i = 0; i < links.length; i++) {
      if (!links[i].sheet) return false;
    }
    return true;
  }

  function guard(html) {
    var start = performance.now();
    html.style.setProperty("visibility", "hidden", "important");
    (function check() {
      if (stylesReady(html) || performance.now() - start > MAX_WAIT_MS) {
        html.style.removeProperty("visibility");
        if (!html.getAttribute("style")) html.removeAttribute("style");
        return;
      }
      requestAnimationFrame(check);
    })();
  }

  var seen = original;
  new MutationObserver(function () {
    var html = document.documentElement;
    if (html && html !== seen) {
      seen = html;
      if (html !== original) guard(html);
    }
  }).observe(document, { childList: true });
})();
