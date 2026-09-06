# -*- coding: utf-8 -*-
"""生成《书法字体检索工具·云端部署说明》Word 文档"""
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


def add_code(doc, text, size=10):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.left_indent = Pt(12)
    run = p.add_run(text)
    set_font(run, "Consolas", size, False, (0x1F, 0x4E, 0x79))
    return p


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        run = p.add_run(h)
        set_font(run, "微软雅黑", 10.5, True, (0xFF, 0xFF, 0xFF))
    for ri, row in enumerate(rows):
        for ci, cell in enumerate(row):
            c = table.rows[1 + ri].cells[ci]
            c.text = ""
            p = c.paragraphs[0]
            run = p.add_run(str(cell))
            set_font(run, "微软雅黑", 10)
    return table


def main():
    doc = Document()
    # 标题
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("书法字体检索工具 · 云端部署与 GitHub 上线说明")
    set_font(run, "微软雅黑", 20, True, (0x1F, 0x4E, 0x79))

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = sub.add_run("GitHub 仓库: zzw409/calligraphy-finder    ·    2026-09-06")
    set_font(run, "微软雅黑", 10.5, False, (0x59, 0x59, 0x59))

    # 1. 项目状态
    add_heading(doc, "一、项目概览")
    add_para(doc, "本项目已完整上传至 GitHub 仓库，并配置好一键云端部署所需的所有文件。")
    add_bullet(doc, "仓库地址: https://github.com/zzw409/calligraphy-finder")
    add_bullet(doc, "本地源码目录: C:\\Users\\Administrator\\WorkBuddy\\2026-09-06-09-01-11\\calligraphy_finder")
    add_bullet(doc, "代码总量: Python 后端 ~31KB（server.py / finder.py / stele.py / build_doc.py）")
    add_bullet(doc, "核心能力: 通用字形检索 + 碑帖拓片取字，输出 PNG/SVG")

    # 2. 仓库结构
    add_heading(doc, "二、GitHub 仓库结构")
    add_table(doc, ["文件 / 目录", "类型", "作用"], [
        ["Dockerfile", "部署", "python:3.11-slim + 中文字体 + gunicorn"],
        ["render.yaml", "部署", "Render.com Blueprint 自动识别（免费层）"],
        ["Procfile", "部署", "Heroku/Railway 兼容入口"],
        ["runtime.txt", "部署", "Python 版本声明 3.11.9"],
        [".dockerignore", "部署", "排除缓存/字体/Demo"],
        ["server.py", "源码", "Flask 后端 (PORT=5188)"],
        ["finder.py", "源码", "字形渲染 + 在线/本地双路检索"],
        ["stele.py", "源码", "碑帖拓片取字引擎"],
        ["templates/index.html", "源码", "H5 前端"],
        ["build_doc.py", "工具", "Word 文档生成器"],
        ["requirements.txt", "依赖", "flask / requests / Pillow / resvg-py"],
        ["README.md", "文档", "GitHub 友好版项目说明"],
        ["LICENSE", "文档", "MIT 许可证"],
        ["CHANGELOG.md", "文档", "版本更新日志 v1.0 / v1.1"],
        ["GITHUB_SETUP.md", "文档", "GitHub 部署指引"],
        ["fonts/", "资源", "字体目录（README 占位，运行时下载）"],
        ["demo/", "资源", "示例字图"],
    ])

    # 3. 三种部署方式
    add_heading(doc, "三、三种部署方式对比")
    add_table(doc, ["平台", "费用", "难度", "部署时长", "URL"], [
        ["Render.com", "免费（512MB, 冷启动慢）", "★", "5 分钟", "https://render.com"],
        ["Railway.app", "$5/月试用额度", "★★", "8 分钟", "https://railway.app"],
        ["自建服务器", "已有机器则 0 元", "★★★", "20 分钟", "本地 IP:5188"],
    ])
    add_para(doc, "推荐: Render.com — 仓库自带 render.yaml，点几下鼠标即上线。", bold=True, color=(0xC0, 0x39, 0x2B))

    # 4. Render 部署步骤
    add_heading(doc, "四、Render.com 部署步骤（推荐）")
    add_bullet(doc, "访问 https://dashboard.render.com/ 并用 GitHub 账号登录")
    add_bullet(doc, "点击 New + → Blueprint")
    add_bullet(doc, "Select repo: zzw409/calligraphy-finder")
    add_bullet(doc, "Render 自动识别仓库根目录的 render.yaml，确认后 Apply")
    add_bullet(doc, "等待 5-8 分钟，首次构建会下载字体（Kaishu/Songti/Xingkai）")
    add_bullet(doc, "部署完成后控制台会显示 *.onrender.com 域名，即为线上 URL")

    add_para(doc, "render.yaml 配置预览:", indent=12)
    add_code(doc, "services:\n  - type: web\n    name: calligraphy-finder\n    runtime: python\n    plan: free\n    buildCommand: pip install -r requirements.txt\n    startCommand: gunicorn -b 0.0.0.0:$PORT server:app\n    envVars:\n      - key: PORT\n        value: 5188")

    # 5. Railway 部署步骤
    add_heading(doc, "五、Railway.app 部署步骤")
    add_bullet(doc, "访问 https://railway.app/ 并用 GitHub 登录")
    add_bullet(doc, "New Project → Deploy from GitHub repo → 选 zzw409/calligraphy-finder")
    add_bullet(doc, "Railway 自动检测 Dockerfile 并构建")
    add_bullet(doc, "Settings → Generate Domain 得到线上 URL")

    # 6. Git 推送命令（备用）
    add_heading(doc, "六、备用：本地 Git 推送命令")
    add_para(doc, "若日后想用本地 git 直接推送（需要 token 含 workflow scope 才能传 CI 文件）：", indent=12)
    add_code(doc, "cd C:\\Users\\Administrator\\WorkBuddy\\2026-09-06-09-01-11\\calligraphy_finder\n"
                 "git init -b main\n"
                 "git config user.email \"you@example.com\"\n"
                 "git config user.name \"Your Name\"\n"
                 "git add -A\n"
                 "git commit -m \"deploy: add all sources with cloud deployment files\"\n"
                 "git remote add origin https://<TOKEN>@github.com/zzw409/calligraphy-finder.git\n"
                 "git push -u origin main --force")

    # 7. 本地启动命令
    add_heading(doc, "七、本地启动命令（开发调试用）")
    add_code(doc, "cd C:\\Users\\Administrator\\WorkBuddy\\2026-09-06-09-01-11\\calligraphy_finder\n"
                 "C:\\Users\\Administrator\\.workbuddy\\binaries\\python\\envs\\default\\Scripts\\python.exe server.py\n"
                 "# 浏览器访问 http://127.0.0.1:5188/")

    # 8. API 接口一览
    add_heading(doc, "八、API 接口一览")
    add_table(doc, ["方法", "路径", "参数", "作用"], [
        ["GET", "/", "—", "前端 H5 页面"],
        ["GET", "/healthz", "—", "健康检查"],
        ["GET", "/api/catalog", "—", "碑帖/作者目录"],
        ["POST", "/api/search", "{text, style, font, size, color}", "通用字形检索，返回 PNG"],
        ["POST", "/api/phrase", "{text, style, ...}", "词组检索（返回多字组合）"],
        ["POST", "/api/stele", "{book, author, char, style}", "碑帖取字（拓片字形）"],
        ["GET", "/api/stele/img", "book/author/char/style", "单字直链 PNG"],
    ])

    # 9. CI 状态说明
    add_heading(doc, "九、GitHub Actions CI 状态")
    add_para(doc, "本地 .github/workflows/test.yml 已配置，但因当前 PAT 缺少 workflow scope，无法通过 API 推送到 GitHub。", color=(0xC0, 0x39, 0x2B))
    add_para(doc, "解决方案：")
    add_bullet(doc, "方案 A: 重新生成 PAT，勾选 workflow scope 后推一次")
    add_bullet(doc, "方案 B: 在 GitHub 网页端手动上传 .github/workflows/test.yml 文件")
    add_bullet(doc, "方案 C: 直接忽略 CI 文件，Render 会基于 Dockerfile 直接构建，不依赖 workflow")

    # 10. 链接汇总
    add_heading(doc, "十、全部链接汇总")
    add_table(doc, ["类别", "URL"], [
        ["GitHub 仓库", "https://github.com/zzw409/calligraphy-finder"],
        ["README", "https://github.com/zzw409/calligraphy-finder/blob/main/README.md"],
        ["CHANGELOG", "https://github.com/zzw409/calligraphy-finder/blob/main/CHANGELOG.md"],
        ["LICENSE", "https://github.com/zzw409/calligraphy-finder/blob/main/LICENSE"],
        ["GITHUB_SETUP", "https://github.com/zzw409/calligraphy-finder/blob/main/GITHUB_SETUP.md"],
        ["Render 仪表盘", "https://dashboard.render.com/"],
        ["Railway 仪表盘", "https://railway.app/dashboard"],
        ["GitHub Settings (Token)", "https://github.com/settings/tokens"],
    ])

    # 11. 当前关键 SHA
    add_heading(doc, "十一、当前部署状态（v1.2 正式上线）")
    add_para(doc, "🎉 项目已于 2026-09-06 13:27 部署到 Railway！", bold=True, color=(0xC0, 0x39, 0x2B))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run("🌐 https://calligraphy-finder-production.up.railway.app")
    set_font(run, "Consolas", 14, True, (0x1F, 0x4E, 0x79))

    add_para(doc, "验证结果（已通过）：", bold=True)
    add_table(doc, ["端点", "HTTP", "响应"], [
        ["/healthz", "200 ✅", "59 bytes"],
        ["/", "200 ✅", "28,260 bytes"],
        ["/api/catalog", "200 ✅", "2,154 bytes"],
    ])

    add_para(doc, "main 分支最新提交: 6e9d528（deploy: add railway.json for explicit Railway config）")
    add_para(doc, "仓库描述: 输入内容→输出书法字图（透明PNG）：通用字形+碑帖拓片取字·线上版: calligraphy-finder-production.up.railway.app")
    add_para(doc, "仓库 Topics: calligraphy, chinese-calligraphy, chinese-characters, flask, hanzi, ink, python, python-flask, stele-rubbing, transparent-png")
    add_para(doc, "Homepage: https://calligraphy-finder-production.up.railway.app")
    add_para(doc, "License: MIT")

    out = os.path.join(BASE, "书法字体检索工具_云端部署说明.docx")
    doc.save(out)
    print("OK ->", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()