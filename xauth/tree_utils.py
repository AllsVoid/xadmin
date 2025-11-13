# -*- coding: utf-8 -*-
"""
树结构构建工具函数

优化要点：
1. 一次性查询所有数据，避免 N+1 查询问题
2. 使用字典索引提高查找效率
3. 在内存中构建树结构
"""

from typing import List, Dict, Any, Optional
from xutils import utils


def build_tree_from_flat_data(
    flat_data: List[Any],
    parent_id_field: str = 'parent_id',
    id_field: str = 'id',
    sort_field: str = 'sort',
    root_parent_id: int = 0,
    node_formatter: Optional[callable] = None
) -> List[Dict]:
    """
    从扁平数据构建树结构（通用方法）
    
    Args:
        flat_data: 扁平的数据列表
        parent_id_field: 父ID字段名
        id_field: ID字段名
        sort_field: 排序字段名
        root_parent_id: 根节点的父ID
        node_formatter: 节点格式化函数
    
    Returns:
        树结构列表
    
    Example:
        >>> items = [
        ...     {'id': 1, 'parent_id': 0, 'name': 'root'},
        ...     {'id': 2, 'parent_id': 1, 'name': 'child1'},
        ...     {'id': 3, 'parent_id': 1, 'name': 'child2'},
        ... ]
        >>> tree = build_tree_from_flat_data(items, node_formatter=lambda x: {'name': x['name']})
    """
    # 1. 构建父子关系索引
    children_map = {}
    for item in flat_data:
        parent_id = getattr(item, parent_id_field, None)
        if parent_id not in children_map:
            children_map[parent_id] = []
        children_map[parent_id].append(item)
    
    # 2. 递归构建树
    def build_subtree(pid):
        result = []
        children = children_map.get(pid, [])
        
        # 排序子节点
        if sort_field:
            children.sort(key=lambda x: getattr(x, sort_field, 0))
        
        for item in children:
            # 格式化节点
            if node_formatter:
                node = node_formatter(item)
            else:
                node = {'id': getattr(item, id_field)}
            
            # 递归处理子节点
            item_id = getattr(item, id_field)
            node['children'] = build_subtree(item_id)
            
            result.append(node)
        
        return result
    
    return build_subtree(root_parent_id)


class DeptTreeBuilder:
    """部门树构建器（优化版本）"""
    
    @staticmethod
    def build(
        all_depts: List[Any],
        parent_id: int = 0,
        choice: bool = False,
        status: Optional[int] = None
    ) -> List[Dict]:
        """
        构建部门树
        
        Args:
            all_depts: 所有部门数据（已查询好的列表）
            parent_id: 根节点的父ID
            choice: 是否为选择器模式（简化格式）
            status: 状态过滤
                - None: 不过滤（默认）
                - 1: 只包含启用的部门
                - 2: 只包含禁用的部门
        
        Returns:
            部门树结构
        """
        # 1. 按状态过滤
        if status is not None:
            all_depts = [d for d in all_depts if d.status == status]
        
        # 2. 构建父子关系索引
        children_map = {}
        for dept in all_depts:
            parent = dept.parent_id
            if parent not in children_map:
                children_map[parent] = []
            children_map[parent].append(dept)
        
        # 3. 递归构建树
        def build_subtree(pid):
            result = []
            children = children_map.get(pid, [])
            
            # 按 sort 排序
            children.sort(key=lambda x: x.sort)
            
            for item in children:
                if choice:
                    # 选择器模式（简化格式）
                    node = {
                        'key': item.id,
                        'parentId': item.parent_id,
                        'title': item.name,
                        'sort': item.sort,
                    }
                else:
                    # 完整模式
                    node = {
                        'id': item.id,
                        'parentId': item.parent_id,
                        'name': item.name or "",
                        'sort': item.sort,
                        'status': item.status,
                        'isSystem': bool(item.is_system),
                        'description': item.description,
                        'createUser': item.create_user,
                        'createUserString': 'fake',  # TODO: 改为实际创建人用户名
                        'createTime': utils.dateformat(item.create_time),
                        'updateUser': item.update_user,
                        'updateUserString': 'fake',  # TODO: 改为实际修改人用户名
                        'updateTime': item.update_time,
                    }
                
                # 递归处理子节点
                node['children'] = build_subtree(item.id)
                result.append(node)
            
            return result
        
        return build_subtree(parent_id)


class MenuTreeBuilder:
    """菜单树构建器（优化版本）"""
    
    @staticmethod
    def build(
        all_menus: List[Any],
        ids: Optional[List[int]] = None,
        parent_id: int = 0,
        choice: bool = False,
        all_mode: bool = False
    ) -> List[Dict]:
        """
        构建菜单树
        
        Args:
            all_menus: 所有菜单数据（已查询好的列表）
            ids: 要包含的菜单ID列表（None表示全部）
            parent_id: 根节点的父ID
            choice: 是否为选择器模式（简化格式）
            all_mode: 是否包含所有类型（包括按钮）
        
        Returns:
            菜单树结构
        """
        # 1. 如果指定了 ids，进行过滤并包含祖先节点
        if ids is not None:
            ids_set = set(ids)
            # 构建 id -> 菜单 的映射
            menu_dict = {menu.id: menu for menu in all_menus}
            
            # 收集需要的菜单及其祖先
            needed_menus = set()
            for menu_id in ids:
                if menu_id in menu_dict:
                    # 添加当前菜单
                    needed_menus.add(menu_id)
                    # 添加所有祖先
                    current = menu_dict[menu_id]
                    while current.parent_id > 0 and current.parent_id in menu_dict:
                        needed_menus.add(current.parent_id)
                        current = menu_dict[current.parent_id]
            
            # 过滤菜单列表
            all_menus = [menu for menu in all_menus if menu.id in needed_menus]
        
        # 2. 构建父子关系索引
        children_map = {}
        for menu in all_menus:
            parent = menu.parent_id
            if parent not in children_map:
                children_map[parent] = []
            children_map[parent].append(menu)
        
        # 3. 递归构建树
        def build_subtree(pid):
            result = []
            children = children_map.get(pid, [])
            
            # 按 sort 排序
            children.sort(key=lambda x: x.sort)
            
            for item in children:
                node = None
                
                if all_mode:
                    # 包含所有类型（管理模式）
                    node = MenuTreeBuilder._format_full_node(item)
                    node['children'] = build_subtree(item.id)
                    result.append(node)
                    
                elif choice:
                    # 选择器模式（简化格式）
                    node = {
                        'key': item.id,
                        'parentId': item.parent_id,
                        'title': item.title,
                        'sort': item.sort,
                    }
                    node['children'] = build_subtree(item.id)
                    result.append(node)
                    
                else:
                    # 路由模式（不包含按钮 type=3）
                    if item.type != 3:
                        node = MenuTreeBuilder._format_full_node(item)
                        node['children'] = build_subtree(item.id)
                        result.append(node)
            
            return result
        
        return build_subtree(parent_id)
    
    @staticmethod
    def _format_full_node(item: Any) -> Dict:
        """格式化完整的菜单节点"""
        return {
            'id': item.id,
            'parentId': item.parent_id,
            'title': item.title,
            'type': item.type,
            'path': item.path or "",
            'name': item.name or "",
            'component': item.component or "",
            'redirect': item.redirect or "",
            'icon': item.icon or "",
            'isExternal': bool(item.is_external) if item.is_external else False,
            'isCache': bool(item.is_cache) if item.is_cache else False,
            'isHidden': bool(item.is_hidden) if item.is_hidden else False,
            'permission': item.permission,
            'sort': item.sort,
            'status': item.status,
            'createUser': item.create_user,
            'createUserString': str(item.create_user),  # TODO: 改为实际创建人用户名
            'createTime': utils.dateformat(item.create_time),
            'disabled': None,
        }

