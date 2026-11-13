#!/usr/bin/env python3
"""우선기획 홈페이지 정적 사이트 생성기.

사용법: python3 build.py <출력폴더>
- books.json(책 목록), style.css, covers/ 를 읽어 출력폴더에 사이트 전체를 만든다.
- 새 책은 books.json에 항목을 추가하고 covers/에 표지(가로 600px jpg)를 넣은 뒤 다시 실행한다.
"""
import json, shutil, sys, html
from urllib.parse import quote
from pathlib import Path

SRC = Path(__file__).parent
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else SRC / "dist")
DOMAIN = "https://woosunai.com"
EMAIL = "kwsong@woosunai.com"
FONT = "https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css"

data = json.loads((SRC / "books.json").read_text(encoding="utf-8"))
KO, EN = data["ko"], data["en"]
e = html.escape


def amazon(asin):
    return f"https://www.amazon.com/dp/{asin}"


def fmt_date(d, lang="ko"):
    y, m, dd = d.split("-")
    if lang == "ko":
        return f"{y}년 {int(m)}월 {int(dd)}일"
    months = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]
    return f"{months[int(m) - 1]} {int(dd)}, {y}"


NAV_KO = [("/books/", "도서"), ("/about/", "소개"), ("/contact/", "연락"), ("/en/", "EN")]
NAV_EN = [("/en/", "Books"), ("/en/#about", "About"), ("/en/#contact", "Contact"), ("/", "한국어")]


def page(path, title, body, desc, lang="ko", active=None):
    nav = NAV_EN if lang == "en" else NAV_KO
    links = "".join(
        f'<a href="{h}"{" aria-current=page" if h == active else ""}>{t}</a>' for h, t in nav)
    brand = ('<a class="brand" href="/en/"><img src="/assets/img/logo.png" alt="" width="30" height="36">Woosun Planning<small>AI-Powered Insights</small></a>' if lang == "en"
             else '<a class="brand" href="/"><img src="/assets/img/logo.png" alt="" width="30" height="36">우선기획<small>AI-Powered Insights</small></a>')
    if lang == "en":
        foot = (f'<strong>Woosun Planning (우선기획)</strong> · Publisher Kwangwoo Song · Seoul, Korea<br>'
                f'<a href="mailto:{EMAIL}">{EMAIL}</a><br>© 2026 Woosun Planning')
    else:
        foot = (f'<strong>우선기획</strong> · 대표 송광우 · '
                f'출판사 신고 제2026-000059호 · 서울 강서구<br>'
                f'<a href="mailto:{EMAIL}">{EMAIL}</a><br>© 2026 우선기획')
    url = DOMAIN + path
    full_title = title if title.startswith(("우선기획", "Woosun")) else f"{title} | {'Woosun Planning' if lang == 'en' else '우선기획'}"
    doc = f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="website">
<meta property="og:image" content="{DOMAIN}/assets/covers/vol5.jpg">
<link rel="icon" href="/assets/img/logo.png" type="image/png">
<link rel="stylesheet" href="{FONT}">
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<header class="site-head"><div class="wrap">{brand}<nav class="nav" aria-label="{'Main' if lang == 'en' else '주 메뉴'}">{links}</nav></div></header>
<main class="wrap">
{body}
</main>
<footer class="site-foot"><div class="wrap">{foot}</div></footer>
</body>
</html>
"""
    f = OUT / path.lstrip("/")
    if path.endswith("/"):
        f = f / "index.html"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(doc, encoding="utf-8")
    return path


def cover(img, alt, eager=False):
    return (f'<img class="cover" src="/assets/covers/{img}" alt="{e(alt)} 표지" width="600" '
            f'{"" if eager else "loading=lazy "}decoding="async">')


def card_ko(b):
    return (f'<a class="card" href="/books/{b["slug"]}/">{cover(b["cover"], b["title"])}'
            f'<div class="t">{e(b["title"])}</div><div class="a">{e(b["author"])} · {b["date"][:4]}</div></a>')


def card_en(b, href=None):
    href = href or f'/en/#{b["slug"]}'
    return (f'<a class="card" href="{href}">{cover(b["cover"], b["title"])}'
            f'<div class="t">{e(b["title"])}</div><div class="a">{e(b["author"])}</div></a>')


pages = []

# ---------- 홈 ----------
new = KO[0]
home = f"""
<section class="hero">
<h1>AI로 기획하고,<br>사람이 검증해 만드는 책.</h1>
<p>우선기획은 2026년 서울에서 문을 연 1인 출판사입니다. AI 활용으로 일과 삶을 바꾸는 실용서를 국내 서점과 Amazon에서 펴냅니다.</p>
</section>
<section class="featured" aria-labelledby="new-title">
<a href="/books/{new['slug']}/">{cover(new['cover'], new['title'], eager=True)}</a>
<div>
<div class="label">신간</div>
<h2 id="new-title"><a href="/books/{new['slug']}/" style="color:inherit">{e(new['title'])}</a></h2>
<p class="sub">{e(new['subtitle'])}</p>
<p>{e(new['oneline'])}</p>
<div class="buy">{''.join(f'<a class="btn{"" if i == 0 else " ghost"}" href="{s["url"]}" rel="noopener" target="_blank">{e(s["name"])}</a>' for i, s in enumerate(new['stores']))}</div>
</div>
</section>
<section class="section" aria-labelledby="ko-books">
<div class="section-head"><h2 id="ko-books">국내 도서</h2><a href="/books/">전체 보기</a></div>
<div class="grid">{''.join(card_ko(b) for b in KO[1:])}</div>
</section>
<section class="section" aria-labelledby="en-books">
<div class="section-head"><h2 id="en-books">Books in English · Amazon</h2><a href="/en/">More</a></div>
<div class="grid">{''.join(card_en(b) for b in EN)}</div>
</section>
"""
pages.append(page("/", "우선기획 — AI로 기획하고 사람이 검증하는 1인 출판사", home,
                  "우선기획은 2026년 서울에서 문을 연 1인 출판사로, AI 활용으로 일과 삶을 바꾸는 실용서를 펴냅니다."))

# ---------- 도서 목록 ----------
books = f"""
<div class="prose" style="padding-bottom:16px"><h1>도서</h1><p class="lead">우선기획이 펴낸 책입니다. 표지를 누르면 책 소개와 구매처가 나옵니다.</p></div>
<section class="section" style="border-top:0;padding-top:16px" aria-labelledby="ko"><div class="section-head"><h2 id="ko">국내 도서</h2></div>
<div class="grid">{''.join(card_ko(b) for b in KO)}</div></section>
<section class="section" aria-labelledby="en"><div class="section-head"><h2 id="en">영문 도서 (Amazon)</h2></div>
<div class="grid">{''.join(card_en(b) for b in EN)}</div></section>
"""
pages.append(page("/books/", "도서", books, "우선기획이 펴낸 국내 도서와 Amazon 영문 도서 목록.", active="/books/"))

# ---------- 책별 상세 ----------
for b in KO:
    eds = "".join(
        f'<div><dt>{e(x["label"])}</dt><dd>ISBN {x["isbn"]} · {x["price"]}</dd></div>' for x in b["editions"])
    toc = ("<h2 style='font-size:19px;margin:32px 0 4px'>차례</h2><ul class='toc'>" +
           "".join(f"<li>{e(t)}</li>" for t in b["toc"]) + "</ul>") if b["toc"] else ""
    body = "".join(f"<p>{e(p)}</p>" for p in b["body"])
    stores = "".join(
        f'<a class="btn{"" if i == 0 else " ghost"}" href="{s["url"]}" rel="noopener" target="_blank">{e(s["name"])}에서 보기</a>'
        for i, s in enumerate(b["stores"]))
    det = f"""
<article class="book">
<div>{cover(b['cover'], b['title'], eager=True)}</div>
<div>
<h1>{e(b['title'])}</h1>
{f'<p class="sub">{e(b["subtitle"])}</p>' if b['subtitle'] else ''}
<p class="lead" style="font-size:18px">{e(b['oneline'])}</p>
{body}
<div class="buy">{stores}</div>
{toc}
<dl class="meta">
<div><dt>지은이</dt><dd>{e(b['author'])}</dd></div>
<div><dt>펴낸 날</dt><dd>{fmt_date(b['date'])}</dd></div>
{eds}
<div><dt>펴낸곳</dt><dd>우선기획</dd></div>
</dl>
<a class="back" href="/books/">← 전체 도서</a>
</div>
</article>
"""
    pages.append(page(f"/books/{b['slug']}/", b["title"], det, b["oneline"], active="/books/"))

# ---------- 소개 ----------
about = f"""
<div class="prose">
<h1>소개</h1>
<p class="lead">우선기획은 2026년 4월에 문을 연 1인 출판사입니다. AI로 기획하고 집필하되, 무엇을 낼지와 무엇이 맞는지는 사람이 판단합니다.</p>
<h2>하는 일</h2>
<p>일과 삶에 바로 쓰는 실용서를 냅니다. 국내에서는 교보문고·예스24·알라딘·밀리의 서재 등에서 전자책과 종이책을, 해외에서는 Amazon에서 영어·스페인어·프랑스어·독일어·포르투갈어 책을 펴냅니다.</p>
<h2>만드는 방식</h2>
<p>직접 만든 멀티에이전트 집필 시스템 BookOrchestra로 기획, 자료 조사, 집필, 편집, 사실 확인을 역할별로 나눠 진행합니다. 초안을 쓴 AI에게 검증을 맡기지 않고, 마지막 판정은 사람이 합니다. 그 과정은 『은퇴하고 AI로 출판사를 차렸습니다』에 기록했습니다.</p>
<h2>대표 송광우</h2>
<img src="/assets/img/author.jpg" alt="우선기획 대표 송광우" width="200" style="width:200px;margin:4px 0 20px;border:1px solid var(--line)">
<p>30여 년간 디지털 전환 컨설팅 분야에서 일했습니다. 2026년 4월 우선기획을 설립했습니다. 블로그 <a href="https://blog.naver.com/kwsongai" rel="noopener" target="_blank">송광우의 AI 실무노트</a>에 AI 활용과 1인 기업 운영 기록을 씁니다.</p>
<h2>출판사 정보</h2>
<dl class="meta" style="margin-top:8px">
<div><dt>상호</dt><dd>우선기획 (Woosun Planning)</dd></div>
<div><dt>대표</dt><dd>송광우</dd></div>
<div><dt>출판사 신고</dt><dd>2026년 4월 23일 · 제2026-000059호</dd></div>
<div><dt>소재지</dt><dd>서울 강서구</dd></div>
<div><dt>이메일</dt><dd><a href="mailto:{EMAIL}">{EMAIL}</a></dd></div>
</dl>
</div>
"""
pages.append(page("/about/", "소개", about, "우선기획과 대표 송광우 소개, 출판사 정보.", active="/about/"))

# ---------- 연락 ----------
contact = f"""
<div class="prose">
<h1>연락</h1>
<p class="lead">모든 문의는 메일로 받습니다.</p>
<p style="font-size:22px;font-weight:600;margin:24px 0 32px"><a href="mailto:{EMAIL}">{EMAIL}</a></p>
<h2>이런 문의를 받습니다</h2>
<ul>
<li>도서 유통·제휴</li>
<li>원고 기고와 공동 출간</li>
<li>강연, AI 활용·1인 출판 관련 자문</li>
<li>독자 문의와 오탈자 제보</li>
</ul>
<p>메일 제목에 문의 유형을 적어 주시면 더 빨리 확인할 수 있습니다.</p>
</div>
"""
pages.append(page("/contact/", "연락", contact, "우선기획 문의 메일 안내.", active="/contact/"))

# ---------- English ----------
def lang_links(l):
    a = lambda u, t: f'<a href="{u}" rel="noopener" target="_blank">{t}</a>'
    out = []
    if l.get("kindle"):
        out.append(a(amazon(l["kindle"]), "Kindle"))
    if l.get("paperback"):
        out.append(a(amazon(l["paperback"]), "Paperback"))
    if not out:  # ASIN 미확인: 아마존 제목 검색으로 연결
        out.append(a("https://www.amazon.com/s?k=" + quote(l["title"]), "Amazon"))
    return " · ".join(out)


def en_block(b):
    if "languages" in b:
        langs = "".join(
            f'<div>{cover(l["cover"], l["title"])}<div class="t">{e(l["name"])}</div>'
            f'<div class="links">{lang_links(l)}</div></div>'
            for l in b["languages"])
        return (f'<section class="section" id="{b["slug"]}"><h2 style="font-size:24px;margin:0 0 6px">{e(b["title"])}</h2>'
                f'<p class="sub" style="color:var(--muted);margin:0 0 12px">{e(b["subtitle"])} · {e(b["author"])}</p>'
                f'<p>{e(b["oneline"])}</p><div class="langs">{langs}</div></section>')
    return (f'<section class="section" id="{b["slug"]}"><div class="featured" style="border:0;padding:0">'
            f'{cover(b["cover"], b["title"])}<div><h2>{e(b["title"])}</h2><p class="sub">{e(b["subtitle"])}</p>'
            f'<p>{e(b["oneline"])} <span style="color:var(--muted)">By {e(b["author"])}.</span></p>'
            f'<div class="buy"><a class="btn" href="{amazon(b["kindle"])}" rel="noopener" target="_blank">Kindle on Amazon</a>'
            f'<a class="btn ghost" href="{amazon(b["paperback"])}" rel="noopener" target="_blank">Paperback</a></div></div></div></section>')


en = f"""
<section class="hero">
<h1>Practical books,<br>made with AI and checked by people.</h1>
<p>Woosun Planning is a one-person publisher founded in Seoul in 2026. We publish practical books on using AI to change how you work and live, sold in Korean bookstores and on Amazon.</p>
</section>
{''.join(en_block(b) for b in EN)}
<section class="section prose" id="about" style="padding-top:56px">
<h2 style="margin-top:0">About</h2>
<p>Woosun Planning is a one-person publisher founded in April 2026. We use AI to plan and write, but people decide what to publish and whether it is right.</p>
<p>We publish practical books for work and life. In Korea our e-books and print books are sold through Kyobo, Yes24, Aladin and Millie's Library; abroad we publish on Amazon in English, Spanish, French, German and Portuguese.</p>
<p>Our books are drafted with BookOrchestra, a multi-agent writing system that splits planning, research, writing, editing and fact-checking into separate roles. The AI that writes a draft never approves it; the final call is always human.</p>
<p>The press is run by Kwangwoo Song, who spent some 30 years in digital transformation consulting and founded Woosun Planning in April 2026. He grew up in Seoul and speaks Korean as his native language, and writes about using AI and running a one-person company on his <a href="https://blog.naver.com/kwsongai" rel="noopener" target="_blank">Korean-language blog</a>.</p>
<h2 id="contact">Contact</h2>
<p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
</section>
"""
pages.append(page("/en/", "Woosun Planning — Books in English", en,
                  "Woosun Planning is a one-person publisher founded in Seoul in 2026, making practical books on using AI to change how you work and live.",
                  lang="en", active="/en/"))

# ---------- 404 ----------
nf = '<div class="prose"><h1>페이지를 찾을 수 없습니다</h1><p><a href="/">처음으로</a> · <a href="/books/">도서 목록</a></p></div>'
page("/404.html", "페이지를 찾을 수 없습니다", nf, "우선기획")

# ---------- 자산 ----------
(OUT / "assets/covers").mkdir(parents=True, exist_ok=True)
shutil.copy(SRC / "style.css", OUT / "assets/style.css")
(OUT / "assets/img").mkdir(parents=True, exist_ok=True)
for c in list((SRC / "images").glob("*.jpg")) + list((SRC / "images").glob("*.png")):
    shutil.copy(c, OUT / "assets/img" / c.name)
for c in (SRC / "covers").glob("*.jpg"):
    shutil.copy(c, OUT / "assets/covers" / c.name)
(OUT / "assets/favicon.svg").write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="#1f3a68"/>'
    '<text x="32" y="44" font-size="34" text-anchor="middle" fill="#fff" font-family="sans-serif" font-weight="700">우</text></svg>',
    encoding="utf-8")
(OUT / "CNAME").write_text("woosunai.com\n", encoding="utf-8")
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {DOMAIN}/sitemap.xml\n", encoding="utf-8")
(OUT / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{DOMAIN}{p}</loc></url>\n" for p in pages) + "</urlset>\n", encoding="utf-8")
print(f"built {len(pages)} pages -> {OUT}")
