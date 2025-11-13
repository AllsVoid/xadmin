# TPDB 安装和配置指南

## 📦 安装步骤

### 1. 添加菜单到数据库

TPDB 页面需要在系统菜单中配置才能访问。有两种方式添加菜单：

#### 方式一：通过 SQL 直接添加（推荐）

在项目根目录执行以下 SQL 文件：

```bash
# 连接到数据库并执行 SQL
psql -h 10.67.167.53 -p 5433 -U amd -d xadmin -f add_tpdb_menu.sql
```

或者手动在数据库中执行 `add_tpdb_menu.sql` 的内容。

#### 方式二：通过 Django Shell 添加

激活虚拟环境后：

```bash
cd /home/xadmin
source .venv/bin/activate
python manage.py shell
```

在 Python shell 中执行：

```python
from xadmin_db.models import SysMenu
from django.utils import timezone

# 创建 TPDB 管理菜单
SysMenu.objects.create(
    id=3000,
    title='TPDB管理',
    parent_id=0,
    type=2,  # 菜单类型
    path='/tpdb',
    name='TPDBManagement',
    component='tpdb/index',
    redirect=None,
    icon='database',
    is_external=0,
    is_cache=0,
    is_hidden=0,
    permission=None,
    sort=5,
    status=1,
    create_user=1,
    create_time=timezone.now()
)

# 创建权限按钮
permissions = [
    (3001, '查看', 'tpdb:view', 1),
    (3002, '新增', 'tpdb:add', 2),
    (3003, '修改', 'tpdb:update', 3),
    (3004, '删除', 'tpdb:delete', 4),
]

for id, title, perm, sort in permissions:
    SysMenu.objects.create(
        id=id,
        title=title,
        parent_id=3000,
        type=3,  # 按钮类型
        path=None,
        name=None,
        component=None,
        redirect=None,
        icon=None,
        is_external=None,
        is_cache=None,
        is_hidden=None,
        permission=perm,
        sort=sort,
        status=1,
        create_user=1,
        create_time=timezone.now()
    )

print("TPDB 菜单添加成功！")
```

#### 方式三：通过系统菜单管理页面添加

1. 登录系统
2. 进入"系统管理" → "菜单管理"
3. 点击"新增"按钮
4. 填写以下信息：
   - **标题**: TPDB管理
   - **上级菜单**: 根目录
   - **类型**: 菜单
   - **路由地址**: /tpdb
   - **组件名称**: TPDBManagement
   - **组件路径**: tpdb/index
   - **图标**: database
   - **排序**: 5
   - **状态**: 启用

### 2. 验证菜单是否添加成功

执行以下 SQL 查询：

```sql
SELECT id, title, parent_id, type, path, component 
FROM sys_menu 
WHERE id >= 3000 AND id < 3100
ORDER BY id;
```

应该能看到：

```
  id  |  title   | parent_id | type |  path  |  component
------+----------+-----------+------+--------+-------------
 3000 | TPDB管理 |         0 |    2 | /tpdb  | tpdb/index
 3001 | 查看     |      3000 |    3 | NULL   | NULL
 3002 | 新增     |      3000 |    3 | NULL   | NULL
 3003 | 修改     |      3000 |    3 | NULL   | NULL
 3004 | 删除     |      3000 |    3 | NULL   | NULL
```

### 3. 配置用户权限

为用户或角色分配 TPDB 菜单权限：

1. 进入"系统管理" → "角色管理"
2. 选择需要配置的角色（如"管理员"）
3. 点击"配置权限"
4. 勾选"TPDB管理"菜单及其子权限
5. 保存配置

### 4. 刷新页面查看菜单

1. 退出登录
2. 重新登录
3. 在侧边栏菜单中应该能看到"TPDB管理"菜单项
4. 点击菜单项，进入 TPDB 管理页面

## 🔧 前端配置

### 确认文件结构

确保以下文件已正确创建：

```
web/src/
├── apis/
│   └── tpdb/
│       ├── index.ts      # API 请求函数
│       └── type.ts       # TypeScript 类型定义
└── views/
    └── tpdb/
        ├── index.vue     # 主入口页面
        ├── index.scss    # 样式文件
        ├── types.ts      # 视图类型定义
        ├── README.md     # 项目文档
        └── components/   # 组件目录
            ├── SutDeviceManager.vue
            ├── OsConfigManager.vue
            ├── TestTypeManager.vue
            ├── TestComponentManager.vue
            └── TestCaseManager.vue
```

### 重启前端开发服务器

如果前端正在运行，需要重启以确保新文件被正确加载：

```bash
cd /home/xadmin/web
pnpm dev
```

## 🌐 后端配置

### 确认 API 路由已配置

检查 `/home/xadmin/tpgen/urls.py`，确保 TPGEN API 已经配置：

```python
# 在 /home/xadmin/xadmin/urls.py 中应该有：
urlpatterns = [
    path('system/', include('xadmin_auth.urls')),
    path('tpgen/', include('xadmin_tpgen.urls')),
    path('tp/', include('tpgen.urls')),  # TPDB 使用此 API
]
```

### 确认数据库连接

TPDB 使用独立的 `tpdb` 数据库，确认配置正确：

```python
# 在 /home/xadmin/xadmin/settings.py 中：
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "xadmin",
        # ...
    },
    "tpdb": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "tpdb",
        "USER": "amd",
        "PASSWORD": "amdyes",
        "HOST": "10.67.167.53",
        "PORT": 5433,
        # ...
    },
}
```

## ✅ 验证安装

### 1. 检查菜单显示

- 登录系统后，侧边栏应该显示"TPDB管理"菜单
- 图标应该是数据库图标（database）

### 2. 检查页面访问

- 点击菜单项，应该能正常打开 TPDB 管理页面
- 页面标题显示"TPDB - Test Plan Database"
- 显示 5 个 Tab：测试设备、操作系统配置、测试类型、测试组件、测试用例

### 3. 检查 API 连接

- 打开浏览器开发者工具（F12）
- 切换到不同的 Tab，观察网络请求
- 应该能看到对 `/tp/api/` 的请求
- 请求应该正常返回数据（即使是空列表也是正常的）

### 4. 测试 CRUD 操作

#### 测试设备管理
1. 点击"新增设备"按钮
2. 填写设备信息（主机名为必填）
3. 保存并检查是否成功添加
4. 尝试编辑和删除操作

#### 操作系统配置
1. 点击"新增配置"按钮
2. 填写 OS 家族和版本
3. 保存并验证

#### 其他模块
按照类似步骤测试其他管理模块

## 🐛 故障排查

### 问题 1: 菜单不显示

**可能原因**：
- 菜单未正确添加到数据库
- 用户没有菜单权限
- 缓存未更新

**解决方法**：
```bash
# 清除菜单缓存
python manage.py shell
>>> from django.core.cache import cache
>>> cache.delete('common_menu_tree')
>>> exit()
```

### 问题 2: 页面 404 错误

**可能原因**：
- 前端组件路径配置错误
- 组件文件不存在

**解决方法**：
1. 检查 `component` 字段是否为 `tpdb/index`
2. 确认 `/home/xadmin/web/src/views/tpdb/index.vue` 存在
3. 重启前端开发服务器

### 问题 3: API 请求失败

**可能原因**：
- 后端服务未启动
- API 路径配置错误
- 跨域问题

**解决方法**：
```bash
# 检查后端服务状态
ps aux | grep python

# 重启后端服务
cd /home/xadmin
source .venv/bin/activate
python manage.py runserver
```

### 问题 4: 数据库连接错误

**可能原因**：
- tpdb 数据库不存在
- 数据库连接配置错误

**解决方法**：
```bash
# 检查数据库是否存在
psql -h 10.67.167.53 -p 5433 -U amd -l | grep tpdb

# 如果不存在，创建数据库
psql -h 10.67.167.53 -p 5433 -U amd -c "CREATE DATABASE tpdb;"

# 运行迁移
cd /home/xadmin
source .venv/bin/activate
python manage.py migrate --database=tpdb
```

## 📝 后续步骤

1. **为超级管理员分配权限**
   - 进入角色管理
   - 为管理员角色添加 TPDB 相关权限

2. **初始化测试数据**
   - 可以使用 `/home/xadmin/tpgen/tp_data.sql` 中的示例数据
   - 根据实际需求添加测试设备、OS 配置等

3. **配置权限控制**
   - 根据需要为不同角色配置不同的 TPDB 访问权限
   - 可以细化到按钮级别的权限控制

## 📖 相关文档

- [TPDB 使用文档](./README.md)
- [TPGEN API 文档](../../../tpgen/TPGEN_API_DOCUMENT.md)
- [系统菜单管理](../system/menu/)

---

如有问题，请查看项目日志或联系开发团队。

