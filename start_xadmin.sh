#!/bin/bash

echo "=========================================="
echo "🚀 启动 xadmin 项目"
echo "=========================================="
echo ""

# 检查当前目录
if [ ! -f "manage.py" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    echo "   cd /mnt/c/Users/kuntian/xadmin/xadmin"
    exit 1
fi

# 1. 测试远程服务连接
echo "📡 步骤 1/3: 测试远程服务器连接..."
echo ""

# 测试 PostgreSQL
echo "  - PostgreSQL (10.67.167.53:5433)..."
if timeout 3 bash -c "cat < /dev/null > /dev/tcp/10.67.167.53/5433" 2>/dev/null; then
    echo "    ✅ 连接成功"
else
    echo "    ❌ 无法连接到远程 PostgreSQL"
    echo "    请检查远程服务器是否运行"
    exit 1
fi

# 测试 Redis
echo "  - Redis (10.67.167.53:6379)..."
if timeout 3 bash -c "cat < /dev/null > /dev/tcp/10.67.167.53/6379" 2>/dev/null; then
    echo "    ✅ 连接成功"
else
    echo "    ❌ 无法连接到远程 Redis"
    echo "    请检查远程服务器是否运行"
    exit 1
fi
echo ""

# 2. 检查 Python 依赖
echo "📦 步骤 2/3: 检查 Python 依赖..."
if python -c "import yaml" 2>/dev/null; then
    echo "✅ PyYAML 已安装"
else
    echo "⚠️  PyYAML 未安装，正在安装..."
    pip install pyyaml || uv add pyyaml
    echo "✅ PyYAML 安装完成"
fi
echo ""

# 3. 启动后端
echo "🎯 步骤 3/3: 启动后端服务..."
echo ""
echo "=========================================="
echo "后端服务启动信息："
echo ""
echo "  📍 本地地址:"
echo "     - http://127.0.0.1:8000"
echo "     - http://localhost:8000"
echo ""
echo "  📚 API 文档:"
echo "     - http://127.0.0.1:8000/system/docs"
echo ""
echo "  🗄️  远程数据库:"
echo "     - PostgreSQL: 10.67.167.53:5433"
echo "     - Redis: 10.67.167.53:6379"
echo ""
echo "  📝 日志文件:"
echo "     - logs/xadmin.log"
echo ""
echo "=========================================="
echo ""
echo "⚠️  请在另一个终端启动前端:"
echo "   cd /mnt/c/Users/kuntian/xadmin/xadmin/web"
echo "   ./start_frontend.sh"
echo ""
echo "按 Ctrl+C 停止后端服务"
echo ""
echo "=========================================="
echo ""

# 启动 Django 开发服务器
uv run python manage.py runserver 0.0.0.0:8000
