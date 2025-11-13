#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试部门状态过滤功能

验证 status 参数从 999 改为 None 后功能正常
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadmin.settings')
django.setup()

from xauth.models import SysDept


def count_nodes(tree):
    """统计树节点数量"""
    count = len(tree)
    for node in tree:
        if 'children' in node:
            count += count_nodes(node['children'])
    return count


def test_status_filter():
    """测试状态过滤功能"""
    print("=" * 80)
    print("测试部门状态过滤功能")
    print("=" * 80)
    
    # 统计各状态部门数量
    total = SysDept.objects.count()
    enabled = SysDept.objects.filter(status=1).count()
    disabled = SysDept.objects.filter(status=2).count()
    
    print(f"\n数据库统计:")
    print(f"  - 总部门数: {total}")
    print(f"  - 启用部门: {enabled} (status=1)")
    print(f"  - 禁用部门: {disabled} (status=2)")
    
    # 测试1：不过滤（默认）
    print(f"\n【测试 1】不传 status 参数（默认返回所有部门）")
    tree_all = SysDept.build_dept_tree()
    nodes_all = count_nodes(tree_all)
    print(f"  - 方法调用: SysDept.build_dept_tree()")
    print(f"  - 返回节点数: {nodes_all}")
    print(f"  - 预期: {total}")
    print(f"  - 结果: {'✓ 通过' if nodes_all == total else '✗ 失败'}")
    
    # 测试2：传 status=None
    print(f"\n【测试 2】明确传 status=None（返回所有部门）")
    tree_none = SysDept.build_dept_tree(status=None)
    nodes_none = count_nodes(tree_none)
    print(f"  - 方法调用: SysDept.build_dept_tree(status=None)")
    print(f"  - 返回节点数: {nodes_none}")
    print(f"  - 预期: {total}")
    print(f"  - 结果: {'✓ 通过' if nodes_none == total else '✗ 失败'}")
    
    # 测试3：只返回启用的部门
    print(f"\n【测试 3】传 status=1（只返回启用部门）")
    tree_enabled = SysDept.build_dept_tree(status=1)
    nodes_enabled = count_nodes(tree_enabled)
    print(f"  - 方法调用: SysDept.build_dept_tree(status=1)")
    print(f"  - 返回节点数: {nodes_enabled}")
    print(f"  - 预期: {enabled}")
    print(f"  - 结果: {'✓ 通过' if nodes_enabled == enabled else '✗ 失败'}")
    
    # 测试4：只返回禁用的部门
    if disabled > 0:
        print(f"\n【测试 4】传 status=2（只返回禁用部门）")
        tree_disabled = SysDept.build_dept_tree(status=2)
        nodes_disabled = count_nodes(tree_disabled)
        print(f"  - 方法调用: SysDept.build_dept_tree(status=2)")
        print(f"  - 返回节点数: {nodes_disabled}")
        print(f"  - 预期: {disabled}")
        print(f"  - 结果: {'✓ 通过' if nodes_disabled == disabled else '✗ 失败'}")
    else:
        print(f"\n【测试 4】跳过（数据库中没有禁用部门）")
    
    # 测试5：类型提示验证
    print(f"\n【测试 5】类型注解验证")
    try:
        # 这些调用应该都能正常工作
        SysDept.build_dept_tree()
        SysDept.build_dept_tree(status=None)
        SysDept.build_dept_tree(status=1)
        SysDept.build_dept_tree(parent_id=0, choice=True, status=1)
        print(f"  ✓ 所有调用方式都能正常工作")
    except Exception as e:
        print(f"  ✗ 调用失败: {e}")
    
    # 总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    
    all_tests = [
        ("不传参数（默认）", nodes_all == total),
        ("status=None", nodes_none == total),
        ("status=1（启用）", nodes_enabled == enabled),
    ]
    
    if disabled > 0:
        all_tests.append(("status=2（禁用）", nodes_disabled == disabled))
    
    passed = sum(1 for _, result in all_tests if result)
    total_tests = len(all_tests)
    
    print(f"\n通过测试: {passed}/{total_tests}")
    
    for name, result in all_tests:
        status_icon = "✓" if result else "✗"
        print(f"  {status_icon} {name}")
    
    if passed == total_tests:
        print(f"\n🎉 所有测试通过！status 参数优化成功！")
        return True
    else:
        print(f"\n❌ 有测试失败，请检查代码")
        return False


def test_comparison():
    """对比优化前后的调用方式"""
    print("\n" + "=" * 80)
    print("优化前后对比")
    print("=" * 80)
    
    print(f"\n优化前（使用 999）:")
    print(f"  ❌ build_dept_tree(status=999)  # 魔法值，不直观")
    print(f"  ❌ build_dept_tree(status=1)")
    print(f"  ❌ build_dept_tree()  # 默认 status=999")
    
    print(f"\n优化后（使用 None）:")
    print(f"  ✅ build_dept_tree(status=None)  # 明确表示不过滤")
    print(f"  ✅ build_dept_tree(status=1)     # 不变")
    print(f"  ✅ build_dept_tree()             # 默认 status=None，更清晰")
    
    print(f"\n类型提示:")
    print(f"  ✅ status: Optional[int] = None  # IDE 友好，类型安全")
    print(f"  ✅ 完整的 docstring 说明")
    print(f"  ✅ 返回类型注解: List[Dict[str, Any]]")


if __name__ == '__main__':
    print("\n🧪 开始测试部门状态过滤功能...\n")
    
    try:
        # 运行测试
        success = test_status_filter()
        
        # 显示对比
        test_comparison()
        
        if success:
            print("\n✅ 所有测试通过！\n")
            sys.exit(0)
        else:
            print("\n❌ 部分测试失败！\n")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ 测试过程出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

