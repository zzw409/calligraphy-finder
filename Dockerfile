FROM python:3.11-slim

# 容器内系统依赖（cairo / pango / libffi 用于 Pillow 与字体渲染）
RUN apt-get update && apt-get install -y --no-install-recommends \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf-2.0-0 \
        shared-mime-info \
        fonts-noto-cjk \
        fonts-noto-color-emoji \
        fonts-arphic-uming \
        fonts-arphic-ukai \
        ca-certificates \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先安装依赖（缓存利用）
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# 复制工程
COPY . .

# 自动下载开源书法字体到 fonts/ —— 部署环境也能渲染马善政/龙藏等
RUN mkdir -p fonts && \
    curl -fsSL -o fonts/MaShanZheng.ttf   https://github.com/google/fonts/raw/main/ofl/mashanzheng/MaShanZheng-Regular.ttf && \
    curl -fsSL -o fonts/LongCang.ttf      https://github.com/google/fonts/raw/main/ofl/longcang/LongCang-Regular.ttf && \
    curl -fsSL -o fonts/LiuJianMaoCao.ttf https://github.com/google/fonts/raw/main/ofl/liujianmaocao/LiuJianMaoCao-Regular.ttf && \
    curl -fsSL -o fonts/ZCOOLKuaiLe.ttf   https://github.com/google/fonts/raw/main/ofl/zcoolkuaile/ZCOOLKuaiLe-Regular.ttf || true

ENV PORT=5188 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Shanghai

EXPOSE 5188

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://127.0.0.1:${PORT}/healthz || exit 1

# 启动 gunicorn（生产 WSGI 服务器），2 worker，支持平滑扩展
CMD ["gunicorn", "--workers", "2", "--threads", "4", "--bind", "0.0.0.0:5188", "--access-logfile", "-", "server:app"]
