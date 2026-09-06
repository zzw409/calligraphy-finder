# 书法字体检索工具 · Calligraphy Finder

> 输入汉字 → 检索多体书法字图 → 输出**透明背景 PNG**；
> 支持从**历代名家碑帖真迹**（颜真卿、欧阳询、王羲之、柳公权…）取字。

[![Repo](https://img.shields.io/badge/repo-zzw409/calligraphy--finder-181717?style=flat-square&logo=github)](https://github.com/zzw409/calligraphy-finder)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Deploy to Render](https://img.shields.io/badge/deploy-render-46E3B7?style=flat-square&logo=render&logoColor=white)](https://render.com/deploy?repo=https://github.com/zzw409/calligraphy-finder)
[![Deploy to Railway](https://img.shields.io/badge/deploy-railway-0B0D0D?style=flat-square&logo=railway&logoColor=white)](https://railway.app/new/template?template=https://github.com/zzw409/calligraphy-finder)

---

## 📌 直达链接（点开就用）

> 🔗 **GitHub 仓库**：<https://github.com/zzw409/calligraphy-finder>
>
> 🚀 **一键部署到 Render**：<https://render.com/deploy?repo=https://github.com/zzw409/calligraphy-finder>
>
> 📥 **克隆命令**：
> ```bash
> git clone https://github.com/zzw409/calligraphy-finder.git
> cd calligraphy-finder
> ```
>
> 💡 **在线访问**：上面"一键部署"按钮点进去 → render.com 自动识别 `render.yaml` → 选择 free plan → 等 2 分钟即可获得 `https://calligraphy-finder.onrender.com` 的公开网址，无需信用卡。

---

## ✨ 功能一览

| 模块 | 说明 |
|---|---|
| 🔍 **通用检索** | 输入任意汉字 → 调用汉典标准字形 + 本地 7 种开源字体 → **12+** 种书体的单字透明 PNG |
| 🪨 **碑帖取字** | 输入字 + 选择书法家/碑帖 → 从历代真迹拓片中取字 → **自动去底**得到透明 PNG |
| 🖼 **整句合成** | 输入整句话 → 拼成横排大图（适合标题、题字） |
| 📦 **多书体** | 楷/行/草/隶/篆/章草/魏碑/简牍 共 8 类 + 5 地异体（大陆/港/台/日/韩） |
| 🏛 **常用碑帖** | 内置 20 组（颜真卿·多宝塔碑、欧·九成宫、柳·玄秘塔碑、王·兰亭序、赵·胆巴碑…） |

## 🚀 快速开始（3 步）

### 第 1 步：下载 4 个开源书法字体

字体不进入 git（避免 5MB×4 大文件），首次启动前手动下载：

```powershell
# Windows PowerShell
cd fonts
curl.exe -L -o MaShanZheng.ttf   "https://github.com/google/fonts/raw/main/ofl/mashanzheng/MaShanZheng-Regular.ttf"
curl.exe -L -o LongCang.ttf      "https://github.com/google/fonts/raw/main/ofl/longcang/LongCang-Regular.ttf"
curl.exe -L -o LiuJianMaoCao.ttf "https://github.com/google/fonts/raw/main/ofl/liujianmaocao/LiuJianMaoCao-Regular.ttf"
curl.exe -L -o ZCOOLKuaiLe.ttf   "https://github.com/google/fonts/raw/main/ofl/zcoolkuaile/ZCOOLKuaiLe-Regular.ttf"
```

或者让 `fonts/README.md` 的脚本一次跑完。

### 第 2 步：安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 第 3 步：启动

```bash
python server.py
```

然后浏览器访问：

```
http://127.0.0.1:5188/
```

> 全程只用浏览器，**不需要联网**也能跑（本地字体 + 汉典已缓存即可）。碑帖取字需要联网以调用 shufazidian.com。

---

## 🌐 在浏览器里看到的样子

页面分两大区块：

1. **通用检索**：上半部分，输入文字 → 多书体卡片 / 下载 PNG / 整句合成预览。
2. **碑帖取字**：下半部分，选择书体（楷书/行书/草书…）→ 选书法家/碑帖（可点常用）→ 一键导出真迹透明 PNG。

*左侧示例是颜真卿《多宝塔碑》的「福」字，右侧是马善政行楷「福」字，均为去底透明 PNG。*

---

## 📁 项目结构

```
calligraphy-finder/
├── server.py                              # Flask 后端入口（端口 5188）
├── finder.py                              # 通用检索、整句合成、拓片去底
├── stele.py                               # 碑帖/作者真迹检索与下载
├── build_doc.py                           # 一键重新生成 Word 使用说明
├── templates/
│   └── index.html                         # 浏览器界面（单文件 H5）
├── fonts/
│   ├── README.md                          # 字体一键下载说明
│   ├── MaShanZheng.ttf                    # （按需下载）
│   ├── LongCang.ttf                       #
│   ├── LiuJianMaoCao.ttf                  #
│   └── ZCOOLKuaiLe.ttf                    #
├── demo/                                  # 演示效果图
├── cache/                                 # 临时图片缓存（已 .gitignore）
├── requirements.txt
├── README.md                              # ⬅ 本文件
├── GITHUB_SETUP.md                        # 把仓库同步到 GitHub 的步骤
└── 书法字体检索工具_使用说明.docx            # 完整 Word 说明
```

---

## 🛰 数据来源

| 来源 | 用途 | 备注 |
|---|---|---|
| [汉典 zdic.net](https://www.zdic.net/) | 标准楷书矢量字形（5 地异体） | 走 `img.zdic.net/kai/...` 直链，可靠 |
| [书法字典 shufazidian.com](http://www.shufazidian.com/) | 名家碑帖真迹拓片 | 通过 `POST s.php` 接口 |
| [Google Fonts 开源字体](https://fonts.google.com/) | 马善政/龙藏/刘建毛草/站酷快乐体 | OFL 1.1 协议 |
| 系统字体（simkai/simfang/simhei） | 本地兜底 | 仅 Windows |

---

## 📚 接口文档（供二次开发）

启动后访问 `http://127.0.0.1:5188/api/...`

| 方法 | 路径 | 说明 |
|---|---|---|
| `POST` | `/api/search` | 输入 `{text, presets, size}` → 返回每字多书体 base64 图像 |
| `POST` | `/api/phrase` | 输入 `{text, preset, size, gap}` → 返回整句横排 PNG |
| `POST` | `/api/stele` | 输入 `{text, styles, author, book, limit}` → 返回碑帖真迹列表 |
| `GET`  | `/api/stele/img?url=&mode=&size=` | 下载拓片并去底转透明 PNG |
| `GET`  | `/api/catalog` | 返回书体预设、碑帖书体、常用碑帖列表 |
| `GET`  | `/` | H5 界面 |

请求示例：

```bash
curl -X POST http://127.0.0.1:5188/api/search \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"福寿康宁\",\"presets\":[\"mashanzheng\",\"longcang\"]}"

curl -X POST http://127.0.0.1:5188/api/stele \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"福寿\",\"styles\":[\"kaishu\"],\"book\":\"多宝塔碑\"}"
```

详细接口说明见 `书法字体检索工具_使用说明.docx`。

---

## 🌍 一键部署到云端

本项目已自带 `Dockerfile` / `render.yaml` / `Procfile`，可一键部署到任何支持 Docker 或 Python 的 PaaS 平台。

### 🟢 Render（推荐 · 免费 · 免信用卡）

> **最快路径**：点击本页顶部 **"Deploy to Render"** 徽章 → Render 登录 → 选 free plan → 等约 2 分钟 → 拿到形如 `https://calligraphy-finder.onrender.com` 的公开地址。

或者手动：
1. 注册 https://render.com（GitHub 一键登录）
2. New + → Blueprint → 选本仓库
3. Render 自动读取 `render.yaml`，点 Apply
4. 完成！默认免费 tier，自带 HTTPS

### 🚂 Railway（同样免费起步）

点击本页顶部 **"Deploy to Railway"** 徽章，或：
1. 登录 https://railway.app
2. New Project → Deploy from GitHub repo → 选 `calligraphy-finder`
3. Railway 自动识别 `Procfile`
4. 部署完成后点 → Generate Domain

### 🐳 自己跑 Docker

```bash
docker build -t calligraphy-finder .
docker run -p 5188:5188 calligraphy-finder
# 浏览器打开 http://localhost:5188
```

### 🐍 自己的 VPS

```bash
git clone https://github.com/zzw409/calligraphy-finder.git
cd calligraphy-finder
pip install -r requirements.txt gunicorn

# 开发
python server.py                     # http://127.0.0.1:5188

# 生产
gunicorn --workers 2 --threads 4 --bind 0.0.0.0:5188 server:app
# 然后用 nginx / caddy 反向代理到 443，加 HTTPS
```

---

## 🐳 CI / 持续集成

每次 push / PR 到 main，会自动跑两条检查（见 `.github/workflows/test.yml`）：

- ✅ Python 语法检查 + 模块 import
- ✅ 实际启动 server.py，访问 `/healthz` 验证健康

打开 https://github.com/zzw409/calligraphy-finder/actions 即可看到绿色 ✓ 徽章（成功后会自动出现在 README 上方）。

---

## 📝 版权与许可

- **代码**：MIT License
- **字体**：Google Fonts 项目下的开源中文字体（OFL 1.1）—— 个人学习、商业使用皆可
- **碑帖拓片**：来源为 shufazidian.com 聚合站点，原版权归原作者与典藏机构 —— 商业用途请自行确认授权
- **汉典字形**：仅作学习参考

## 🆙 更新日志

- **v1.1**：碑帖取字（shufazidian 真迹 + 智能去底）
- **v1.0**：通用检索（汉典标准字形 + 本地多字体渲染 + 整句合成）

---

📮 **Issue / 反馈**：[https://github.com/zzw409/calligraphy-finder/issues](https://github.com/zzw409/calligraphy-finder/issues)
⭐ **Star** 一颗，欢迎贡献 ✨
