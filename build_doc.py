# -*- coding: utf-8 -*-
"""生成《书法字体检索工具·使用说明》Word 文档（含碑帖取字）"""
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

BASE = os.path.dirname(os.path.abspath(__file__))


def set_font(run, name="微软雅黑", size=11, bold=False, color=None):
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    if color:
        run.font.color.rgb = RGBColor(*color)
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:eastAsia"), name)


def add_heading(doc, text, size=15):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    set_font(run, "微软雅黑", size, True, (0x1A, 0x1A, 0x1A))
    return p


def add_para(doc, text, size=11, bold=False, color=None, indent=0):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    if indent:
        p.paragraph_format.left_indent = Pt(indent)
    run = p.add_run(text)
    set_font(run, "微软雅黑", size, bold, color)
    return p


def add_bullet(doc, text, size=10.5):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    set_font(run, "微软雅黑", size)
    return p


def add_image_center(doc, path, width_in, caption=None):
    if not os.path.exists(path):
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run()
    run.add_picture(path, width=Inches(width_in))
    if caption:
        add_caption(doc, caption)


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(10)
    run = p.add_run(text)
    set_font(run, "微软雅黑", 9, False, (0x88, 0x66, 0x44))


def add_table(doc, header, rows):
    table = doc.add_table(rows=1, cols=len(header))
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = table.rows[0].cells[i]
        c.text = ""
        c.paragraphs[0].add_run(h).bold = True
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            cells[i].paragraphs[0].add_run(val)
    for row in table.rows:
        for cell in row.cells:
            for par in cell.paragraphs:
                for rr in par.runs:
                    set_font(rr, "微软雅黑", 10)


doc = Document()
sec = doc.sections[0]
sec.page_height = Inches(11.69)
sec.page_width = Inches(8.27)
sec.left_margin = Inches(0.9)
sec.right_margin = Inches(0.9)
sec.top_margin = Inches(0.9)
sec.bottom_margin = Inches(0.9)

# ===== 封面 =====
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title.paragraph_format.space_before = Pt(18)
title.paragraph_format.space_after = Pt(6)
run = title.add_run("书法字体检索工具")
set_font(run, "微软雅黑", 26, True, (0x1A, 0x1A, 0x1A))

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub.paragraph_format.space_after = Pt(16)
run = sub.add_run("输入内容 → 检索内容 → 输出书法文字 PNG")
set_font(run, "微软雅黑", 13, False, (0xB3, 0x32, 0x2A))

# ===== 一、功能概述 =====
add_heading(doc, "一、功能概述")
add_para(doc, "本工具用于快速检索汉字书法字形，并导出带透明背景的单字 PNG。用户输入文字（单字、词组或整句）后：")
add_bullet(doc, "通用检索：拉取汉典标准字形 + 多套开源书法字体渲染，得到多种书体效果。")
add_bullet(doc, "碑帖取字（新增）：从指定书法家 / 碑帖的历代真迹拓片中取出对应单字，自动去除深色背景，得到透明 PNG。")
add_bullet(doc, "整句合成：把整句文字横向拼成一张书法图。")

# ===== 二、启动与界面 =====
add_heading(doc, "二、启动与界面")
add_para(doc, "1. 启动服务（项目目录下）：", bold=True)
p = doc.add_paragraph(); p.paragraph_format.left_indent = Pt(20)
run = p.add_run("python server.py"); set_font(run, "Consolas", 11, True, (0x11, 0x44, 0x88))
add_para(doc, "2. 浏览器打开：")
p = doc.add_paragraph(); p.paragraph_format.left_indent = Pt(20)
run = p.add_run("http://127.0.0.1:5188/"); set_font(run, "Consolas", 11, True, (0x11, 0x44, 0x88))
add_para(doc, "3. 输入文字，点击【检索】（通用）或【取字】（碑帖）。")
add_para(doc, "界面包含两个区：", bold=True)
add_bullet(doc, "上部「通用检索」：输入 + 书体勾选 + 整句预览 + 多书体结果卡片。")
add_bullet(doc, "下部「碑帖取字」：书体下拉 + 书法家 / 碑帖筛选 + 常用碑帖快捷选择 + 真迹结果。")

# ===== 三、碑帖取字（重点） =====
add_heading(doc, "三、碑帖取字（特色功能）")
add_para(doc, "这是从历代名家真迹拓片中直接取字的入口，结果带「朝代 · 书法家 · 碑帖」出处，适合用于招牌、印章、题字等需要名家笔意的场景。")
add_para(doc, "操作步骤：", bold=True)
add_bullet(doc, "选择书法类目：楷书 / 行书 / 草书 / 隶书 / 篆书 / 章草 / 魏碑 / 简牍。")
add_bullet(doc, "（可选）填书法家或碑帖名，或点下方「常用碑帖」快速选中，如颜真卿·多宝塔碑、王羲之·兰亭序。")
add_bullet(doc, "输入要取的字，点【取字】。")
add_bullet(doc, "每个字展示该碑帖下所有真迹，支持「原图」与「透明 PNG」下载，点击可放大。")
add_para(doc, "说明：若指定碑帖中没有某字（如《多宝塔碑》无「寿」字），工具会自动放宽检索范围，并在卡片提示“已扩展检索”。")

add_para(doc, "示例：楷书 · 颜真卿《多宝塔碑》取「福」字（拓片自动去底转透明 PNG）：")
add_image_center(doc, os.path.join(BASE, "demo", "福_多宝塔碑_去底透明.png"), 1.4,
                 caption="颜真卿《多宝塔碑》「福」字 · 已去底为透明PNG")

# ===== 四、通用检索示例 =====
add_heading(doc, "四、通用检索示例")
add_para(doc, "输入【福】，得到多种书体：")
add_image_center(doc, os.path.join(BASE, "demo", "福_mashanzheng.png"), 0.8)
add_image_center(doc, os.path.join(BASE, "demo", "福_longcang.png"), 0.8)
add_caption(doc, "左：马善政（行楷）　右：龙藏（草书）　—— 均为透明背景PNG")
add_para(doc, "输入【永存大志】，整句自动生成：")
add_image_center(doc, os.path.join(BASE, "demo", "phrase_永存大志.png"), 6.0,
                 caption="整句图「永存大志」（马善政行楷，透明背景）")

# ===== 五、支持书体 =====
add_heading(doc, "五、支持的书体")
add_table(doc, ["来源", "标识", "说明"], [
    ("马善政", "mashanzheng", "行楷，潇洒流畅，适合标题"),
    ("龙藏", "longcang", "草书，飘逸灵动"),
    ("刘建毛草", "liujianmaocao", "狂草，气势奔放"),
    ("站酷快乐体", "zcoolkuaile", "楷意手写，活泼现代"),
    ("系统楷体", "simkai", "规范端正，通用"),
    ("系统仿宋", "simfang", "典雅印刷体"),
    ("系统黑体", "simhei", "简洁现代"),
    ("汉典楷书(5地)", "zdic kai", "大陆/香港/台湾/日本/韩国标准矢量字形"),
    ("碑帖真迹", "stele", "名家拓片取字（楷/行/草/隶/篆/章草/魏碑/简牍）"),
])

# ===== 六、接口 =====
add_heading(doc, "六、常用接口（供二次开发）")
add_table(doc, ["接口", "说明"], [
    ("POST /api/search", "输入 {text, presets, size}，返回每字符多书体 base64 图像"),
    ("POST /api/phrase", "输入 {text, preset, size, gap}，返回整句横排 PNG"),
    ("POST /api/stele", "输入 {text, styles, author, book, limit}，按碑帖/作者检索真迹"),
    ("GET  /api/stele/img", "参数 url, mode, size, invert；下载拓片并去底转透明PNG"),
    ("GET  /api/catalog", "返回全部预设书体、碑帖书体、常用碑帖列表"),
    ("GET  /", "浏览器 H5 界面"),
])

# ===== 七、文件结构 =====
add_heading(doc, "七、文件结构与依赖")
files = [
    ("finder.py", "核心检索/渲染（汉典抓取 + 本地字体渲染 + 整句合成 + 去底透明）"),
    ("stele.py",  "碑帖/作者真迹检索（shufazidian 解析 + 下载）"),
    ("server.py", "Flask 后端，提供全部 HTTP 接口"),
    ("templates/index.html", "浏览器交互界面（H5）"),
    ("fonts/",    "开源书法字体（MaShanZheng/LongCang/LiuJianMaoCao/ZCOOLKuaiLe）"),
    ("cache/",    "临时图片缓存（自动创建）"),
]
for fname, desc in files:
    add_bullet(doc, f"{fname} —— {desc}")
add_para(doc, "运行依赖：Python 3.13、flask、requests、Pillow、resvg-py（可选）。")

# ===== 八、重要说明 =====
add_heading(doc, "八、重要说明")
add_bullet(doc, "单字 PNG 为透明背景，可直接嵌入海报、PPT、Word、宣传册、招牌等场景。")
add_bullet(doc, "汉典在线字形为矢量 SVG；离线时自动回退到本地开源字体渲染，保证始终可用。")
add_bullet(doc, "碑帖真迹为历代名家拓片，版权归属原典藏机构/作者；供个人学习、研究及非商业用途参考，商用请自行确认授权。")
add_bullet(doc, "检索结果缓存 7 天，重复检索同一文字显著提速。")

doc.save(os.path.join(BASE, "书法字体检索工具_使用说明.docx"))
print("已生成：", os.path.join(BASE, "书法字体检索工具_使用说明.docx"))
