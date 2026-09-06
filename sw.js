/* Textionary 背誦本 — offline cache.
   改過 index.html 之後，把下面的版本號 +1，手機才會抓到新版。 */
const VERSION = "textionary-v43";
const FILES = [
  "./", "./index.html", "./manifest.webmanifest",
  "./icon-180.png", "./icon-192.png", "./icon-512.png"
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});

/* 聖經全文（bible/xx.json）另放一個快取，App 改版時不清掉，
   使用者不必為了一次更新重新下載已經看過的書卷。 */
const BIBLE = "textionary-bible-v1";
const EGW = "textionary-egw-v1";

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((k) => k !== VERSION && k !== BIBLE && k !== EGW).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;   // 字型等外部資源不快取
  const longLived = url.pathname.indexOf("/bible/") >= 0 ? BIBLE
                  : url.pathname.indexOf("/egw/") >= 0 ? EGW : null;
  if (longLived) {                                   // 書卷與懷氏段落：抓過就長期留著
    e.respondWith(
      caches.match(req).then((hit) => hit || fetch(req).then((res) => {
        const copy = res.clone();
        caches.open(longLived).then((c) => c.put(req, copy));
        return res;
      }))
    );
    return;
  }
  e.respondWith(
    caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      const copy = res.clone();
      caches.open(VERSION).then((c) => c.put(req, copy));
      return res;
    }).catch(() => caches.match("./index.html")))
  );
});
