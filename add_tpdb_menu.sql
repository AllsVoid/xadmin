-- Add TPDB Management Menu
-- TPDB 数据库管理菜单

INSERT INTO sys_menu
(id, title, parent_id, type, path, name, component, redirect, icon, is_external, is_cache, is_hidden, permission, sort, status, create_user, create_time, update_user, update_time)
VALUES
-- TPDB 管理菜单 (顶级菜单)
(3000, 'TPDB管理', 0, 2, '/tpdb', 'TPDBManagement', 'tpdb/index', NULL, 'database', 0, 0, 0, NULL, 5, 1, 1, NOW(), NULL, NULL),

-- TPDB 子菜单权限
(3001, '查看', 3000, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'tpdb:view', 1, 1, 1, NOW(), NULL, NULL),
(3002, '新增', 3000, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'tpdb:add', 2, 1, 1, NOW(), NULL, NULL),
(3003, '修改', 3000, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'tpdb:update', 3, 1, 1, NOW(), NULL, NULL),
(3004, '删除', 3000, 3, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'tpdb:delete', 4, 1, 1, NOW(), NULL, NULL)
ON CONFLICT (id) DO NOTHING;

-- 注释：
-- type: 1=目录, 2=菜单, 3=按钮
-- is_external: 0=否, 1=是
-- is_cache: 0=否, 1=是
-- is_hidden: 0=否, 1=是
-- status: 1=启用, 2=禁用

