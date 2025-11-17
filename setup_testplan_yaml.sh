#!/bin/bash

echo "=========================================="
echo "🚀 测试计划 YAML 功能安装脚本"
echo "=========================================="
echo ""

# 1. 安装 Python 依赖
echo "📦 步骤 1/3: 安装 Python 依赖..."
pip install pyyaml || {
    echo "⚠️  pip 安装失败，尝试使用 uv..."
    uv add pyyaml
}
echo "✅ Python 依赖安装完成"
echo ""

# 2. 运行数据库迁移
echo "🗄️  步骤 2/3: 运行数据库迁移..."
uv run python manage.py makemigrations xadmin_db
if [ $? -eq 0 ]; then
    echo "✅ 迁移文件生成成功"
    uv run python manage.py migrate
    if [ $? -eq 0 ]; then
        echo "✅ 数据库迁移完成"
    else
        echo "❌ 数据库迁移失败"
        echo "请手动执行: uv run python manage.py migrate"
        exit 1
    fi
else
    echo "⚠️  迁移文件生成失败"
    echo "如果模型已存在，可以忽略此错误"
fi
echo ""

# 3. 安装前端依赖
echo "🎨 步骤 3/3: 检查前端依赖..."
cd web
if [ -d "node_modules" ]; then
    echo "✅ 前端依赖已安装"
else
    echo "📦 安装前端依赖..."
    pnpm install
    echo "✅ 前端依赖安装完成"
fi
cd ..
echo ""

echo "=========================================="
echo "✅ 安装完成！"
echo "=========================================="
echo ""
echo "📝 接下来的步骤："
echo ""
echo "1️⃣  启动后端服务："
echo "   cd ~/xadmin"
echo "   uv run python manage.py runserver 0.0.0.0:8000"
echo ""
echo "2️⃣  启动前端服务（新终端）："
echo "   cd ~/xadmin/web"
echo "   pnpm dev"
echo ""
echo "3️⃣  访问页面："
echo "   http://localhost:5173"
echo ""
echo "4️⃣  在系统管理菜单中添加："
echo "   菜单名称: Upload Test Plan"
echo "   路由路径: /system/testplan-yaml"
echo ""
echo "📖 详细文档请查看: TESTPLAN_YAML_INTEGRATION.md"
echo ""
echo "=========================================="

