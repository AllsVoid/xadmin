#!/bin/bash

echo "=========================================="
echo "🚀 设置并启动 xadmin 前端"
echo "=========================================="
echo ""

cd /mnt/c/Users/kuntian/xadmin/xadmin/web

# 检查 package.json
if [ ! -f "package.json" ]; then
    echo "❌ 错误: package.json 不存在"
    exit 1
fi

echo "步骤 1/4: 清理旧依赖..."
rm -rf node_modules pnpm-lock.yaml package-lock.json .vite
echo "✅ 清理完成"
echo ""

echo "步骤 2/4: 安装依赖（约 3-5 分钟）..."
echo "⏳ 正在安装，请耐心等待..."
echo ""

# 尝试使用 npm 安装（对 Windows 文件系统更兼容）
npm install --legacy-peer-deps

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ npm 安装失败"
    echo ""
    echo "⚠️  由于 WSL 在 Windows 文件系统上的限制，建议："
    echo "   1. 将项目复制到 WSL 本地:"
    echo "      cp -r /mnt/c/Users/kuntian/xadmin/xadmin ~/xadmin_local"
    echo "      cd ~/xadmin_local/web"
    echo "      pnpm install && pnpm dev"
    echo ""
    exit 1
fi

echo ""
echo "✅ 依赖安装完成"
echo ""

echo "步骤 3/4: 检查关键依赖..."
if [ -f "node_modules/.bin/vite" ]; then
    echo "✅ vite 已安装"
else
    echo "❌ vite 未正确安装"
    exit 1
fi
echo ""

echo "步骤 4/4: 检查后端服务..."
if curl -s http://127.0.0.1:8000 > /dev/null 2>&1; then
    echo "✅ 后端服务运行中"
else
    echo "⚠️  警告: 后端服务未检测到"
    echo "   请确保后端已启动:"
    echo "   cd /mnt/c/Users/kuntian/xadmin/xadmin && ./start_xadmin.sh"
fi
echo ""

echo "=========================================="
echo "🎉 设置完成！正在启动前端..."
echo "=========================================="
echo ""
echo "访问地址: http://localhost:5173"
echo "登录信息: admin / admin123"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""
echo "=========================================="
echo ""

# 启动前端
npm run dev

