-- 添加 YAML 测试计划菜单
-- 注意：需要根据实际情况调整 parent_id 和 sort

-- 1. 查找系统管理的菜单ID
-- SELECT id, title FROM sys_menu WHERE title = '系统管理' OR title = 'System';

-- 2. 插入菜单项（假设系统管理的ID是2，如果不是需要修改）
INSERT INTO sys_menu (
    title,
    parent_id,
    type,
    path,
    component,
    name,
    icon,
    sort,
    status,
    is_system,
    create_user,
    create_time,
    update_time
) VALUES (
    '上传测试计划',           -- 菜单标题
    2,                        -- 父菜单ID（系统管理，需要根据实际情况修改）
    1,                        -- 类型：1=菜单
    '/system/testplan-yaml',  -- 路由路径
    'system/testplan-yaml/index', -- 组件路径
    'TestPlanYaml',           -- 路由名称
    'upload',                 -- 图标
    999,                      -- 排序
    1,                        -- 状态：1=启用
    0,                        -- 是否系统菜单：0=否
    1,                        -- 创建人ID
    NOW(),                    -- 创建时间
    NOW()                     -- 更新时间
) ON CONFLICT DO NOTHING;

-- 3. 验证插入结果
SELECT id, title, path, component FROM sys_menu WHERE path = '/system/testplan-yaml';

