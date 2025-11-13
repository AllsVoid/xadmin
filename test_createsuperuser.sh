#!/bin/bash
# 测试 createsuperuser 功能

set -e

echo "============================================"
echo "测试 createsuperuser 修复"
echo "============================================"

# 激活虚拟环境
source .venv/bin/activate

echo ""
echo "1. 检查用户模型配置..."
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
print(f"✓ 用户模型: {User.__name__}")
print(f"✓ USERNAME_FIELD: {User.USERNAME_FIELD}")
print(f"✓ REQUIRED_FIELDS: {User.REQUIRED_FIELDS}")

# 检查 Manager
print(f"✓ Manager: {User.objects.__class__.__name__}")
print(f"✓ create_user 方法存在: {hasattr(User.objects, 'create_user')}")
print(f"✓ create_superuser 方法存在: {hasattr(User.objects, 'create_superuser')}")
EOF

echo ""
echo "2. 检查数据库中是否有 dept_id=1 的部门..."
python manage.py shell << 'EOF'
from xauth.models import SysDept
try:
    dept = SysDept.objects.get(id=1)
    print(f"✓ 找到部门: {dept.name} (ID: {dept.id})")
except SysDept.DoesNotExist:
    print("⚠️  警告: 数据库中没有 ID=1 的部门")
    print("   建议先运行初始化数据脚本")
EOF

echo ""
echo "3. 测试 create_user 方法..."
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
import sys

User = get_user_model()

# 删除测试用户（如果存在）
User.objects.filter(username='test_create_user').delete()

try:
    # 测试创建用户
    user = User.objects.create_user(
        username='test_create_user',
        password='testpass123',
        email='test@example.com'
    )
    print(f"✓ 成功创建用户: {user.username} (ID: {user.id})")
    print(f"  - gender: {user.gender}")
    print(f"  - dept_id: {user.dept_id}")
    print(f"  - status: {user.status}")
    print(f"  - is_system: {user.is_system}")
    
    # 清理
    user.delete()
    print("✓ 测试用户已清理")
except Exception as e:
    print(f"✗ 创建用户失败: {e}")
    sys.exit(1)
EOF

echo ""
echo "4. 测试 create_superuser 方法..."
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
import sys

User = get_user_model()

# 删除测试超级用户（如果存在）
User.objects.filter(username='test_superuser').delete()

try:
    # 测试创建超级用户
    superuser = User.objects.create_superuser(
        username='test_superuser',
        password='superpass123',
        email='super@example.com'
    )
    print(f"✓ 成功创建超级用户: {superuser.username} (ID: {superuser.id})")
    print(f"  - gender: {superuser.gender}")
    print(f"  - dept_id: {superuser.dept_id}")
    print(f"  - status: {superuser.status}")
    print(f"  - is_system: {superuser.is_system}")
    
    # 清理
    superuser.delete()
    print("✓ 测试超级用户已清理")
except Exception as e:
    print(f"✗ 创建超级用户失败: {e}")
    sys.exit(1)
EOF

echo ""
echo "============================================"
echo "✓ 所有测试通过！"
echo "============================================"
echo ""
echo "现在可以使用以下命令创建超级用户："
echo "  python manage.py createsuperuser"
echo ""

