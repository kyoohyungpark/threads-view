# -*- coding: utf-8 -*-
# src/<번호>_<제목>/ 안의 (이미지 + 글.txt)를 읽어 index.html과 각 글 페이지를 생성한다.
import os, glob, html, re

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
IMG_EXT = (".jpg", ".jpeg", ".png", ".gif", ".webp")

def find_image(folder):
    for f in sorted(os.listdir(folder)):
        if f.lower().endswith(IMG_EXT):
            return f
    return None

def load_posts():
    posts = []
    for folder in sorted(glob.glob(os.path.join(SRC, "*"))):
        if not os.path.isdir(folder):
            continue
        name = os.path.basename(folder)
        m = re.match(r"(\d+)", name)
        if not m:
            continue
        num = int(m.group(1))
        title = name[len(m.group(1)):].lstrip("_-. ") or name
        img = find_image(folder)
        txt_path = os.path.join(folder, "글.txt")
        text = ""
        if os.path.exists(txt_path):
            with open(txt_path, encoding="utf-8") as fp:
                text = fp.read().strip()
        posts.append({"num": num, "name": name, "title": title, "img": img, "text": text})
    posts.sort(key=lambda p: p["num"])
    return posts

PAGE_CSS = """body{font-family:-apple-system,"Malgun Gothic",sans-serif;margin:0;color:#111;background:#fafafa}
.wrap{max-width:1000px;margin:0 auto;padding:20px 16px}
a{color:#1a73e8;text-decoration:none}
.top{margin-bottom:16px;font-size:15px}
.cols{display:flex;gap:20px;align-items:flex-start;flex-wrap:wrap}
.col{flex:1 1 360px;min-width:300px}
img{width:100%;border:1px solid #ddd;border-radius:8px;display:block}
.hint{color:#888;font-size:13px;margin:8px 0 0}
pre{white-space:pre-wrap;font-family:inherit;font-size:16px;line-height:1.7;background:#fff;border:1px solid #eee;border-radius:8px;padding:16px;margin:0}
button{font-size:15px;padding:10px 16px;border:1px solid #ccc;border-radius:8px;background:#fff;cursor:pointer;margin-top:10px}
h2{font-size:18px;font-weight:500}
.list a{display:flex;gap:12px;align-items:center;padding:12px;background:#fff;border:1px solid #eee;border-radius:10px;margin-bottom:10px;color:#111}
.list .n{font-size:18px;font-weight:600;color:#1a73e8;min-width:28px;text-align:center}
.list img{width:64px;height:64px;object-fit:cover;border-radius:8px;flex:none}
.list .t{font-size:15px;color:#444;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}"""

def post_html(p):
    n = p["num"]
    img_tag = '<img src="src/%s/%s" alt="">' % (html.escape(p["name"]), html.escape(p["img"])) if p["img"] else '<p>(사진 없음)</p>'
    text_esc = html.escape(p["text"])
    return """<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>#%d %s</title>
<style>%s</style></head><body><div class="wrap">
<div class="top"><a href="index.html">← 목록</a></div>
<h2>#%d %s</h2>
<div class="cols">
  <div class="col">%s<p class="hint">사진 우클릭 → "이미지 복사" / 모바일은 길게 누르기</p></div>
  <div class="col"><pre id="txt">%s</pre>
  <button onclick="navigator.clipboard.writeText(document.getElementById('txt').innerText).then(()=>{this.innerText='\\u2705 \\ubcf5\\uc0ac\\ub428!';setTimeout(()=>this.innerText='\\uae00 \\uc804\\uccb4 \\ubcf5\\uc0ac',1500)})">글 전체 복사</button></div>
</div></div></body></html>""" % (n, html.escape(p["title"]), PAGE_CSS, n, html.escape(p["title"]), img_tag, text_esc)

def index_html(posts):
    items = []
    for p in posts:
        thumb = '<img src="src/%s/%s" alt="">' % (html.escape(p["name"]), html.escape(p["img"])) if p["img"] else ''
        preview = html.escape(p["text"][:60].replace("\n", " "))
        items.append('<a href="%d.html"><span class="n">%d</span>%s<span class="t">%s</span></a>'
                     % (p["num"], p["num"], thumb, preview))
    return """<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>스레드 글 목록</title>
<style>%s</style></head><body><div class="wrap">
<h2>스레드 글 목록 (%d개)</h2>
<div class="list">%s</div></div></body></html>""" % (PAGE_CSS, len(posts), "".join(items))

def main():
    posts = load_posts()
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html(posts))
    for p in posts:
        with open(os.path.join(ROOT, "%d.html" % p["num"]), "w", encoding="utf-8") as f:
            f.write(post_html(p))
    print("built %d posts" % len(posts))

if __name__ == "__main__":
    main()
