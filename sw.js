/* Textionary 背誦本 — offline cache.
   改過 index.html 之後，把下面的版本號 +1，手機才會抓到新版。 */
const VERSION = "textionary-v77";
const FILES = [
  "./", "./index.html", "./manifest.webmanifest",
  "./icon-180.png", "./icon-192.png", "./icon-512.png"
];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(VERSION).then((c) => c.addAll(FILES)).then(() => self.skipWaiting()));
});

/* 聖經全文（bible/xx.json）與懷氏著作（egw/xx.json）另放長期快取，
   App 改版時不清掉；內容更新時用「先給舊的、背景抓新的」策略自動換新，
   使用者不必手動清除、也不必整批重新下載。 */
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
  if (longLived) {                                   // 書卷與懷氏段落：先給快取（若有），同時背景抓新的
    e.respondWith(
      caches.open(longLived).then((cache) => cache.match(req).then((hit) => {
        const fresh = fetch(req).then((res) => {
          cache.put(req, res.clone());
          return res;
        }).catch(() => hit);
        return hit || fresh;               // 有快取先用快取（快），背景仍會更新，下次自動就是新的
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
