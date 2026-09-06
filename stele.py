"""
书法字体检索：碑帖/作者 字典访问。
- POST  http://shufazidian.com/s.php  检索字图，带书体 sort 参数
- 解析所有 <a href=...jpg title="朝代·作者·碑帖"> 的条目
- 提供按 (字, 书体, 作者/碑帖) 过滤，返回高质量字图
"""

from __future__ import annotations

import re
import logging
from typing import Iterable

import requests

LOG = logging.getLogger("calligraphy_finder.stele")

# shufazidian 端点
BASE_URL = "http://shufazidian.com/s.php"
SORT_MAP = {
    "xingshu": "8",   # 行书
    "kaishu":  "9",   # 楷书
    "caoshu":  "7",   # 草书
    "zhangcao":"1",   # 章草
    "lishu":   "6",   # 隶书
    "weibei":  "5",   # 魏碑
    "jiandu":  "4",   # 简牍
    "zhuanshu":"3",   # 篆书
}
# 用户友好的书体名
STELE_STYLES = [
    ("kaishu", "楷书"),
    ("xingshu", "行书"),
    ("caoshu",  "草书"),
    ("lishu",   "隶书"),
    ("zhuanshu","篆书"),
    ("zhangcao","章草"),
    ("weibei",  "魏碑"),
    ("jiandu",  "简牍"),
]

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "http://shufazidian.com/s.php",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

_SESSION = requests.Session()


def _hit(sort: str, ch: str) -> str:
    """POST 一次检索，返回 HTML 文本。失败返回空串。"""
    try:
        r = _SESSION.post(
            BASE_URL,
            data={"wd": ch, "sort": sort},
            headers=_HEADERS,
            timeout=12,
        )
        if r.status_code == 200 and len(r.text) > 4000:
            return r.text
        LOG.warning("shufazidian 检索 %s 返回空 sort=%s", ch, sort)
    except Exception as e:
        LOG.warning("shufazidian 检索 %s 异常 sort=%s: %s", ch, sort, e)
    return ""


_A_TAG = re.compile(
    r'<a[^>]+href="(https?://[a-z0-9.\-]+\.shufazidian\.com/gq/[^"]+\.jpg)"'
    r'[^>]+title="([^"]+)"',
    re.I,
)


def parse_stele_results(html: str) -> list[dict]:
    """解析 shufazidian 返回的 HTML，提取 (大字 URL, 缩略图 URL, title)。"""
    if not html:
        return []
    out: list[dict] = []
    # 同时抓缩略图
    thumb_pat = re.compile(r'<img src="(https?://[^"]+gq/[^"]+?\.jpg)"', re.I)
    thumbs = [m.group(1) for m in thumb_pat.finditer(html)]

    for idx, m in enumerate(_A_TAG.finditer(html)):
        big_url = m.group(1)
        title = m.group(2).strip()
        parts = [p.strip() for p in title.split("·")]
        era = parts[0] if len(parts) > 0 else ""
        author = parts[1] if len(parts) > 1 else ""
        book = parts[2] if len(parts) > 2 else title
        out.append({
            "url": big_url,
            "thumb": thumbs[idx] if idx < len(thumbs) else big_url,
            "era": era,
            "author": author,
            "book": book,
            "title": title,
        })
    return out


def search_char(ch: str,
                 styles: Iterable[str] = ("kaishu", "xingshu"),
                 author_filter: str | None = None,
                 book_filter: str | None = None,
                 limit_per_style: int = 40) -> list[dict]:
    """检索一个汉字在多个书体下的字图。

    author_filter / book_filter: 非空时仅保留作者/碑帖包含子串的项
    """
    results: list[dict] = []
    seen_urls: set[str] = set()
    for style_key in styles:
        sort = SORT_MAP.get(style_key)
        if not sort:
            continue
        html = _hit(sort, ch)
        items = parse_stele_results(html)
        for it in items:
            if it["url"] in seen_urls:
                continue
            if author_filter and author_filter not in it["author"]:
                continue
            if book_filter and book_filter not in it["book"]:
                continue
            seen_urls.add(it["url"])
            it["style"] = style_key
            results.append(it)
            if len(results) >= limit_per_style:
                break
        if len(results) >= limit_per_style:
            break
    return results


def download_image(url: str) -> bytes | None:
    try:
        r = _SESSION.get(url, headers={
            **_HEADERS,
            "Referer": "http://shufazidian.com/s.php",
        }, timeout=20)
        if r.status_code == 200 and r.content:
            return r.content
    except Exception as e:
        LOG.warning("下载失败 %s: %s", url, e)
    return None


# 一些常见"作者/碑帖"预置（供 UI 默认选中/推荐）
FAVORITES = [
    ("颜真卿",  "多宝塔碑"),
    ("颜真卿",  "颜勤礼碑"),
    ("颜真卿",  "麻姑仙坛记"),
    ("欧阳询",  "九成宫醴泉铭"),
    ("欧阳询",  "化度寺碑"),
    ("柳公权",  "玄秘塔碑"),
    ("柳公权",  "神策军碑"),
    ("赵孟頫",  "胆巴碑"),
    ("赵孟頫",  "三门记"),
    ("王羲之",  "兰亭序"),
    ("王羲之",  "圣教序"),
    ("褚遂良",  "雁塔圣教序"),
    ("褚遂良",  "倪宽赞"),
    ("苏轼",    "黄州寒食诗帖"),
    ("米芾",    "蜀素帖"),
    ("黄庭坚",  "松风阁"),
    ("怀素",    "自叙帖"),
    ("张旭",    "古诗四帖"),
    ("智永",    "真草千字文"),
    ("王献之",  "洛神赋"),
]


if __name__ == "__main__":
    import sys
    ch = sys.argv[1] if len(sys.argv) > 1 else "永"
    for it in search_char(ch, styles=("kaishu", "xingshu"))[:6]:
        print(it["title"], "->", it["url"][:80])
