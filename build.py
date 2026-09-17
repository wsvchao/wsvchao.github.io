# -*- coding: utf-8 -*-
"""Build both editions from one source.

    python3 build.py          -> 銘刻心版 (app/)
    python3 build.py egw      -> 銘刻心版 研讀版 (app2/), with Ellen White passages
"""
import io, os, re, shutil, sys

EGW = (len(sys.argv) > 1 and sys.argv[1] == "egw")
OUT = "/home/claude/app2" if EGW else "/home/claude/app"
DATA = "/tmp/appdata_egw.json" if EGW else "/tmp/appdata.json"
ART = "artifact3.html" if EGW else "artifact2.html"

body = io.open("/home/claude/app/app_body.html", encoding="utf-8").read()
data = io.open(DATA, encoding="utf-8").read().strip()
assert body.count("__DATA__") == 1
app = body.replace("__DATA__", data)

if EGW:
    for old, new in [
        (u"<title>銘刻心版</title>", u"<title>銘刻心版　研讀版</title>"),
        (u'sub:"聖經主題索引", mark1:"銘刻", mark2:"心版", ed:""',
         u'sub:"聖經主題索引", mark1:"銘刻", mark2:"心版", ed:"（研讀版）"'),
        (u'sub:"圣经主题索引", mark1:"铭刻", mark2:"心版", ed:""',
         u'sub:"圣经主题索引", mark1:"铭刻", mark2:"心版", ed:"（研读版）"'),
        (u'sub:"Topical Scripture Index", mark1:"銘刻", mark2:"心版", ed:""',
         u'sub:"Topical Scripture Index", mark1:"銘刻", mark2:"心版", ed:"(Study)"'),
    ]:
        assert app.count(old) == 1, old
        app = app.replace(old, new)

os.makedirs(OUT, exist_ok=True)
io.open(os.path.join(OUT, ART), "w", encoding="utf-8").write(app)

TITLE = u"銘刻心版　研讀版" if EGW else u"銘刻心版"
HEAD = u'''<!doctype html>
<html lang="zh-Hant" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex, nofollow">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="color-scheme" content="dark">
<meta name="theme-color" content="#0F141D">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black">
<meta name="apple-mobile-web-app-title" content="%s">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-180.png">
</head>
<body>
''' % TITLE
TAIL = u'''

<script>
if ("serviceWorker" in navigator) {
  window.addEventListener("load", function () {
    navigator.serviceWorker.register("sw.js").catch(function () {});
  });
}
</script>
</body>
</html>
'''
io.open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(HEAD + app + TAIL)

# shared static files
if EGW:
    for f in ["robots.txt", "icon-180.png", "icon-192.png", "icon-512.png", "icon-1024.png"]:
        shutil.copy(os.path.join("/home/claude/app", f), os.path.join(OUT, f))
    mf = io.open("/home/claude/app/manifest.webmanifest", encoding="utf-8").read()
    mf = mf.replace(u"銘刻心版", TITLE)
    io.open(os.path.join(OUT, "manifest.webmanifest"), "w", encoding="utf-8").write(mf)
    swp = os.path.join(OUT, "sw.js")
    if not os.path.exists(swp):
        sw = io.open("/home/claude/app/sw.js", encoding="utf-8").read()
        io.open(swp, "w", encoding="utf-8").write(re.sub(r'textionary-v\d+', "study-v0", sw))
else:
    swp = os.path.join(OUT, "sw.js")

# bump the cache version so phones pick up the new build
sw = io.open(swp, encoding="utf-8").read()
tag = "study" if EGW else "textionary"
m = re.search(tag + r'-v(\d+)', sw)
n = int(m.group(1)) + 1
sw = sw.replace(m.group(0), "%s-v%d" % (tag, n))
io.open(swp, "w", encoding="utf-8").write(sw)
print("built %s: %s, index.html; sw -> %s-v%d" % (OUT, ART, tag, n))
