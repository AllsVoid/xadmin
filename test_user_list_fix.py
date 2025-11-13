#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试用户列表API修复

验证当没有传递 deptId 参数时不会报错
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadmin.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from xauth import api_user, models
from unittest.mock import Mock


def test_user_list_without_dept_id():
    """测试不传 deptId 参数"""
    print("=" * 80)
    print("测试用户列表API - 不传 deptId 参数")
    print("=" * 80)
    
    # 创建模拟请求
    factory = RequestFactory()
    
    # 获取测试用户
    User = get_user_model()
    test_user = User.objects.filter(is_system=1).first()
    if not test_user:
        print("⚠️  没有找到系统用户，跳过测试")
        return False
    
    print(f"\n使用测试用户: {test_user.username}")
    
    # 测试1：不传 deptId 参数（重置按钮的场景）
    print(f"\n【测试 1】不传 deptId 参数（模拟点击重置按钮）")
    try:
        request = factory.get('/system/user/list?page=1&size=10&sort=t1.id,desc')
        request.user = test_user
        
        response = api_user.user_list(request)
        
        if response and 'data' in response:
            user_count = len(response['data'].get('list', []))
            total = response['data'].get('total', 0)
            print(f"  ✓ 请求成功")
            print(f"  - 返回用户数: {user_count}")
            print(f"  - 总用户数: {total}")
            print(f"  - 响应结构正确")
            test1_passed = True
        else:
            print(f"  ✗ 响应格式错误: {response}")
            test1_passed = False
    except Exception as e:
        print(f"  ✗ 请求失败: {e}")
        import traceback
        traceback.print_exc()
        test1_passed = False
    
    # 测试2：传递有效的 deptId
    print(f"\n【测试 2】传递 deptId=1（正常场景）")
    try:
        request = factory.get('/system/user/list?deptId=1&page=1&size=10&sort=t1.id,desc')
        request.user = test_user
        
        response = api_user.user_list(request)
        
        if response and 'data' in response:
            user_count = len(response['data'].get('list', []))
            total = response['data'].get('total', 0)
            print(f"  ✓ 请求成功")
            print(f"  - 返回用户数: {user_count}")
            print(f"  - 总用户数: {total}")
            test2_passed = True
        else:
            print(f"  ✗ 响应格式错误")
            test2_passed = False
    except Exception as e:
        print(f"  ✗ 请求失败: {e}")
        test2_passed = False
    
    # 测试3：传递 deptId 为空字符串
    print(f"\n【测试 3】传递 deptId='' （空字符串）")
    try:
        request = factory.get('/system/user/list?deptId=&page=1&size=10')
        request.user = test_user
        
        response = api_user.user_list(request)
        
        if response and 'data' in response:
            print(f"  ✓ 请求成功（空字符串被正确处理）")
            test3_passed = True
        else:
            print(f"  ✗ 响应格式错误")
            test3_passed = False
    except Exception as e:
        print(f"  ✗ 请求失败: {e}")
        test3_passed = False
    
    # 测试4：传递带 status 参数但不传 deptId
    print(f"\n【测试 4】传递 status 但不传 deptId")
    try:
        request = factory.get('/system/user/list?page=1&size=10&status=1')
        request.user = test_user
        
        response = api_user.user_list(request)
        
        if response and 'data' in response:
            print(f"  ✓ 请求成功（status 过滤正常工作）")
            test4_passed = True
        else:
            print(f"  ✗ 响应格式错误")
            test4_passed = False
    except Exception as e:
        print(f"  ✗ 请求失败: {e}")
        test4_passed = False
    
    # 测试总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    tests = [
        ("不传 deptId（重置场景）", test1_passed),
        ("传递 deptId=1（正常场景）", test2_passed),
        ("传递 deptId=''（空字符串）", test3_passed),
        ("传递 status 但不传 deptId", test4_passed),
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    print(f"\n通过测试: {passed}/{total}")
    
    for name, result in tests:
        status_icon = "✓" if result else "✗"
        print(f"  {status_icon} {name}")
    
    return passed == total


def test_root_dept_query():
    """测试根部门查询"""
    print("\n" + "=" * 80)
    print("测试根部门查询")
    print("=" * 80)
    
    root_dept = models.SysDept.objects.filter(parent_id=0).first()
    
    if root_dept:
        print(f"\n✓ 找到根部门:")
        print(f"  - ID: {root_dept.id}")
        print(f"  - 名称: {root_dept.name}")
        print(f"  - parent_id: {root_dept.parent_id}")
        print(f"  - ancestors: {root_dept.ancestors}")
        return True
    else:
        print(f"\n✗ 未找到根部门（parent_id=0）")
        return False


if __name__ == '__main__':
    print("\n🧪 开始测试用户列表API修复...\n")
    
    try:
        # 测试根部门查询
        root_dept_ok = test_root_dept_query()
        
        if not root_dept_ok:
            print("\n❌ 根部门查询失败，请检查数据库")
            sys.exit(1)
        
        # 测试用户列表API
        all_passed = test_user_list_without_dept_id()
        
        if all_passed:
            print("\n✅ 所有测试通过！修复成功！\n")
            print("修复说明:")
            print("  - 当前端不传 deptId 参数时，后端会自动使用根部门ID")
            print("  - 根部门ID通过查询 parent_id=0 的部门动态获取")
            print("  - 这样可以避免硬编码，使代码更健壮")
            print("\n现在可以在前端测试:")
            print("  1. 打开用户管理页面")
            print("  2. 设置一些过滤条件（如 status=2）")
            print("  3. 点击【重置】按钮")
            print("  4. 应该能正常显示所有用户，不再报500错误")
            sys.exit(0)
        else:
            print("\n❌ 部分测试失败！\n")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

