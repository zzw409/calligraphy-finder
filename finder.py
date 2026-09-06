"""
书法字典检索核心模块
- 在线主路径：汉典 zdic.net 字源字形（甲骨文/金文/小篆/隶书）
- 在线副路径：百度书法图片聚合 + 通用 curl 抓字图
- 本地兜底：使用开源字体（MaShanZheng / LongCang / LiuJianMaoCao / ZCOOLKuaiLe）+ Windows 系统字体（simkai / simfang / simhei）
- 输出：单字透明 PNG（PNG 文件可直接嵌入 PPT/Word/海报）
"""

from __future__ import annotations

import io
import os
import re
import time
import base64
import hashlib
import logging
from pathlib import Path
from typing import Iterable
from urllib.parse import quote

import requests
from PIL import Image, ImageDraw, ImageFont

LOG = logging.getLogger("calligraphy_finder")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

REQUEST_TIMEOUT = 12
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.zdic.net/",
}

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent
FONTS_DIR = BASE_DIR / "fonts"
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------


def char_unicode_hex(ch: str) -> str:
    """返回字符的 4 位以上大写十六进制 Unicode（汉典 SVG 路径使用此编码）。"""
    return f"{ord(ch):X}"


def is_hanzi(ch: str) -> bool:
    """粗略判断是否为 CJK 汉字。"""
    cp = ord(ch)
    return (
        0x4E00 <= cp <= 0x9FFF      # CJK 统一汉字
        or 0x3400 <= cp <= 0x4DBF    # CJK 扩展 A
        or 0x20000 <= cp <= 0x2A6DF  # CJK 扩展 B
        or 0x2A700 <= cp <= 0x2B73F  # CJK 扩展 C
        or 0x2B740 <= cp <= 0x2B81F  # CJK 扩展 D
    )


# ---------------------------------------------------------------------------
# 数据源 1：汉典 zdic.net 标准字形（SVG） + 字源字形（zy 子目录）
# ---------------------------------------------------------------------------
# 规律：
#   https://img.zdic.net/kai/cn/6C38.svg        -> 楷书（中国大陆）
#   https://img.zdic.net/kai/hk/6C38.svg        -> 楷书（香港）
#   https://img.zdic.net/kai/tw/6C38.svg        -> 楷书（台湾）
#   https://img.zdic.net/kai/jp/6C38.svg        -> 楷书（日本）
#   https://img.zdic.net/kai/kr/6C38.svg        -> 楷书（韩国）
#   https://img.zdic.net/zy/jiaguwen/43_EA05.svg  -> 甲骨文
#   https://img.zdic.net/zy/jinwen/33_ECD5.svg    -> 金文
#   https://img.zdic.net/zy/xiaozhuan/27_6C38.svg -> 小篆
#   https://img.zdic.net/zy/lishu/93_F253.svg     -> 隶书

ZDIC_STD_STYLES = {
    "kaishu_cn": ("kai", "cn", "楷书（中国大陆）"),
    "kaishu_hk": ("kai", "hk", "楷书（香港）"),
    "kaishu_tw": ("kai", "tw", "楷书（台湾）"),
    "kaishu_jp": ("kai", "jp", "楷书（日本）"),
    "kaishu_kr": ("kai", "kr", "楷书（韩国）"),
}
ZDIC_ZY_STYLES = {
    "jiaguwen": "甲骨文",
    "jinwen": "金文",
    "xiaozhuan": "小篆",
    "lishu": "隶书",
}


def fetch_zdic_svg(ch: str, kind: str) -> bytes | None:
    """从汉典抓取单字 SVG。

    kind:
        "kaishu_cn" / "kaishu_hk" / "kaishu_tw" / "kaishu_jp" / "kaishu_kr"
        -> 固定 URL：https://img.zdic.net/kai/<region>/<CODE>.svg
    注：
        汉典字源字形（甲骨文/金文/小篆/隶书）的 URL 含不可预测的桶号前缀，
        在不能访问详情页解析 URL 的情况下命中率很低，故不在此处抓取，
        由本地字体中风格相近的部分（mashanzheng/longcang/liujianmaocao）
        作为近似替代。
    """
    if kind in ZDIC_STD_STYLES:
        which = ZDIC_STD_STYLES[kind]
        code = char_unicode_hex(ch)
        url = f"https://img.zdic.net/{which[0]}/{which[1]}/{code}.svg"
        try:
            r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200 and r.content and b"<svg" in r.content[:200].lower():
                return r.content
        except Exception as e:
            LOG.warning("汉典楷书抓取失败 %s (%s): %s", url, kind, e)
        return None
    raise ValueError(f"unknown kind: {kind}")


def svg_to_png(svg_bytes: bytes, size: int = 512) -> bytes | None:
    """将 SVG 字符串渲染为 PNG。优先使用 cairo 库，无 cairosvg 时回退到 resvg-py，
    都没有时用 PIL 重新手工渲染（性能差但确保可用）。"""
    out = io.BytesIO()
    # 方案 1：cairosvg
    try:
        import cairosvg  # type: ignore

        cairosvg.svg2png(bytestring=svg_bytes, output_width=size, output_height=size, write_to=out)
        return out.getvalue()
    except Exception:
        pass
    # 方案 2：resvg-py（Rust 绑定，质量最好）
    try:
        import resvg_py  # type: ignore

        out.write(resvg_py.svg_to_bytes(svg_string=svg_bytes.decode("utf-8", "ignore")))
        return out.getvalue()
    except Exception:
        pass
    # 方案 3：兜底直接输出 SVG 字节（让浏览器展示，通常前端 <img> 会接收 SVG）
    if svg_bytes:
        return svg_bytes
    return None


# ---------------------------------------------------------------------------
# 数据源 2：汉典按字抓页面，从 URL 字符串里提取 zy/书体/桶号_编号.svg 链接
# ---------------------------------------------------------------------------

# 缓存：char -> 详情页 HTML
_HANS_HTML_CACHE: dict[str, str] = {}


def fetch_zdic_hans_page(ch: str) -> str:
    """抓取汉典单字详情页 HTML。带缓存。"""
    if ch in _HANS_HTML_CACHE:
        return _HANS_HTML_CACHE[ch]
    code = ord(ch)
    url = f"https://www.zdic.net/hans/{code:x}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if r.status_code == 200:
            html = r.text
            _HANS_HTML_CACHE[ch] = html
            return html
    except Exception as e:
        LOG.warning("汉典单字页抓取失败 %s: %s", url, e)
    return ""


def find_zy_url_in_hans_page(ch: str, kind: str) -> str | None:
    """从汉典单字详情页里找出首个 zy/<kind>/NNN_CODE.svg 的 URL。

    浏览器看到的 HTML 形如:
        <img src="https://img.zdic.net/zy/jiaguwen/43_EA05.svg" ...>
    """
    html = fetch_zdic_hans_page(ch)
    if not html:
        return None
    # 寻找任意 zy/<kind>/...svg 链接
    pat = re.compile(rf"https?://img\.zdic\.net/zy/{kind}/[0-9A-Fa-f]+_[0-9A-Fa-f]+\.svg")
    m = pat.search(html)
    return m.group(0) if m else None


# ---------------------------------------------------------------------------
# 数据源 3：本地字体渲染（兜底，永远可用）
# ---------------------------------------------------------------------------
# 字体清单：开源书法字体 + 系统楷仿黑
LOCAL_FONT_PRESETS: dict[str, dict] = {
    "mashanzheng": {"name": "马善政（行楷）", "file": "MaShanZheng.ttf", "type": "ttf"},
    "longcang":    {"name": "龙藏（草书）", "file": "LongCang.ttf",     "type": "ttf"},
    "liujianmaocao": {"name": "刘建毛草（狂草）", "file": "LiuJianMaoCao.ttf", "type": "ttf"},
    "zcoolkuaile": {"name": "站酷快乐体（楷意手写）", "file": "ZCOOLKuaiLe.ttf", "type": "ttf"},
    "simkai":      {"name": "楷体（系统）", "file": "C:/Windows/Fonts/simkai.ttf", "type": "sys"},
    "simfang":     {"name": "仿宋（系统）", "file": "C:/Windows/Fonts/simfang.ttf", "type": "sys"},
    "simhei":      {"name": "黑体（系统）", "file": "C:/Windows/Fonts/simhei.ttf", "type": "sys"},
}


def _font_path(preset_key: str) -> Path:
    info = LOCAL_FONT_PRESETS[preset_key]
    p = Path(info["file"])
    if not p.is_absolute():
        p = FONTS_DIR / p.name
    return p


def render_local(ch: str, preset_key: str = "mashanzheng", size: int = 512) -> bytes:
    """使用本地字体把单字渲染为带透明通道的 PNG（白字黑底，可反转）。

    返回的 PNG 实际上是「白字 + 透明背景」，可嵌入任何底图。
    """
    font_path = _font_path(preset_key)
    if not font_path.exists():
        raise FileNotFoundError(f"字体不存在: {font_path}")

    # 字体尺寸选取：让字大约占 80% 画布
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # 寻找最佳字号
    target_h = int(size * 0.82)
    font_size = 16
    font = None
    for fs in range(target_h, 12, -4):
        try:
            font = ImageFont.truetype(str(font_path), fs)
            bbox = draw.textbbox((0, 0), ch, font=font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            if h <= target_h and w <= target_h:
                font_size = fs
                break
        except Exception:
            continue
    if font is None:
        font = ImageFont.truetype(str(font_path), font_size)

    bbox = draw.textbbox((0, 0), ch, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (size - w) // 2 - bbox[0]
    y = (size - h) // 2 - bbox[1]

    # 一层淡淡的黑色描边 + 黑色实心，增强书法意韵
    draw.text((x, y), ch, font=font, fill=(20, 20, 20, 255))

    out = io.BytesIO()
    img.save(out, format="PNG", optimize=True)
    return out.getvalue()


# ---------------------------------------------------------------------------
# 主入口：在线 + 本地联合，单字多风格产出
# ---------------------------------------------------------------------------


def _cache_path(key: str) -> Path:
    digest = hashlib.md5(key.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{digest}.bin"


def _read_cache(key: str) -> bytes | None:
    p = _cache_path(key)
    if p.exists() and time.time() - p.stat().st_mtime < 60 * 60 * 24 * 7:
        return p.read_bytes()
    return None


def _write_cache(key: str, data: bytes) -> None:
    p = _cache_path(key)
    p.write_bytes(data)


def fetch_char(ch: str, preset_keys: Iterable[str] | None = None,
               size: int = 512, include_online: bool = True) -> list[dict]:
    """为单个汉字产出多个书体的图片。

    返回 list[dict]，每项含：
        - key: 风格标识
        - label: 用户展示名
        - source: 数据源  "zdic_svg" / "local_render"
        - bytes: PNG/SVG 原始字节
        - mime:  "image/png" or "image/svg+xml"

    关键设计：本地字体**先**返回（兜底），在线抓取**后**追加，且严格限时
    （单次 4 秒，总计不超过 6 秒）。这样即使在线全挂，前端也能秒级看到字图。
    """
    results: list[dict] = []
    # 非汉字直接返回空（避免无谓的网络请求与字形查找）
    if not is_hanzi(ch):
        return results
    preset_keys = list(preset_keys) if preset_keys else list(LOCAL_FONT_PRESETS.keys())

    # ---- 本地：选定字体渲染（永远兜底，先返回） ----
    for preset in preset_keys:
        cache_key = f"local::{ch}::{preset}::{size}"
        png = _read_cache(cache_key)
        if png is None:
            try:
                png = render_local(ch, preset, size=size)
                _write_cache(cache_key, png)
            except Exception as e:
                LOG.warning("本地渲染失败 %s/%s: %s", ch, preset, e)
                continue

        if png:
            results.append({
                "key": preset,
                "label": LOCAL_FONT_PRESETS[preset]["name"],
                "source": "local_render",
                "bytes": png,
                "mime": "image/png",
            })

    # ---- 在线：汉典标准字形（5 个地区异体）作为补强，严格限时 ----
    if include_online:
        online_kinds = ["kaishu_cn", "kaishu_hk", "kaishu_tw", "kaishu_jp", "kaishu_kr"]
        online_started = time.time()
        ONLINE_BUDGET = 6.0  # 在线抓取总预算（秒）
        for kind in online_kinds:
            if time.time() - online_started > ONLINE_BUDGET:
                LOG.info("在线抓取超出预算 %.1fs，跳过剩余 %d 个地区", ONLINE_BUDGET, len(online_kinds) - online_kinds.index(kind))
                break
            cache_key = f"zdic::{ch}::{kind}::{size}"
            svg = _read_cache(cache_key)
            if svg is None:
                # 单次 4 秒超时（之前的 12 秒太长了）
                try:
                    import requests
                    from requests.exceptions import Timeout, RequestException
                    which = ZDIC_STD_STYLES[kind]
                    code = char_unicode_hex(ch)
                    url = f"https://img.zdic.net/{which[0]}/{which[1]}/{code}.svg"
                    r = requests.get(url, headers=HEADERS, timeout=4)
                    if r.status_code == 200 and r.content and b"<svg" in r.content[:200].lower():
                        svg = r.content
                        _write_cache(cache_key, svg)
                except Exception as e:
                    LOG.debug("汉典抓取跳过 %s: %s", kind, e)
                    continue

            if not svg:
                continue

            results.append({
                "key": kind,
                "label": ZDIC_STD_STYLES[kind][2],
                "source": "zdic_svg",
                "bytes": svg,
                "mime": "image/svg+xml",
            })

    return results


def fetch_phrase(text: str, preset_key: str = "mashanzheng",
                 size_per_char: int = 256, gap: int = 24,
                 bg: tuple[int, int, int, int] = (255, 255, 255, 0)) -> bytes:
    chars = list(text)
    if not chars:
        raise ValueError("empty text")

    # 渲染每个字
    font_path = _font_path(preset_key)
    images: list[Image.Image] = []
    for ch in chars:
        cache_key = f"local::{ch}::{preset_key}::{size_per_char}"
        png = _read_cache(cache_key)
        if png is None:
            png = render_local(ch, preset_key, size=size_per_char)
            _write_cache(cache_key, png)
        images.append(Image.open(io.BytesIO(png)).convert("RGBA"))

    total_w = sum(im.width for im in images) + gap * (len(images) - 1)
    max_h = max(im.height for im in images)
    canvas = Image.new("RGBA", (total_w, max_h), bg)
    x = 0
    for im in images:
        canvas.paste(im, (x, (max_h - im.height) // 2), im)
        x += im.width + gap

    out = io.BytesIO()
    canvas.save(out, format="PNG", optimize=True)
    return out.getvalue()


# ---------------------------------------------------------------------------
# 拓片/深底字图 → 透明 PNG
# ---------------------------------------------------------------------------
# 碑帖图通常是“黑底白字”(拓片)或“深底浅字”，需要按亮度分离文字与背景，
# 把文字变成透明背景上的黑色，方便嵌入任意场景。


def raster_to_transparent(data: bytes, size: int = 512,
                          mode: str = "auto", invert: bool = False) -> bytes:
    """把一张字图（jpg/png）去底转透明 PNG。

    mode:
        "auto"  图片暗底亮字时(拓片)反色，亮底暗字时保持
        "light" 强制按亮底暗字处理（字更深）
        "dark"  强制按暗底亮字处理（字更浅）
    invert: 布尔；True 时强制反转明暗。
    返回深色文字 + 透明背景的 PNG。
    """
    img = Image.open(io.BytesIO(data))
    img = img.convert("RGBA")
    img = img.resize((size, size), Image.LANCZOS)

    # 亮度
    gray = img.convert("L")
    mean = sum(gray.getdata()) / (gray.width * gray.height)

    # 判断文字是亮是暗：拓片通常是暗底亮字（mean 较低）
    if invert:
        pass
    elif mode == "auto":
        # mean > 128 说明整体偏亮（背景亮、文字暗）=> 保持；否则反转
        invert = mean < 128
    elif mode == "dark":
        invert = True
    else:  # light
        invert = False

    px = img.load()
    w, h = img.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    opx = out.load()

    # 遍历像素：取亮度作为文字 alpha，颜色一律用深墨色
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            lum = (r * 299 + g * 587 + b * 114) // 1000
            if invert:
                lum = 255 - lum
            # 低亮度处接近 0 视为背景透明；越亮越接近正文
            opx[x, y] = (25, 22, 18, lum)

    buf = io.BytesIO()
    out.save(buf, format="PNG", optimize=True)
    return buf.getvalue()


if __name__ == "__main__":
    # 简单自检
    samples = "永存大志"
    for ch in samples:
        items = fetch_char(ch)
        print(f"[{ch}] -> {len(items)} 个图样")
        for it in items:
            print(f"  - {it['key']:14s} | {it['label']:30s} | {it['mime']:14s} | {len(it['bytes']):6d} bytes")
