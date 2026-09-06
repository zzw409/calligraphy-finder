"""Flask 后端：书法字典在线 + 本地检索
- POST /api/search    输入查询内容，返回每字的多种风格图
- GET  /api/img/<token>   返回具体一张图的 PNG / SVG 字节
- GET  /             H5 入口
"""

from __future__ import annotations

import base64
import io
import os
import logging
import time
import hashlib
import json
from pathlib import Path
from typing import Iterable

from flask import Flask, request, jsonify, render_template, Response, send_file, abort

import finder
import stele

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOG = logging.getLogger("server")

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["JSON_AS_ASCII"] = False

# 在内存中缓存：key -> [{"key","label","source","mime","b64"}]
_RESULT_CACHE: dict[str, dict] = {}
_MAX_AGE_SEC = 60 * 60 * 6  # 6 小时失效


def _now() -> float:
    return time.time()


def _render_chars(chars: Iterable[str], preset_keys=None, size: int = 512,
                  include_online: bool = True) -> dict:
    """对每个字调用 finder.fetch_char 并打包成可发送的 JSON。"""
    out_chars = []
    for ch in chars:
        # 非汉字直接返回空 items（避免无谓的网络请求和卡顿）
        if not finder.is_hanzi(ch):
            out_chars.append({
                "char": ch,
                "is_hanzi": False,
                "items": [],
                "note": f"非汉字字符（U+{ord(ch):04X}），暂不支持检索",
            })
            continue
        items = finder.fetch_char(ch, preset_keys=preset_keys, size=size,
                                   include_online=include_online)
        out_chars.append({
            "char": ch,
            "is_hanzi": True,
            "items": [
                {
                    "key": it["key"],
                    "label": it["label"],
                    "source": it["source"],
                    "mime": it["mime"],
                    "b64": base64.b64encode(it["bytes"]).decode("ascii"),
                }
                for it in items
            ],
        })
    return {"chars": out_chars}


def _search(text: str, preset_keys=None, size: int = 512,
            include_online: bool = True) -> dict:
    text = text.strip()
    if not text:
        return {"chars": []}
    # 去重保持顺序
    seen = set()
    chars = []
    for c in text:
        if c.isspace():
            c = " "  # 保留空格
        if c not in seen:
            seen.add(c)
            chars.append(c)

    payload = json.dumps(chars, ensure_ascii=False)
    sig = hashlib.md5((payload + str(size) + str(preset_keys) + str(include_online)).encode("utf-8")).hexdigest()

    cached = _RESULT_CACHE.get(sig)
    if cached and _now() - cached["ts"] < _MAX_AGE_SEC:
        return cached["body"]
    body = _render_chars(chars, preset_keys=preset_keys, size=size, include_online=include_online)
    _RESULT_CACHE[sig] = {"ts": _now(), "body": body}
    return body


@app.post("/api/search")
def api_search():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "文本不能为空"}), 400

    preset_keys = data.get("presets")  # 列表可选
    size = int(data.get("size") or 512)
    size = max(128, min(1024, size))
    include_online = bool(data.get("online", True))

    body = _search(text, preset_keys=preset_keys, size=size, include_online=include_online)
    return jsonify({"text": text, "size": size, "count": len(body["chars"]), **body})


@app.post("/api/phrase")
def api_phrase():
    """整句话拼成一张大图，返回 PNG。"""
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "文本不能为空"}), 400
    preset_key = data.get("preset") or "mashanzheng"
    if preset_key not in finder.LOCAL_FONT_PRESETS:
        preset_key = "mashanzheng"
    size_per_char = int(data.get("size") or 256)
    size_per_char = max(96, min(512, size_per_char))
    gap = int(data.get("gap") or 24)
    gap = max(0, min(120, gap))

    try:
        png = finder.fetch_phrase(text, preset_key=preset_key,
                                  size_per_char=size_per_char, gap=gap)
    except Exception as e:
        LOG.exception("整句渲染失败: %s", e)
        return jsonify({"error": f"渲染失败: {e}"}), 500

    return send_file(io.BytesIO(png), mimetype="image/png",
                     download_name=f"phrase_{preset_key}_{int(_now())}.png")


@app.get("/api/catalog")
def api_catalog():
    """返回所有可选的本地字体预设。"""
    return jsonify({
        "presets": [
            {"key": k, "name": v["name"]}
            for k, v in finder.LOCAL_FONT_PRESETS.items()
        ],
        "stele_styles": [
            {"key": k, "name": n} for k, n in stele.STELE_STYLES
        ],
        "favorite_steles": [
            {"author": a, "book": b} for a, b in stele.FAVORITES
        ],
    })


# 内存缓存：字 -> 书体 -> 结果
_STELE_CACHE: dict[str, list[dict]] = {}


@app.post("/api/stele")
def api_stele():
    """按碑帖/作者检索：POST {text, styles:[], author, book, limit}
    返回每个字在指定书体下、可选的作者/碑帖过滤后的字图。
    """
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "文本不能为空"}), 400
    styles = data.get("styles") or ["kaishu"]
    author_filter = (data.get("author") or "").strip() or None
    book_filter = (data.get("book") or "").strip() or None
    limit = int(data.get("limit") or 40)
    limit = max(1, min(120, limit))

    # 细分到字
    chars = []
    seen = set()
    for c in text:
        if c.isspace():
            continue
        if c not in seen:
            seen.add(c)
            chars.append(c)
    if not chars:
        return jsonify({"error": "未包含汉字"}), 400

    # 缓存键
    cache_key = f"{''.join(chars)}|{','.join(styles)}|{author_filter}|{book_filter}|{limit}"
    if cache_key in _STELE_CACHE:
        return jsonify({"text": text, "chars": _STELE_CACHE[cache_key]})

    out_chars = []
    for ch in chars:
        try:
            items = stele.search_char(
                ch,
                styles=styles,
                author_filter=author_filter,
                book_filter=book_filter,
                limit_per_style=limit,
            )
        except Exception as e:
            LOG.exception("碑帖检索失败: %s", e)
            items = []

        # 若指定了碑帖且无命中，尝试放宽到同作者；再否则不限定碑帖 （保留放宽级别供前端提示）
        relaxed = False
        if not items and book_filter:
            try:
                items = stele.search_char(
                    ch, styles=styles, author_filter=author_filter,
                    book_filter=None, limit_per_style=limit,
                )
                relaxed = True
            except Exception:
                pass
        if not items and author_filter:
            try:
                items = stele.search_char(
                    ch, styles=styles, author_filter=None,
                    book_filter=None, limit_per_style=limit,
                )
                relaxed = True
            except Exception:
                pass

        # 只保留元信息，图片字节通过 /api/stele/img 下载
        out_chars.append({
            "char": ch,
            "count": len(items),
            "relaxed": relaxed,  # True 表示放宽了检索条件（原指定碑帖下无字）
            "items": [
                {
                    "url": it["url"],
                    "thumb": it["thumb"],
                    "era": it["era"],
                    "author": it["author"],
                    "book": it["book"],
                    "title": it["title"],
                    "style": it["style"],
                }
                for it in items[:limit]
            ],
        })
    _STELE_CACHE[cache_key] = out_chars
    return jsonify({"text": text, "chars": out_chars})


@app.get("/api/stele/img")
def api_stele_img():
    """下载并去底转透明 PNG。
    参数 url=原图大图URL，mode=auto|light|dark，size=边长，invert=0|1
    """
    url = request.args.get("url", "")
    mode = request.args.get("mode", "auto")
    size = int(request.args.get("size") or 512)
    size = max(128, min(1024, size))
    invert = request.args.get("invert") == "1"
    if not url.startswith("http"):
        return jsonify({"error": "url 参数缺失"}), 400

    data = stele.download_image(url)
    if not data:
        return jsonify({"error": "图片下载失败"}), 502
    try:
        png = finder.raster_to_transparent(data, size=size, mode=mode, invert=invert)
    except Exception as e:
        LOG.exception("去底失败: %s", e)
        return jsonify({"error": f"去底失败: {e}"}), 500
    return send_file(io.BytesIO(png), mimetype="image/png",
                     download_name=f"stele_{int(_now())}.png")


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/healthz")
def healthz():
    """健康检查端点，部署平台用来探活。"""
    return {"ok": True, "service": "calligraphy-finder", "version": "1.1"}


if __name__ == "__main__":
    # 本地开发：监听 127.0.0.1:5188
    # 生产环境请使用 gunicorn（见 Procfile / Dockerfile）
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5188"))
    app.run(host=host, port=port, debug=False)
