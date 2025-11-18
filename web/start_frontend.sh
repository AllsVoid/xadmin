#!/bin/bash

echo "=========================================="
echo "🎨 启动 xadmin 前端"
echo "=========================================="
echo ""

# 检查当前目录
if [ ! -f "package.json" ]; then
    echo "❌ 错误: 请在 web 目录运行此脚本"
    echo "   cd /mnt/c/Users/kuntian/xadmin/xadmin/web"
    exit 1
fi

# 检查 node_modules
if [ ! -d "node_modules" ] || [ ! -f "node_modules/.bin/vite" ]; then
    echo "📦 检测到依赖缺失，正在安装..."
    echo "   这可能需要 2-5 分钟，请耐心等待..."
    echo ""
    
    # 清理旧的依赖
    rm -rf node_modules pnpm-lock.yaml package-lock.json
    
    # 使用 pnpm 安装
    echo "使用 pnpm 安装依赖..."
    pnpm install --shamefully-hoist
    
    if [ $? -ne 0 ]; then
        echo ""
        echo "⚠️  pnpm 安装失败，尝试使用 npm..."
        npm install --legacy-peer-deps
        
        if [ $? -ne 0 ]; then
            echo "❌ 依赖安装失败，请检查网络连接"
            exit 1
        fi
        USE_NPM=1
    fi
    
    echo ""
    echo "✅ 依赖安装完成"
    echo ""
else
    echo "✅ 依赖已安装"
    echo ""
fi

# 检查后端服务
echo "🔍 检查后端服务..."
if curl -s http://127.0.0.1:8000 > /dev/null 2>&1; then
    echo "✅ 后端服务运行中"
else
    echo "⚠️  警告: 后端服务未检测到"
    echo ""
    echo "请确保后端已启动:"
    echo "  cd /mnt/c/Users/kuntian/xadmin/xadmin"
    echo "  ./start_xadmin.sh"
    echo ""
fi
echo ""

echo "=========================================="
echo "前端服务启动信息:"
echo ""
echo "  🌐 本地访问:"
echo "     - http://localhost:5173"
echo "     - http://127.0.0.1:5173"
echo ""
echo "  🔑 登录信息:"
echo "     - 用户名: admin"
echo "     - 密码: admin123"
echo ""
echo "  📤 新功能 - YAML 上传:"
echo "     - http://localhost:5173/#/system/testplan-yaml"
echo ""
echo "  📝 提示:"
echo "     - 首次加载可能需要 10-30 秒"
echo "     - 按 Ctrl+C 停止前端服务"
echo ""
echo "=========================================="
echo ""

# 启动前端
if [ "$USE_NPM" = "1" ]; then
    npm run dev
else
    pnpm dev
fi
