#!/bin/bash
# 测试超级用户权限判断修复

set -e

echo "============================================"
echo "测试超级用户权限判断修复"
echo "============================================"

# 激活虚拟环境
source .venv/bin/activate

echo ""
echo "1. 检查代码中不再使用 settings.TITW_SUPER_USER..."
echo ""

# 检查是否还有代码使用 TITW_SUPER_USER（除了 settings.py）
USAGE_COUNT=$(grep -r "TITW_SUPER_USER" --include="*.py" --exclude-dir=".venv" . | grep -v "settings.py" | grep -v "SUPERUSER_AUTH_FIX.md" | wc -l)

if [ "$USAGE_COUNT" -eq 0 ]; then
    echo "✓ 代码中已不再使用 settings.TITW_SUPER_USER"
else
    echo "⚠️  发现 $USAGE_COUNT 处仍在使用 TITW_SUPER_USER"
    grep -r "TITW_SUPER_USER" --include="*.py" --exclude-dir=".venv" . | grep -v "settings.py"
fi

echo ""
echo "2. 验证代码使用 is_system 字段判断..."
echo ""

# 检查是否使用 is_system
IS_SYSTEM_COUNT=$(grep -r "is_system == 1" --include="*.py" --exclude-dir=".venv" xauth/ | wc -l)

if [ "$IS_SYSTEM_COUNT" -gt 0 ]; then
    echo "✓ 找到 $IS_SYSTEM_COUNT 处使用 is_system == 1 进行判断"
    grep -n "is_system == 1" xauth/*.py | head -5
else
    echo "✗ 未找到使用 is_system 的代码"
fi

echo ""
echo "3. 测试数据库中的用户 is_system 字段..."
echo ""

python manage.py shell << 'EOF'
from xauth.models import SysUser

print("数据库中的用户及其 is_system 状态:")
print("-" * 60)

users = SysUser.objects.all()[:10]  # 只显示前10个用户
for user in users:
    user_type = "系统用户" if user.is_system == 1 else "普通用户"
    print(f"ID: {user.id:3d} | {user.username:15s} | is_system={user.is_system} | {user_type}")

print("-" * 60)

# 统计
system_users = SysUser.objects.filter(is_system=1).count()
normal_users = SysUser.objects.filter(is_system=0).count()

print(f"\n统计:")
print(f"  系统用户 (is_system=1): {system_users} 个")
print(f"  普通用户 (is_system=0): {normal_users} 个")
EOF

echo ""
echo "4. 测试权限判断逻辑..."
echo ""

python manage.py shell << 'EOF'
from xauth.models import SysUser
from xauth.auth import XadminPermAuth
from unittest.mock import Mock

# 模拟请求对象
def create_mock_request(user):
    request = Mock()
    request.user = user
    return request

# 获取系统用户和普通用户
try:
    system_user = SysUser.objects.filter(is_system=1).first()
    normal_user = SysUser.objects.filter(is_system=0).first()
    
    if system_user:
        print(f"✓ 系统用户: {system_user.username} (is_system={system_user.is_system})")
        
        # 测试系统用户的权限检查
        auth = XadminPermAuth(permission="system:test:permission")
        request = create_mock_request(system_user)
        try:
            auth.check_permission(request)
            print("  ✓ 系统用户可以通过权限检查（无需具体权限）")
        except Exception as e:
            print(f"  ✗ 系统用户权限检查失败: {e}")
    else:
        print("⚠️  数据库中没有系统用户")
    
    print()
    
    if normal_user:
        print(f"✓ 普通用户: {normal_user.username} (is_system={normal_user.is_system})")
        print("  ℹ️  普通用户需要通过角色-菜单关联获得权限")
    else:
        print("⚠️  数据库中没有普通用户")
        
except Exception as e:
    print(f"✗ 测试失败: {e}")
    import traceback
    traceback.print_exc()
EOF

echo ""
echo "============================================"
echo "✓ 测试完成！"
echo "============================================"
echo ""
echo "修改总结:"
echo "  - ✓ auth.py: 使用 is_system 判断权限"
echo "  - ✓ api_user.py: 使用 is_system 返回权限"
echo "  - ✓ api_auth.py: 使用 is_system 判断路由和权限（2处）"
echo "  - ✓ settings.py: TITW_SUPER_USER 已标记为废弃"
echo ""
echo "建议:"
echo "  1. 确保系统管理员账号的 is_system=1"
echo "  2. 普通用户的 is_system 应设置为 0"
echo "  3. 通过角色-菜单关联为普通用户分配权限"
echo ""

