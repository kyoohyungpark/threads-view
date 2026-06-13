# -*- coding: utf-8 -*-
# src/<카테고리>/<번호>_<제목>/ 안의 (글.txt + 선택적 이미지)를 읽어
# index.html(섹션별 번호 목록)과 각 글 페이지를 생성한다.
import os, glob, html, re

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
IMG_EXT = (".jpg", ".jpeg", ".png", ".gif", ".webp")

# (폴더명, 화면표시 라벨, 페이지 파일 접두어)
CATEGORIES = [
    ("ssul", "오늘의 썰", "s"),
    ("ads", "특가·광고", "a"),
]

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

PAGE_CSS = """body{font-family:-apple-system,"Malgun Gothic",sans-serif;margin:0;color:#111;background:#fafafa}
.wrap{max-width:1000px;margin:0 auto;padding:20px 16px}
a{color:#1a73e8;text-decoration:none}
.top{margin-bottom:16px;font-size:15px}
.cols{display:flex;gap:20px;align-items:flex-start;flex-wrap:wrap}
.col{flex:1 1 360px;min-width:300px}
.full{max-width:640px}
img{width:100%;border:1px solid #ddd;border-radius:8px;display:block}
.hint{color:#888;font-size:13px;margin:8px 0 0}
pre{white-space:pre-wrap;font-family:inherit;font-size:17px;line-height:1.8;background:#fff;border:1px solid #eee;border-radius:8px;padding:18px;margin:0}
button{font-size:15px;padding:10px 16px;border:1px solid #ccc;border-radius:8px;background:#fff;cursor:pointer;margin-top:10px}
h2{font-size:18px;font-weight:500}
.sec{margin:8px 0 28px}
.sec h2{border-bottom:2px solid #eee;padding-bottom:8px}
.list a{display:flex;gap:12px;align-items:center;padding:12px;background:#fff;border:1px solid #eee;border-radius:10px;margin-bottom:10px;color:#111}
.list .n{font-size:18px;font-weight:600;color:#1a73e8;min-width:28px;text-align:center}
.list img{width:64px;height:64px;object-fit:cover;border-radius:8px;flex:none}
.list .t{font-size:15px;color:#444;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}"""

COPY_BTN = ('<button onclick="navigator.clipboard.writeText('
            "document.getElementById('txt').innerText)"
            ".then(()=>{this.innerText='\\u2705 \\ubcf5\\uc0ac\\ub428!';"
            "setTimeout(()=>this.innerText='\\uae00 \\uc804\\uccb4 \\ubcf5\\uc0ac',1500)})\">"
            "글 전체 복사</button>")

def page_name(p):
    pref = dict((c[0], c[2]) for c in CATEGORIES)[p["cat"]]
    return "%s%d.html" % (pref, p["num"])

def post_html(p):
    text_esc = html.escape(p["text"])
    if p["img"]:
        img_tag = '<img src="src/%s/%s/%s" alt="">' % (p["cat"], html.escape(p["name"]), html.escape(p["img"]))
        body = ('<div class="cols"><div class="col">%s'
                '<p class="hint">사진 우클릭 → "이미지 복사" / 모바일은 길게 누르기</p></div>'
                '<div class="col"><pre id="txt">%s</pre>%s</div></div>'
                % (img_tag, text_esc, COPY_BTN))
    else:
        body = '<div class="full"><pre id="txt">%s</pre>%s</div>' % (text_esc, COPY_BTN)
    return """<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>#%d %s</title>
<style>%s</style></head><body><div class="wrap">
<div class="top"><a href="index.html">← 목록</a></div>
<h2>#%d %s</h2>
%s</div></body></html>""" % (p["num"], html.escape(p["title"]), PAGE_CSS, p["num"], html.escape(p["title"]), body)

def index_html(sections):
    blocks = []
    for label, posts in sections:
        items = []
        for p in posts:
            thumb = ('<img src="src/%s/%s/%s" alt="">' % (p["cat"], html.escape(p["name"]), html.escape(p["img"]))
                     if p["img"] else '')
            preview = html.escape((p["text"][:60] or p["title"]).replace("\n", " "))
            items.append('<a href="%s"><span class="n">%d</span>%s<span class="t">%s</span></a>'
                         % (page_name(p), p["num"], thumb, preview))
        body = "".join(items) if items else '<p style="color:#888">아직 글이 없어요</p>'
        blocks.append('<div class="sec"><h2>%s (%d개)</h2><div class="list">%s</div></div>'
                      % (label, len(posts), body))
    return """<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>스레드 글 목록</title>
<style>%s</style></head><body><div class="wrap">%s</div></body></html>""" % (PAGE_CSS, "".join(blocks))

def main():
    # 옛 루트 페이지 정리
    for old in glob.glob(os.path.join(ROOT, "[0-9]*.html")):
        os.remove(old)
    for pref in ("s", "a"):
        for old in glob.glob(os.path.join(ROOT, pref + "[0-9]*.html")):
            os.remove(old)
    sections = []
    total = 0
    for cat, label, _ in CATEGORIES:
        posts = load_posts(cat)
        for p in posts:
            with open(os.path.join(ROOT, page_name(p)), "w", encoding="utf-8") as f:
                f.write(post_html(p))
        sections.append((label, posts))
        total += len(posts)
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html(sections))
    print("built %d posts (%s)" % (total, ", ".join("%s:%d" % (l, len(p)) for l, p in sections)))

if __name__ == "__main__":
    main()
