# -*- coding: utf-8 -*-
"""生成《书法字体检索工具·Railway 部署操作手册》Word 文档"""
import os
from docx import Document
from docx.shared import Pt, RGBColor
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


def add_step(doc, idx, title, lines):
    """步骤区块：粗体标题 + 行内说明"""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(f"步骤 {idx}: {title}")
    set_font(run, "微软雅黑", 12, True, (0x1F, 0x4E, 0x79))
    for line in lines:
        bp = doc.add_paragraph()
        bp.paragraph_format.space_after = Pt(2)
        bp.paragraph_format.left_indent = Pt(18)
        r = bp.add_run(line)
        set_font(r, "微软雅黑", 10.5)


def add_table(doc, headers, rows):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        run = p.add_run(h)
        set_font(run, "微软雅黑", 10.5, True, (0x1F, 0x4E, 0x79))
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

    # 封面
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("书法字体检索工具 · Railway 部署操作手册")
    set_font(run, "微软雅黑", 20, True, (0x1F, 0x4E, 0x79))

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = sub.add_run("仓库: zzw409/calligraphy-finder    ·    部署平台: Railway.app    ·    2026-09-06")
    set_font(run, "微软雅黑", 10.5, False, (0x59, 0x59, 0x59))

    # 一、为什么选 Railway
    add_heading(doc, "一、为什么选 Railway")
    add_bullet(doc, "Docker 原生识别：Railway 自动检测仓库根目录的 Dockerfile，无需额外配置")
    add_bullet(doc, "启动快：通常 2-4 分钟完成首次部署")
    add_bullet(doc, "无冷启动：相比 Render 免费层的休眠，Railway 持续在线")
    add_bullet(doc, "免费试用：每月 $5 信用额度（Trial 计划），轻量服务足够跑很久")
    add_bullet(doc, "自动 HTTPS：部署完直接得到 https://xxx.up.railway.app 域名")
    add_bullet(doc, "GitHub 直连：每次 git push main 自动重新部署")

    add_para(doc, "对比 Render 免费层：", bold=True, indent=12)
    add_table(doc, ["维度", "Railway", "Render Free"], [
        ["月费", "Trial $5 信用", "$0"],
        ["冷启动", "无", "15 分钟无访问则休眠"],
        ["首屏", "< 1 秒", "首次访问需 30+ 秒唤醒"],
        ["部署速度", "2-4 分钟", "5-8 分钟"],
        ["自定义域名", "支持", "支持"],
        ["额度耗尽后", "需绑卡升级", "自动停服"],
    ])

    # 二、前置准备
    add_heading(doc, "二、前置准备（您已具备）")
    add_bullet(doc, "✅ GitHub 账号：zzw409")
    add_bullet(doc, "✅ 仓库已推送：https://github.com/zzw409/calligraphy-finder")
    add_bullet(doc, "✅ Dockerfile 已就位（含中文字体下载）")
    add_bullet(doc, "✅ requirements.txt 含 flask / requests / Pillow / resvg-py / gunicorn")
    add_bullet(doc, "✅ server.py 暴露 app = Flask(...) ，gunicorn 可直接调用")

    # 三、Railway 注册
    add_heading(doc, "三、注册并登录 Railway")
    add_step(doc, 1, "打开 Railway 官网", [
        "浏览器访问：https://railway.app/",
        "点击右上角 \"Login\"",
    ])
    add_step(doc, 2, "使用 GitHub 登录", [
        "在弹窗中选择 \"Login with GitHub\"",
        "授权 Railway 访问您的 GitHub 账号",
        "首次使用会要求填写项目名 + 选择 Hobby / Trial 计划",
        "Trial 计划无需绑卡，每月赠送 $5 信用额度",
    ])

    # 四、创建项目
    add_heading(doc, "四、创建项目并部署")
    add_step(doc, 1, "新建项目", [
        "登录后点击 \"New Project\"（或首页 \"+\" 号）",
        "选择 \"Deploy from GitHub repo\"",
    ])
    add_step(doc, 2, "选择仓库", [
        "在仓库列表中找到 \"zzw409/calligraphy-finder\"",
        "点击选中（首次需要点 \"Configure GitHub App\" 给 Railway 授权仓库访问）",
        "授权完成后回到此步选择仓库",
    ])
    add_step(doc, 3, "等待自动部署", [
        "Railway 检测到 Dockerfile 后自动开始构建",
        "构建日志实时显示在右侧 \"Build Logs\" 面板",
        "首次构建约 3-5 分钟（要下载中文字体和 Python 依赖）",
        "构建成功后自动进入运行状态",
    ])
    add_step(doc, 4, "生成公网域名", [
        "点击服务卡片进入详情页",
        "切换到 \"Settings\" 选项卡",
        "找到 \"Networking\" → \"Generate Domain\"",
        "Railway 会自动生成一个域名，形如：calligraphy-finder-production.up.railway.app",
        "这就是您的线上 URL（已自动配置 HTTPS）",
    ])

    # 五、验证部署
    add_heading(doc, "五、验证部署是否成功")
    add_para(doc, "本项目已正式部署上线，官方线上地址：", indent=12, bold=True, color=(0xC0, 0x39, 0x2B))
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run("🌐 https://calligraphy-finder-production.up.railway.app")
    set_font(run, "Consolas", 14, True, (0x1F, 0x4E, 0x79))

    add_para(doc, "实测验证结果（2026-09-06 13:27 已通过）：", indent=12, bold=True)
    add_table(doc, ["URL", "HTTP", "响应大小"], [
        ["https://calligraphy-finder-production.up.railway.app/healthz", "200 ✅", "59 bytes"],
        ["https://calligraphy-finder-production.up.railway.app/", "200 ✅", "28,260 bytes"],
        ["https://calligraphy-finder-production.up.railway.app/api/catalog", "200 ✅", "2,154 bytes"],
    ])

    add_para(doc, "也可以用 curl 验证：", indent=12, color=(0x59, 0x59, 0x59))
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Pt(24)
    run = p.add_run("curl https://calligraphy-finder-production.up.railway.app/healthz")
    set_font(run, "Consolas", 10, False, (0x1F, 0x4E, 0x79))

    # 六、域名自定义
    add_heading(doc, "六、（可选）绑定自定义域名")
    add_step(doc, 1, "添加域名", [
        "Settings → Networking → Custom Domain → 输入您的域名（如 shuzi.yourdomain.com）",
        "Railway 给出一个 CNAME 目标（形如 xxx.up.railway.app）",
    ])
    add_step(doc, 2, "DNS 配置", [
        "到您的域名注册商（阿里云/腾讯云/Cloudflare 等）",
        "添加 CNAME 记录：主机 shuzi → xxx.up.railway.app",
        "等待 DNS 生效（5-30 分钟）",
        "Railway 自动签发 Let's Encrypt SSL 证书",
    ])

    # 七、环境变量（如需调整）
    add_heading(doc, "七、（可选）环境变量调整")
    add_para(doc, "Railway 默认会注入 PORT 环境变量，server.py 已读取该变量。如需调整可手动设置：", indent=12)
    add_table(doc, ["变量", "默认值", "说明"], [
        ["PORT", "5188 (Dockerfile)", "HTTP 监听端口，Railway 会自动覆盖为它指定的端口"],
        ["PYTHONUNBUFFERED", "1", "Python 输出不缓冲，Docker 日志可实时看到"],
        ["TZ", "Asia/Shanghai", "时区设置为东八区"],
    ])
    add_para(doc, "修改方式：Settings → Variables → New Variable", indent=12)

    # 八、费用与监控
    add_heading(doc, "八、费用与监控")
    add_para(doc, "Trial 计划说明：", bold=True)
    add_bullet(doc, "每月 $5 信用额度（约等于 512MB RAM 实例跑 30 天 × 24 小时）")
    add_bullet(doc, "本项目（Flask + Pillow）轻量级，预计消耗 < $2/月")
    add_bullet(doc, "可升级到 Developer Plan（$5/月含 $5 信用），更稳定")
    add_para(doc, "查看用量：项目详情页 → Usage 选项卡可看本月已用", indent=12)

    # 九、常见问题排查
    add_heading(doc, "九、常见问题排查")
    add_table(doc, ["问题", "原因", "解决方案"], [
        ["构建失败：pip install 超时", "网络问题", "Settings → Variables 添加 PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple"],
        ["启动失败：gunicorn 找不到 app", "server.py 未暴露 app", "确认 server.py 第 27 行有 app = Flask(...)"],
        ["访问 502", "构建未完成", "等待 1-2 分钟，Railway 启动需要时间"],
        ["中文乱码", "容器缺中文字体", "Dockerfile 已装 fonts-noto-cjk，正常不会出问题"],
        ["碑帖检索超时", "shufazidian.com 网络慢", "在 server.py 增加 timeout，或加缓存层"],
    ])

    # 十、回滚与更新
    add_heading(doc, "十、回滚与更新")
    add_bullet(doc, "更新代码：本地修改后 git push origin main → Railway 自动重新部署")
    add_bullet(doc, "回滚：项目详情 → Deployments → 选历史版本 → \"Redeploy\"")
    add_bullet(doc, "删除服务：Settings → Danger → Delete Service")

    # 十一、链接汇总
    add_heading(doc, "十一、链接汇总")
    add_table(doc, ["类别", "URL"], [
        ["GitHub 仓库", "https://github.com/zzw409/calligraphy-finder"],
        ["Railway 仪表盘", "https://railway.app/dashboard"],
        ["Railway 文档", "https://docs.railway.app/"],
        ["Railway Dockerfile 指南", "https://docs.railway.app/build/dockerfile"],
        ["Railway 环境变量", "https://docs.railway.app/develop/variables"],
    ])

    # 十二、当前部署状态
    add_heading(doc, "十二、当前部署状态（v1.2 正式上线）")
    add_para(doc, "🎉 本项目已于 2026-09-06 13:27 正式上线！", bold=True, color=(0xC0, 0x39, 0x2B))
    add_para(doc, "线上地址：https://calligraphy-finder-production.up.railway.app", bold=True)

    add_table(doc, ["维度", "状态"], [
        ["Railway 部署", "✅ 运行中"],
        ["健康检查 /healthz", "✅ 200 OK"],
        ["首页 H5 页面 /", "✅ 28KB 正常渲染"],
        ["碑帖目录接口 /api/catalog", "✅ 2154 bytes"],
        ["Dockerfile 构建", "✅ 自动识别"],
        ["中文字体", "✅ 已装 fonts-noto-cjk"],
        ["HTTPS 证书", "✅ Railway 自动签发"],
    ])

    add_para(doc, "GitHub 仓库同步更新：")
    add_bullet(doc, "description: 输入内容→输出书法字图（透明PNG）：通用字形+碑帖拓片取字·线上版")
    add_bullet(doc, "homepage: https://calligraphy-finder-production.up.railway.app")
    add_bullet(doc, "topics: calligraphy, chinese-calligraphy, chinese-characters, flask, hanzi, ink, python, python-flask, stele-rubbing, transparent-png")

    out = os.path.join(BASE, "书法字体检索工具_Railway部署操作手册.docx")
    doc.save(out)
    print("OK ->", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()