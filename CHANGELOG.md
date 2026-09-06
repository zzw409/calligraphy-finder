# 更新日志 / Changelog

## v1.2 (2026-09-06)
### 新增 (feat)
- 🚀 **正式上线 Railway**：https://calligraphy-finder-production.up.railway.app
- ✅ 健康检查 `/healthz` 返回 200，首页 `/` 渲染正常，`/api/catalog` 正常返回碑帖目录
- 📦 新增 `railway.json` 显式声明构建方式与健康检查
- 📦 新增 `.railwayignore` 排除无关文件
- 📝 README 顶部新增"官方在线版"直达链接
- 📝 GitHub 仓库 homepage 已设置为线上 URL

### 修复 (fix)
- 修复 `build_deploy_doc.py` 表头背景色设置 API 错误
- 修复 `build_railway_doc.py` 中文引号导致 SyntaxError

## v1.1 (2026-09)
### 新增 (feat)
- 碑帖取字：调用 shufazidian.com，检索历代名家碑帖真迹拓片
- 智能去底：自动把拓片（黑底白字）转为透明背景深墨字
- 智能降级：碑帖无字时自动扩展到同作者 → 全字库
- 新增 `stele.py` 模块
- 新增 `/api/stele` 和 `/api/stele/img` 接口
- 新增常用碑帖推荐（颜/欧/柳/王/赵/米/黄/怀/张旭 等 20 组）
- 新增 /api/catalog 接口
- 前端 H5 新增碑帖取字区块
- Word 使用说明同步更新

## v1.0 (2026-09)
### 新增 (feat)
- 通用检索：汉典标准字形 + 本地多书法字体
- 整句合成（横排大图）
- 3 种本地字体渲染（simkai/simfang/simhei）+ 4 种开源书法字体（MaShanZheng/LongCang/LiuJianMaoCao/ZCOOLKuaiLe）
- 单字透明背景 PNG
- 基础 H5 界面
