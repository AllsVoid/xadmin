#!/bin/bash

echo "=========================================="
echo "🔄 同步 xadmin 文件到 WSL"
echo "=========================================="
echo ""

SRC="/mnt/c/Users/kuntian/xadmin/xadmin"
DST="$HOME/xadmin_1111"

echo "源目录: $SRC"
echo "目标目录: $DST"
echo ""

# 1. 后端文件
echo "📦 同步后端文件..."
cp "$SRC/xadmin_auth/utils_yaml.py" "$DST/xadmin_auth/utils_yaml.py"
cp "$SRC/xadmin_auth/api_test_plan_yaml.py" "$DST/xadmin_auth/api_test_plan_yaml.py"
echo "✅ 后端文件已同步"
echo ""

# 2. 前端文件
echo "📦 同步前端文件..."
cp "$SRC/web/src/views/system/testplan-yaml/index.vue" "$DST/web/src/views/system/testplan-yaml/index.vue"
echo "✅ 前端文件已同步"
echo ""

echo "=========================================="
echo "✅ 所有文件已同步完成！"
echo "=========================================="
echo ""
echo "📝 更改内容："
echo "  1. ✅ 恢复机器数据到 5台"
echo "  2. ✅ 上传成功提示显示文件名"
echo "  3. ✅ Incompatible Machines 可折叠（默认收起）"
echo ""
echo "下一步："
echo "  - 后端会自动重载"
echo "  - 前端刷新浏览器即可"
echo ""

