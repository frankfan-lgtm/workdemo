#!/bin/bash
# 即梦 AI 创作助手 - 一键初始化脚本
# 使用方法: curl -sL <url> | bash  或  bash setup.sh

set -e

PROJECT_DIR="${1:-$(pwd)/jimeng-search-agent}"

echo "🚀 创建项目目录: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"/{agent/search,static/css,static/js,templates}
cd "$PROJECT_DIR"

# --- .gitignore ---
cat > .gitignore << 'ENDFILE'
__pycache__/
*.pyc
.env
*.egg-info/
dist/
build/
.venv/
ENDFILE

# --- requirements.txt ---
cat > requirements.txt << 'ENDFILE'
fastapi==0.115.6
uvicorn==0.34.0
jinja2==3.1.4
python-multipart==0.0.18
httpx==0.28.1
pydantic==2.10.4
python-dotenv==1.0.1
ENDFILE

# --- .env ---
cat > .env << 'ENDFILE'
ARK_API_KEY=94090db7-6585-460e-a8ff-7830c1516624
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
ARK_MODEL=deepseek-v3-2-251201
ENDFILE

echo "📦 安装依赖..."
pip3 install -r requirements.txt

echo ""
echo "✅ 项目初始化完成！"
echo "   cd $PROJECT_DIR"
echo "   python3 app.py"
echo "   然后浏览器打开 http://localhost:8000"
