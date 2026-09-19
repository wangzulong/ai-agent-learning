# -*- coding: utf-8 -*-
"""下载腾讯云开发者社区"王海涛"全部文章并转为 Markdown。仅用标准库。"""
import re, time, html as htmllib
from html.parser import HTMLParser
from urllib.request import Request, urlopen
from pathlib import Path

OUT = Path(r"D:/ai_agent_learning/王海涛-腾讯云专栏/articles")
RAW = Path(r"D:/ai_agent_learning/王海涛-腾讯云专栏/raw")
OUT.mkdir(parents=True, exist_ok=True)
RAW.mkdir(parents=True, exist_ok=True)

ARTICLES = [
    ("2734355", "00", "2026-08-31", "序章"),
    ("2735190", "01", "2026-09-01", "第一篇-约束金字塔"),
    ("2737089", "02", "2026-09-04", "第二篇-战略层设计"),
    ("2737628", "03", "2026-09-05", "第三篇-架构层设计"),
    ("2738011", "04", "2026-09-06", "第四篇-契约层设计"),
    ("2738299", "05", "2026-09-07", "第五篇-门禁层设计"),
    ("2738794", "06", "2026-09-08", "第六篇-实现层设计"),
    ("2740420", "07", "2026-09-10", "第七篇-规约文件构造"),
    ("2741161", "08", "2026-09-10", "第八篇-多Agent编排"),
    ("2741580", "09", "2026-09-11", "第九篇-记忆与知识"),
    ("2742110", "10", "2026-09-12", "第十篇-冰山假设"),
    ("2742960", "11", "2026-09-14", "第十一篇-进击的测试"),
    ("2743376", "12", "2026-09-15", "第十二篇-成熟度模型"),
]

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"}


def fetch(url):
    req = Request(url, headers=UA)
    with urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def extract_container(html, marker):
    """截取 marker 所在 <div ...> 开始、配对 </div> 结束的片段。"""
    i = html.find(marker)
    if i == -1:
        return None
    start = html.rfind("<div", 0, i)
    depth = 0
    pos = start
    for m in re.finditer(r"<div\b|</div>", html[start:]):
        if m.group(0) == "<div":
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                pos = start + m.end()
                break
    return html[start:pos]


class MDConverter(HTMLParser):
    """轻量 HTML→Markdown，覆盖本站正文用到的标签。"""

    BLOCK_END = {"p", "h1", "h2", "h3", "h4", "h5", "h6", "li", "blockquote", "pre", "table", "hr", "tr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.list_stack = []  # 'ul' / 'ol' with counters
        self.in_pre = False
        self.pre_buf = []
        self.pre_lang = ""
        self.in_code = False
        self.code_buf = []
        self.link_href = None
        self.link_text = []
        self.quote_depth = 0
        self.skip = 0  # script/style

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class", "")
        if tag in ("script", "style"):
            self.skip += 1
            return
        if tag == "pre" or (tag == "div" and "code-block" in cls):
            self.in_pre = True
            self.pre_buf = []
            m = re.search(r"language-([\w#+-]+)", cls)
            self.pre_lang = m.group(1) if m else ""
            return
        if tag == "code" and not self.in_pre:
            self.in_code = True
            self.code_buf = []
            return
        if tag == "br":
            self.out.append("\n")
        elif tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.out.append("\n" + "#" * int(tag[1]) + " ")
        elif tag == "p":
            self.out.append("\n")
        elif tag in ("ul", "ol"):
            self.list_stack.append([tag, 0])
        elif tag == "li":
            indent = "  " * (len(self.list_stack) - 1)
            if self.list_stack and self.list_stack[-1][0] == "ol":
                self.list_stack[-1][1] += 1
                self.out.append("\n" + indent + f"{self.list_stack[-1][1]}. ")
            else:
                self.out.append("\n" + indent + "- ")
        elif tag == "blockquote":
            self.quote_depth += 1
            self.out.append("\n" + "> " * self.quote_depth)
        elif tag == "a":
            self.link_href = a.get("href", "")
            self.link_text = []
        elif tag == "img":
            alt = a.get("alt", "")
            src = a.get("src", "") or a.get("data-src", "")
            if src:
                self.out.append(f"![{alt}]({src})")
        elif tag in ("strong", "b"):
            self.out.append("**")
        elif tag in ("em", "i"):
            self.out.append("*")
        elif tag == "hr":
            self.out.append("\n\n---\n\n")
        elif tag == "table":
            self.out.append("\n")
        elif tag == "tr":
            self.out.append("\n|")
        elif tag in ("td", "th"):
            self.out.append(" ")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
            return
        if tag == "pre" or (tag == "div" and self.in_pre and not self.get_starttag_text()):
            pass
        if self.in_pre and tag in ("pre", "div"):
            code = "".join(self.pre_buf).strip("\n")
            fence = "```"
            self.out.append(f"\n\n{fence}{self.pre_lang}\n{code}\n{fence}\n\n")
            self.in_pre = False
            return
        if self.in_code and tag == "code":
            self.out.append("`" + "".join(self.code_buf) + "`")
            self.in_code = False
            return
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6", "p", "li"):
            self.out.append("\n")
        elif tag in ("ul", "ol"):
            if self.list_stack:
                self.list_stack.pop()
            if not self.list_stack:
                self.out.append("\n")
        elif tag == "blockquote":
            self.quote_depth = max(0, self.quote_depth - 1)
        elif tag == "a":
            text = "".join(self.link_text).strip()
            if self.link_href and text:
                self.out.append(f"[{text}]({self.link_href})")
            elif text:
                self.out.append(text)
            self.link_href, self.link_text = None, []
        elif tag in ("strong", "b"):
            self.out.append("**")
        elif tag in ("em", "i"):
            self.out.append("*")
        elif tag in ("td", "th"):
            self.out.append("|")
        elif tag == "tr":
            self.out.append("|")

    def handle_data(self, data):
        if self.skip:
            return
        if self.in_pre:
            self.pre_buf.append(data)
            return
        if self.in_code:
            self.code_buf.append(data)
            return
        if self.link_href is not None:
            self.link_text.append(data)
        self.out.append(data)

    def result(self):
        text = "".join(self.out)
        text = re.sub(r"[ \t]+\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def html2md(fragment):
    c = MDConverter()
    c.feed(fragment)
    return c.result()


def clean_md(md):
    # 去掉残留的行首块级标签痕迹
    md = re.sub(r"</?(?:div|span|section|figure|figcaption)[^>]*>", "", md)
    md = re.sub(r"<br\s*/?>", "\n", md)
    return md


def extract_markdown(html, aid):
    """优先从 __NEXT_DATA__ JSON 取 Markdown 正文，失败再退回 HTML 提取。"""
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
    if m:
        try:
            import json
            data = json.loads(m.group(1))
            fb = data["props"]["pageProps"]["fallback"]
            for key, val in fb.items():
                if isinstance(val, dict) and "articleInfo" in val:
                    info = val["articleInfo"]
                    content = info.get("content") or ""
                    if info.get("title"):
                        return info["title"], content
        except Exception as e:
            print(f"  [json-parse-fail {aid}: {e}]")
    frag = extract_container(html, 'class="mod-content__markdown"') or extract_container(html, "rno-markdown3")
    if not frag:
        return None, None
    t = re.search(r"<title>(.*?)</title>", html, re.S)
    title = re.sub(r"<[^>]+>", "", t.group(1)).strip() if t else aid
    return title, clean_md(html2md(frag))


def main():
    results = []
    for aid, no, date, short in ARTICLES:
        url = f"https://developer.cloud.tencent.com/article/{aid}"
        try:
            html = fetch(url)
        except Exception as e:
            print(f"[FAIL] {aid} {short}: {e}")
            results.append((no, short, url, date, "下载失败"))
            continue
        (RAW / f"{aid}.html").write_text(html, encoding="utf-8")
        title, md = extract_markdown(html, aid)
        if not md:
            print(f"[NO-CONTENT] {aid} {short}")
            results.append((no, short, url, date, "未找到正文"))
            continue
        title = htmllib.unescape(title or f"{no}-{short}").replace("-腾讯云开发者社区-腾讯云", "").replace("-腾讯云开发者社区", "").strip()
        md = clean_md(md)
        header = (
            f"---\n标题: {title}\n作者: 王海涛（中基宁波集团 CTO · 腾讯云 TVP）\n"
            f"发布日期: {date}\n来源: {url}\n系列: AI Harness Engineering\n---\n\n"
        )
        path = OUT / f"{no}-{short}.md"
        path.write_text(header + md + "\n", encoding="utf-8")
        chars = len(md)
        print(f"[OK] {no}-{short} {chars} 字符 -> {path.name}")
        results.append((no, short, url, date, f"OK {chars}字符"))
        time.sleep(1.5)

    print("\n===== 汇总 =====")
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
