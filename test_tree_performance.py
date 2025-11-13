#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
树结构构建性能测试脚本

测试 build_dept_tree 和 build_menu_tree 的性能
"""

import os
import sys
import django
import time
from django.db import connection, reset_queries
from django.conf import settings

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadmin.settings')
django.setup()

from xauth.models import SysDept, SysMenu


def test_dept_tree_performance():
    """测试部门树构建性能"""
    print("=" * 80)
    print("测试部门树构建性能 (build_dept_tree)")
    print("=" * 80)
    
    # 获取部门总数
    dept_count = SysDept.objects.count()
    print(f"\n部门总数: {dept_count}")
    
    if dept_count == 0:
        print("⚠️  数据库中没有部门数据，跳过测试")
        return
    
    # 启用查询记录
    settings.DEBUG = True
    
    # 测试优化后的方法
    print("\n开始测试...")
    reset_queries()
    start_time = time.time()
    
    tree = SysDept.build_dept_tree()
    
    end_time = time.time()
    elapsed = (end_time - start_time) * 1000
    query_count = len(connection.queries)
    
    print(f"\n✓ 构建完成")
    print(f"  - 查询次数: {query_count}")
    print(f"  - 耗时: {elapsed:.2f}ms")
    print(f"  - 树节点数: {count_tree_nodes(tree)}")
    
    # 显示执行的SQL查询
    if query_count <= 5:
        print(f"\n执行的SQL查询:")
        for i, query in enumerate(connection.queries, 1):
            sql = query['sql'][:100] + '...' if len(query['sql']) > 100 else query['sql']
            print(f"  {i}. {sql}")
    
    # 关闭查询记录
    settings.DEBUG = False
    
    return query_count, elapsed


def test_menu_tree_performance():
    """测试菜单树构建性能"""
    print("\n" + "=" * 80)
    print("测试菜单树构建性能 (build_menu_tree)")
    print("=" * 80)
    
    # 获取菜单总数
    menu_count = SysMenu.objects.count()
    print(f"\n菜单总数: {menu_count}")
    
    if menu_count == 0:
        print("⚠️  数据库中没有菜单数据，跳过测试")
        return
    
    # 启用查询记录
    settings.DEBUG = True
    
    # 测试 1：构建完整菜单树
    print("\n【测试 1】构建完整菜单树 (ids=None)...")
    reset_queries()
    start_time = time.time()
    
    tree1 = SysMenu.build_menu_tree(ids=None)
    
    end_time = time.time()
    elapsed1 = (end_time - start_time) * 1000
    query_count1 = len(connection.queries)
    
    print(f"  - 查询次数: {query_count1}")
    print(f"  - 耗时: {elapsed1:.2f}ms")
    print(f"  - 树节点数: {count_tree_nodes(tree1)}")
    
    # 测试 2：构建指定ID的菜单树
    print("\n【测试 2】构建指定ID的菜单树 (ids=[1010, 1030])...")
    reset_queries()
    start_time = time.time()
    
    tree2 = SysMenu.build_menu_tree(ids=[1010, 1030])
    
    end_time = time.time()
    elapsed2 = (end_time - start_time) * 1000
    query_count2 = len(connection.queries)
    
    print(f"  - 查询次数: {query_count2}")
    print(f"  - 耗时: {elapsed2:.2f}ms")
    print(f"  - 树节点数: {count_tree_nodes(tree2)}")
    
    # 显示执行的SQL查询
    if query_count2 <= 5:
        print(f"\n执行的SQL查询:")
        for i, query in enumerate(connection.queries, 1):
            sql = query['sql'][:100] + '...' if len(query['sql']) > 100 else query['sql']
            print(f"  {i}. {sql}")
    
    # 关闭查询记录
    settings.DEBUG = False
    
    return query_count1, elapsed1, query_count2, elapsed2


def count_tree_nodes(tree):
    """递归计算树节点总数"""
    if not tree:
        return 0
    
    count = len(tree)
    for node in tree:
        if 'children' in node:
            count += count_tree_nodes(node['children'])
    
    return count


def print_summary(dept_result, menu_result):
    """打印性能总结"""
    print("\n" + "=" * 80)
    print("性能测试总结")
    print("=" * 80)
    
    if dept_result:
        dept_queries, dept_time = dept_result
        print(f"\n【部门树】")
        print(f"  - 数据库查询: {dept_queries} 次")
        print(f"  - 响应时间: {dept_time:.2f}ms")
        
        if dept_queries == 1:
            print(f"  ✓ 查询优化成功！仅1次数据库查询")
        else:
            print(f"  ⚠️  查询次数 > 1，可能存在优化空间")
    
    if menu_result:
        menu_queries1, menu_time1, menu_queries2, menu_time2 = menu_result
        print(f"\n【菜单树】")
        print(f"  完整树:")
        print(f"    - 数据库查询: {menu_queries1} 次")
        print(f"    - 响应时间: {menu_time1:.2f}ms")
        
        print(f"  指定ID树:")
        print(f"    - 数据库查询: {menu_queries2} 次")
        print(f"    - 响应时间: {menu_time2:.2f}ms")
        
        if menu_queries1 == 1 and menu_queries2 == 1:
            print(f"  ✓ 查询优化成功！所有场景仅1次数据库查询")
        else:
            print(f"  ⚠️  查询次数 > 1，可能存在优化空间")
    
    print("\n" + "=" * 80)
    print("优化目标:")
    print("  - 查询次数应为 1（一次性查询所有数据）")
    print("  - 响应时间应 < 100ms（中小规模数据）")
    print("=" * 80)


if __name__ == '__main__':
    print("\n🚀 开始性能测试...\n")
    
    try:
        # 测试部门树
        dept_result = test_dept_tree_performance()
        
        # 测试菜单树
        menu_result = test_menu_tree_performance()
        
        # 打印总结
        print_summary(dept_result, menu_result)
        
        print("\n✅ 测试完成！\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

