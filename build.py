# -*- coding: utf-8 -*-
# src/<카테고리>/<번호>_<제목>/ 의 (글.txt + 선택 이미지)를 읽어
# 랜딩(index.html) → 카테고리 목록(<cat>.html) → 글 페이지(접두어+번호.html) 3단 구조를 만든다.
import os, glob, html, re

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
IMG_EXT = (".jpg", ".jpeg", ".png", ".gif", ".webp")

# folder, 라벨, 페이지접두어, 메인색, 보조색(그라데이션), 이모지, 한줄설명
CATEGORIES = [
    ("ssul",   "일상글",   "s", "#7C5CFF", "#B49CFF", "📖", "사연·일상 글 모음"),
    ("debate", "스하리",   "d", "#FF5B6E", "#FF9A8B", "🔥", "스하리 글 모음"),
    ("ads",    "특가·광고", "a", "#0FB5A6", "#4FD6C2", "🛒", "쿠팡·특가 모음"),
]
CAT_BY_KEY = {c[0]: c for c in CATEGORIES}

def find_image(folder):
    for f in sorted(os.listdir(folder)):
        if f.lower().endswith(IMG_EXT):
            return f
    return None

def load_posts(cat):
    posts = []
    base = os.path.join(SRC, cat)
    if not os.path.isdir(base):
        return posts
    for folder in sorted(glob.glob(os.path.join(base, "*"))):
        if not os.path.isdir(folder):
            continue
        name = os.path.basename(folder)
        m = re.match(r"(\d+)", name)
        num = int(m.group(1)) if m else len(posts) + 1
        title = name[len(m.group(1)):].lstrip("_-. ") if m else name
        img = find_image(folder)
        txt_path = os.path.join(folder, "글.txt")
        text = ""
        if os.path.exists(txt_path):
            with open(txt_path, encoding="utf-8") as fp:
                text = fp.read().strip()
        posts.append({"num": num, "name": name, "title": title or name,
                      "img": img, "text": text, "cat": cat})
    posts.sort(key=lambda p: p["num"])
    return posts

BASE_CSS = """*{box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Malgun Gothic","Apple SD Gothic Neo",sans-serif;margin:0;color:#1a1a1a;background:#f4f5f7;-webkit-font-smoothing:antialiased}
.wrap{max-width:920px;margin:0 auto;padding:24px 16px 60px}
a{text-decoration:none;color:inherit}
.back{display:inline-flex;align-items:center;gap:6px;font-size:14px;color:#666;margin-bottom:18px}
.back:hover{color:#1a1a1a}
.hero{font-size:26px;font-weight:800;letter-spacing:-.5px;margin:6px 0 4px}
.hero-sub{color:#888;font-size:14px;margin-bottom:26px}
/* 랜딩 카테고리 카드 */
.cats{display:grid;grid-template-columns:1fr;gap:16px}
.cat-card{display:flex;align-items:center;gap:16px;padding:22px 20px;border-radius:18px;color:#fff;position:relative;overflow:hidden;transition:transform .15s,box-shadow .15s;box-shadow:0 6px 18px rgba(0,0,0,.08)}
.cat-card:hover{transform:translateY(-3px);box-shadow:0 12px 28px rgba(0,0,0,.16)}
.cat-emoji{font-size:34px;width:58px;height:58px;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,.22);border-radius:14px;flex:none}
.cat-name{font-size:20px;font-weight:800;letter-spacing:-.3px}
.cat-desc{font-size:13.5px;opacity:.92;margin-top:3px}
.cat-count{margin-left:auto;font-size:14px;font-weight:700;background:rgba(255,255,255,.25);padding:7px 13px;border-radius:999px;white-space:nowrap}
/* 카테고리 헤더 바 */
.catbar{border-radius:16px;padding:20px 22px;color:#fff;margin-bottom:22px;display:flex;align-items:center;gap:14px;box-shadow:0 6px 18px rgba(0,0,0,.1)}
.catbar .cat-emoji{width:48px;height:48px;font-size:26px}
.catbar .nm{font-size:20px;font-weight:800}
.catbar .ct{margin-left:auto;font-size:13.5px;font-weight:700;background:rgba(255,255,255,.25);padding:6px 12px;border-radius:999px}
/* 글 목록 */
.list{display:grid;gap:12px}
.item{display:flex;gap:14px;align-items:center;padding:14px 16px;background:#fff;border-radius:14px;box-shadow:0 2px 8px rgba(0,0,0,.05);transition:transform .12s,box-shadow .12s}
.item:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(0,0,0,.1)}
.num{font-size:17px;font-weight:800;min-width:30px;height:30px;border-radius:9px;display:flex;align-items:center;justify-content:center;color:#fff;flex:none}
.item img{width:60px;height:60px;object-fit:cover;border-radius:10px;flex:none}
.item .t{font-size:15px;color:#333;line-height:1.5;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
/* 글 페이지 */
.cols{display:flex;gap:22px;align-items:flex-start;flex-wrap:wrap}
.col{flex:1 1 360px;min-width:300px}
.full{max-width:660px}
.postimg{width:100%;border-radius:14px;display:block;box-shadow:0 4px 14px rgba(0,0,0,.1)}
.hint{color:#999;font-size:13px;margin:10px 0 0}
.posttext{white-space:pre-wrap;font-size:17.5px;line-height:1.85;background:#fff;border-radius:16px;padding:24px;box-shadow:0 3px 12px rgba(0,0,0,.06);margin:0}
.copy{font-size:15px;font-weight:700;padding:12px 20px;border:none;border-radius:12px;color:#fff;cursor:pointer;margin-top:14px;transition:filter .12s}
.copy:hover{filter:brightness(1.07)}
.copy:active{transform:scale(.98)}
.posttitle{font-size:20px;font-weight:800;margin:4px 0 20px;letter-spacing:-.3px}"""

def grad(c):
    return "linear-gradient(135deg,%s,%s)" % (c[3], c[4])

def landing_html(counts):
    cards = []
    for c in CATEGORIES:
        key, label, _, c1, c2, emoji, desc = c
        cards.append(
            '<a class="cat-card" style="background:%s" href="%s.html">'
            '<span class="cat-emoji">%s</span>'
            '<span><span class="cat-name">%s</span><div class="cat-desc">%s</div></span>'
            '<span class="cat-count">%d개</span></a>'
            % (grad(c), key, emoji, html.escape(label), html.escape(desc), counts.get(key, 0)))
    return """<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>스레드 글 보관함</title>
<style>%s</style></head><body><div class="wrap">
<div class="hero">스레드 글 보관함</div>
<div class="hero-sub">카테고리를 골라 들어가세요</div>
<div class="cats">%s</div></div></body></html>""" % (BASE_CSS, "".join(cards))

def page_name(p):
    return "%s%d.html" % (CAT_BY_KEY[p["cat"]][2], p["num"])

def category_html(c, posts):
    key, label, _, c1, c2, emoji, desc = c
    items = []
    for p in posts:
        thumb = ('<img src="src/%s/%s/%s" alt="">' % (p["cat"], html.escape(p["name"]), html.escape(p["img"]))
                 if p["img"] else '')
        preview = html.escape((p["text"][:70] or p["title"]).replace("\n", " "))
        items.append('<a class="item" href="%s"><span class="num" style="background:%s">%d</span>%s'
                     '<span class="t">%s</span></a>'
                     % (page_name(p), c1, p["num"], thumb, preview))
    body = "".join(items) if items else '<p style="color:#999">아직 글이 없어요</p>'
    return """<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>%s</title>
<style>%s</style></head><body><div class="wrap">
<a class="back" href="index.html">← 홈으로</a>
<div class="catbar" style="background:%s"><span class="cat-emoji">%s</span>
<span class="nm">%s</span><span class="ct">%d개</span></div>
<div class="list">%s</div></div></body></html>""" % (
        html.escape(label), BASE_CSS, grad(c), emoji, html.escape(label), len(posts), body)

def post_html(p):
    c = CAT_BY_KEY[p["cat"]]
    c1 = c[3]
    text_esc = html.escape(p["text"])
    copy_btn = ('<button class="copy" style="background:%s" onclick="navigator.clipboard.writeText('
                "document.getElementById('txt').innerText)"
                ".then(()=>{this.innerText='\\u2705 \\ubcf5\\uc0ac\\ub428!';"
                "setTimeout(()=>this.innerText='\\uae00 \\uc804\\uccb4 \\ubcf5\\uc0ac',1500)})\">"
                "글 전체 복사</button>") % c1
    if p["img"]:
        img_tag = '<img class="postimg" src="src/%s/%s/%s" alt="">' % (p["cat"], html.escape(p["name"]), html.escape(p["img"]))
        body = ('<div class="cols"><div class="col">%s'
                '<p class="hint">사진 우클릭 → "이미지 복사" / 모바일은 길게 누르기</p></div>'
                '<div class="col"><pre class="posttext" id="txt">%s</pre>%s</div></div>'
                % (img_tag, text_esc, copy_btn))
    else:
        body = '<div class="full"><pre class="posttext" id="txt">%s</pre>%s</div>' % (text_esc, copy_btn)
    return """<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>#%d %s</title>
<style>%s</style></head><body><div class="wrap">
<a class="back" href="%s.html">← %s 목록</a>
<div class="posttitle">#%d %s</div>
%s</div></body></html>""" % (p["num"], html.escape(p["title"]), BASE_CSS,
        p["cat"], html.escape(c[1]), p["num"], html.escape(p["title"]), body)

def main():
    # 옛 페이지 정리
    for old in glob.glob(os.path.join(ROOT, "[0-9]*.html")):
        os.remove(old)
    for pref in ("s", "d", "a"):
        for old in glob.glob(os.path.join(ROOT, pref + "[0-9]*.html")):
            os.remove(old)
    counts = {}
    parts = []
    for c in CATEGORIES:
        posts = load_posts(c[0])
        counts[c[0]] = len(posts)
        with open(os.path.join(ROOT, c[0] + ".html"), "w", encoding="utf-8") as f:
            f.write(category_html(c, posts))
        for p in posts:
            with open(os.path.join(ROOT, page_name(p)), "w", encoding="utf-8") as f:
                f.write(post_html(p))
        parts.append("%s:%d" % (c[0], len(posts)))
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(landing_html(counts))
    print("built (%s)" % ", ".join(parts))

if __name__ == "__main__":
    main()
