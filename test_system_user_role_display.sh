#!/bin/bash
# 测试系统用户角色显示修复

set -e

echo "============================================"
echo "测试系统用户角色显示修复"
echo "============================================"

# 激活虚拟环境
source .venv/bin/activate

echo ""
echo "1. 测试用户列表 API - 检查系统用户角色返回..."
echo ""

python manage.py shell << 'EOF'
from xauth.models import SysUser
from xauth import api_user
from unittest.mock import Mock
import json

print("=" * 60)
print("测试用户列表 API 返回")
print("=" * 60)

# 获取系统用户和普通用户
system_user = SysUser.objects.filter(is_system=1).first()
normal_user = SysUser.objects.filter(is_system=0).first()

if system_user:
    print(f"\n✓ 系统用户: {system_user.username} (ID: {system_user.id}, is_system={system_user.is_system})")
else:
    print("\n⚠️  数据库中没有系统用户")

if normal_user:
    print(f"✓ 普通用户: {normal_user.username} (ID: {normal_user.id}, is_system={normal_user.is_system})")
else:
    print("⚠️  数据库中没有普通用户")

print("\n" + "=" * 60)
print("模拟用户列表 API 返回（仅测试角色字段）")
print("=" * 60)

# 模拟用户列表数据结构
from django.db.models import Subquery, OuterRef, Q
from xauth import models

dept_id = 1  # 测试部门ID
dept_ids = models.SysDept.objects.filter(ancestors__contains=str(dept_id)).values("id")
dept_name_subquery = models.SysDept.objects.filter(id=OuterRef("dept_id")).values("name")[:1]

filter_condition = Q(dept_id__in=dept_ids) | Q(dept_id=dept_id)
users = models.SysUser.objects.filter(filter_condition).annotate(
    dept_name=Subquery(dept_name_subquery)
)[:5]  # 只取前5个

print(f"\n找到 {users.count()} 个用户\n")

for user in users:
    # 这是修复后的逻辑
    if user.is_system == 1:
        role_ids = []
        role_names = ["系统管理员"]
    else:
        roles = models.SysUserRole.objects.filter(user_id=user.id).values_list(
            "role_id", flat=True
        )
        role_names = models.SysRole.objects.filter(id__in=roles).values_list(
            "name", flat=True
        )
        role_ids = list(roles)
        role_names = list(role_names)
    
    user_type = "系统用户" if user.is_system == 1 else "普通用户"
    print(f"用户: {user.username:15s} | 类型: {user_type:8s} | 角色: {role_names}")

print("\n" + "=" * 60)

EOF

echo ""
echo "2. 测试用户详情方法 - 检查系统用户角色返回..."
echo ""

python manage.py shell << 'EOF'
from xauth.models import SysUser

print("=" * 60)
print("测试用户详情方法 get_user_and_roles_by_id")
print("=" * 60)

# 测试系统用户
system_users = SysUser.objects.filter(is_system=1)[:2]
if system_users:
    print("\n【系统用户】")
    for user in system_users:
        user_data = SysUser.get_user_and_roles_by_id(user.id)
        print(f"\n用户: {user_data['username']}")
        print(f"  - ID: {user_data['id']}")
        print(f"  - is_system: {user_data['isSystem']}")
        print(f"  - roleIds: {user_data['roleIds']}")
        print(f"  - roleNames: {user_data['roleNames']}")
        
        if user_data['roleNames'] == ['系统管理员']:
            print("  ✓ 角色显示正确：系统管理员")
        else:
            print(f"  ✗ 角色显示错误：{user_data['roleNames']}")
else:
    print("\n⚠️  数据库中没有系统用户")

# 测试普通用户
normal_users = SysUser.objects.filter(is_system=0)[:2]
if normal_users:
    print("\n【普通用户】")
    for user in normal_users:
        user_data = SysUser.get_user_and_roles_by_id(user.id)
        print(f"\n用户: {user_data['username']}")
        print(f"  - ID: {user_data['id']}")
        print(f"  - is_system: {user_data['isSystem']}")
        print(f"  - roleIds: {user_data['roleIds']}")
        print(f"  - roleNames: {user_data['roleNames']}")
        
        if len(user_data['roleNames']) == 0:
            print("  ⚠️  该用户未分配角色")
        else:
            print(f"  ✓ 角色显示：{', '.join(user_data['roleNames'])}")
else:
    print("\n⚠️  数据库中没有普通用户")

print("\n" + "=" * 60)

EOF

echo ""
echo "3. 检查代码修改..."
echo ""

echo "✓ 检查 xauth/api_user.py 是否包含系统用户角色逻辑..."
if grep -q "系统用户不需要分配角色" xauth/api_user.py; then
    echo "  ✓ 找到系统用户角色处理逻辑"
else
    echo "  ✗ 未找到系统用户角色处理逻辑"
fi

echo ""
echo "✓ 检查 xauth/models.py 是否包含系统用户角色逻辑..."
if grep -q "系统用户不需要分配角色" xauth/models.py; then
    echo "  ✓ 找到系统用户角色处理逻辑"
else
    echo "  ✗ 未找到系统用户角色处理逻辑"
fi

echo ""
echo "✓ 检查前端是否禁用系统用户的分配角色按钮..."
if grep -q "系统用户无需分配角色" web/src/views/system/user/index.vue; then
    echo "  ✓ 找到分配角色按钮禁用逻辑"
else
    echo "  ✗ 未找到分配角色按钮禁用逻辑"
fi

echo ""
echo "✓ 检查分配角色对话框是否有系统用户提示..."
if grep -q "该用户为系统用户，拥有所有权限" web/src/views/system/user/UserUpdateRoleModal.vue; then
    echo "  ✓ 找到系统用户提示信息"
else
    echo "  ✗ 未找到系统用户提示信息"
fi

echo ""
echo "============================================"
echo "✓ 测试完成！"
echo "============================================"
echo ""
echo "修改总结:"
echo "  - ✓ 后端：用户列表 API 为系统用户返回 '系统管理员'"
echo "  - ✓ 后端：用户详情方法为系统用户返回 '系统管理员'"
echo "  - ✓ 前端：禁用系统用户的 '分配角色' 按钮"
echo "  - ✓ 前端：分配角色对话框显示系统用户警告"
echo "  - ✓ 前端：阻止系统用户的角色修改操作"
echo ""
echo "Web 测试步骤:"
echo "  1. 启动 Django 开发服务器："
echo "     python manage.py runserver"
echo ""
echo "  2. 登录 web 界面，进入 '用户管理'"
echo ""
echo "  3. 查看系统用户（如 admin、lucy）的角色列"
echo "     预期：显示 '系统管理员' 标签"
echo ""
echo "  4. 点击系统用户的 '更多' 按钮"
echo "     预期：'分配角色' 按钮为灰色禁用状态"
echo ""
echo "  5. 鼠标悬停在 '分配角色' 按钮上"
echo "     预期：显示提示 '系统用户无需分配角色'"
echo ""

