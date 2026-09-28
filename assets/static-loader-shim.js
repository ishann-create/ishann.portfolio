/*
 * Static-hosting shim for the Remix loaders.
 *
 * The page bundles were exported from a Remix app whose routes have loaders.
 * On client-side navigation (e.g. /work -> /#about) Remix fetches
 *   /?_data=routes/_index   or   /work?_data=routes/work
 * server.py answers those with JSON, but a static host (Vercel, Netlify,
 * GitHub Pages, ...) just returns index.html, so the route receives a string
 * instead of { home, navigationItems, socialLinks } and crashes with
 * "Cannot read properties of undefined (reading 'hero')".
 *
 * This script answers those requests locally from index_data.json /
 * work_data.json, so the site works on any host. It must load BEFORE the
 * Remix entry script.
 */
(function () {
  var sources = {
    "routes/_index": "/index_data.json",
    "routes/work": "/work_data.json"
  };
  var cache = {};
  var realFetch = window.fetch.bind(window);

  function loaderData(route) {
    if (!cache[route]) {
      cache[route] = realFetch(sources[route])
        .then(function (r) {
          if (!r.ok) throw new Error("HTTP " + r.status);
          return r.json();
        })
        .then(function (json) {
          return json.state.loaderData[route];
        })
        .catch(function (err) {
          delete cache[route];
          throw err;
        });
    }
    return cache[route];
  }

  function json(body, status) {
    return new Response(JSON.stringify(body), {
      status: status || 200,
      headers: { "Content-Type": "application/json; charset=utf-8" }
    });
  }

  window.fetch = function (input, init) {
    try {
      var raw = typeof input === "string" ? input : input && input.url;
      var url = new URL(raw, window.location.href);
      if (url.origin === window.location.origin) {
        var route = url.searchParams.get("_data");
        if (route && sources[route]) {
          return loaderData(route).then(function (data) {
            return json(data);
          });
        }
        // Page-view counter: there is no backend on a static host.
        if (url.pathname.replace(/\/$/, "") === "/api/page-view") {
          return Promise.resolve(json({ source: "organic", total: 0 }));
        }
      }
    } catch (e) {
      /* fall through to the real fetch */
    }
    return realFetch(input, init);
  };
})();
