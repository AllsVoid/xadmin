# 测试计划 YAML 上传功能集成指南

## 📋 功能概述

已成功将 TPGen.html 中的 "Upload Your Test Plan" 功能移植到 xadmin 项目中，包括：

1. ✅ YAML 文件上传（拖拽+点击）
2. ✅ YAML 解析与验证
3. ✅ 分析结果展示（兼容机器、警告、错误）
4. ✅ YAML 对比功能（与标准模板对比并高亮差异）

---

## 🗂️ 已创建的文件

### 后端文件

#### 1. 数据模型
- **文件**: `xadmin_db/models.py`
- **新增模型**: `TestPlanYaml`
- **说明**: 存储上传的 YAML 文件和分析结果

#### 2. YAML 分析工具
- **文件**: `xadmin_auth/utils_yaml.py`
- **功能**:
  - YAML 解析
  - 结构验证
  - 机器兼容性检查
  - 模板对比

#### 3. API 接口
- **文件**: `xadmin_auth/api_test_plan_yaml.py`
- **接口列表**:
  - `POST /system/test/plan/yaml/upload` - 上传 YAML
  - `GET /system/test/plan/yaml/{id}/analysis` - 获取分析结果
  - `GET /system/test/plan/yaml/{id}/comparison` - 获取对比结果
  - `GET /system/test/plan/yaml/list` - 获取列表
  - `DELETE /system/test/plan/yaml/{id}` - 删除记录

#### 4. 路由配置
- **文件**: `xadmin_auth/urls.py`
- **已注册**: `api.add_router('test/plan/yaml', api_test_plan_yaml.router)`

### 前端文件

#### 1. Vue 组件
- **文件**: `web/src/views/system/testplan-yaml/index.vue`
- **功能**:
  - 文件上传区域
  - 分析结果展示
  - 统计信息
  - 兼容机器列表
  - 不兼容机器列表
  - 警告和错误展示
  - YAML 对比视图

#### 2. API 接口
- **文件**: `web/src/apis/system/test-plan-yaml.ts`
- **导出**: `testPlanYamlApi`

---

## 🚀 安装和配置步骤

### 1. 安装 PyYAML 依赖

在 xadmin 项目根目录执行：

```bash
pip install pyyaml
# 或使用 uv
uv add pyyaml
```

### 2. 运行数据库迁移

#### 方法 A: 使用 Django 迁移（推荐）

```bash
cd ~/xadmin
# 或 cd /mnt/c/Users/kuntian/xadmin/xadmin

# 生成迁移文件
uv run python manage.py makemigrations xadmin_db

# 应用迁移
uv run python manage.py migrate
```

#### 方法 B: 手动创建表（如果迁移失败）

在 PostgreSQL 中执行以下 SQL:

```sql
CREATE TABLE test_plan_yaml (
    id BIGSERIAL PRIMARY KEY,
    
    -- 文件信息
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_content TEXT NOT NULL,
    file_size INTEGER DEFAULT 0,
    
    -- 测试计划基本信息
    plan_name VARCHAR(255),
    test_type VARCHAR(100),
    cpu VARCHAR(100),
    gpu VARCHAR(100),
    os_distribution VARCHAR(100),
    kernel_version VARCHAR(50),
    
    -- 分析结果（JSONB 格式）
    analysis_result JSONB,
    validation_status VARCHAR(20) DEFAULT 'valid',
    
    -- 兼容性信息
    compatible_machines JSONB,
    incompatible_machines JSONB,
    compatible_count INTEGER DEFAULT 0,
    incompatible_count INTEGER DEFAULT 0,
    
    -- 警告和错误
    warnings JSONB,
    errors JSONB,
    warning_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    
    -- 对比信息
    template_name VARCHAR(100),
    missing_fields JSONB,
    type_errors JSONB,
    
    -- 状态
    is_analyzed BOOLEAN DEFAULT FALSE,
    is_validated BOOLEAN DEFAULT FALSE,
    
    -- 元数据
    create_user BIGINT NOT NULL,
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    update_user BIGINT,
    update_time TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_test_plan_yaml_create_user ON test_plan_yaml(create_user);
CREATE INDEX idx_test_plan_yaml_create_time ON test_plan_yaml(create_time);
CREATE INDEX idx_test_plan_yaml_validation_status ON test_plan_yaml(validation_status);

-- 添加注释
COMMENT ON TABLE test_plan_yaml IS 'YAML测试计划表';
COMMENT ON COLUMN test_plan_yaml.file_name IS '文件名';
COMMENT ON COLUMN test_plan_yaml.file_content IS '文件内容';
COMMENT ON COLUMN test_plan_yaml.validation_status IS '验证状态(valid: 有效; warning: 警告; error: 错误)';
```

### 3. 添加前端路由

编辑 `web/src/router/route.ts`，添加路由配置：

```typescript
// 在适当的位置添加（通常在系统管理模块下）
{
    path: '/system/testplan-yaml',
    name: 'TestPlanYaml',
    component: () => import('@/views/system/testplan-yaml/index.vue'),
    meta: {
        title: 'Upload Test Plan',
        icon: 'upload',
        hidden: false,
        keepAlive: true
    }
}
```

或者，在菜单管理中动态添加菜单项。

### 4. 重启服务

#### 后端

```bash
cd ~/xadmin
uv run python manage.py runserver 0.0.0.0:8000

# 或使用 Gunicorn（生产环境）
gunicorn xadmin.wsgi:application -c gunicorn.conf.py
```

#### 前端

```bash
cd ~/xadmin/web
pnpm dev
```

---

## 📖 使用说明

### 1. 访问页面

- 前端地址: `http://localhost:5173` (开发) 或 `http://localhost:3100` (根据配置)
- 导航到: **系统管理** → **Upload Test Plan**

### 2. 上传 YAML 文件

1. 点击上传区域或拖拽 YAML 文件
2. 支持 `.yaml` 和 `.yml` 文件
3. 最大文件大小: 5MB
4. 点击 "Analyze Test Plan" 按钮

### 3. 查看分析结果

分析完成后会显示:

- **基本信息**: 文件名、计划名称、测试类型、CPU/GPU 等
- **统计数据**: 兼容机器数、不兼容机器数、警告数、错误数
- **详细结果**:
  - Compatible Machines: 兼容的测试机器列表
  - Incompatible Machines: 不兼容的机器及原因
  - Warnings & Errors: 验证警告和错误
  - YAML Comparison: 与标准模板的对比

### 4. YAML 对比功能

点击 "View Detailed Comparison" 按钮查看:
- 标准模板 YAML
- 你上传的 YAML
- 缺失字段列表
- 类型错误列表

---

## 🧪 标准 YAML 模板示例

```yaml
test_plan:
  name: "Smoke Test"
  description: "Basic smoke test for GPU functionality"

hardware:
  cpu: "Ryzen Threadripper"
  gpu: "Radeon RX 7900 Series"
  gpu_version: "24.10.1621"  # GPU firmware version

environment:
  os: "Ubuntu 22.04"
  kernel: "6.2"
  driver: "amdgpu-install 24.10"

test_cases:
  - name: "GPU Detection"
    command: "lspci | grep VGA"
    expected: "Contains AMD/ATI"
  
  - name: "Driver Load"
    command: "lsmod | grep amdgpu"
    expected: "Module loaded"
  
  - name: "ROCm Info"
    command: "rocm-smi"
    expected: "GPU info displayed"
```

---

## 🔧 自定义配置

### 修改机器数据库

编辑 `xadmin_auth/utils_yaml.py` 中的 `MOCK_MACHINES` 列表：

```python
MOCK_MACHINES = [
    {
        "id": 1,
        "name": "AMD-TEST-001",
        "motherboard": "ASUS ROG",
        "cpu": "Ryzen Threadripper",
        "gpu": "Radeon RX 7900 Series",
        "status": "Available"
    },
    # 添加更多机器...
]
```

### 修改标准模板

编辑 `xadmin_auth/utils_yaml.py` 中的 `SMOKE_TEMPLATE`：

```python
SMOKE_TEMPLATE = """
# 你的自定义模板
test_plan:
  name: "Your Test Plan"
  # ...
"""
```

---

## 🐛 故障排除

### 问题 1: 导入错误 "No module named 'yaml'"

**解决方案**:
```bash
pip install pyyaml
```

### 问题 2: 数据库表不存在

**解决方案**:
```bash
uv run python manage.py makemigrations xadmin_db
uv run python manage.py migrate
```

### 问题 3: 404 Not Found (API 路由)

**检查**:
1. 确认 `xadmin_auth/urls.py` 中已添加 `api_test_plan_yaml` 导入和路由注册
2. 重启后端服务

### 问题 4: 前端组件未显示

**检查**:
1. 确认路由配置已添加
2. 确认菜单权限配置正确
3. 清除浏览器缓存

---

## 📝 API 文档

### 上传 YAML

```
POST /system/test/plan/yaml/upload
Content-Type: multipart/form-data

Parameters:
- file: File (YAML 文件)

Response:
{
  "code": 200,
  "message": "File uploaded and analyzed successfully",
  "data": {
    "id": 1,
    "file_name": "test.yaml",
    "basic_info": { ... },
    "is_valid": true,
    "compatible_count": 2,
    "incompatible_count": 3,
    "warning_count": 1,
    "error_count": 0
  }
}
```

### 获取分析结果

```
GET /system/test/plan/yaml/{id}/analysis

Response:
{
  "code": 200,
  "message": "Success",
  "data": {
    "id": 1,
    "file_name": "test.yaml",
    "compatible_machines": [...],
    "incompatible_machines": [...],
    "warnings": [...],
    "errors": [...]
  }
}
```

### 获取对比结果

```
GET /system/test/plan/yaml/{id}/comparison

Response:
{
  "code": 200,
  "message": "Success",
  "data": {
    "user_yaml": "...",
    "template_yaml": "...",
    "missing_fields": [...],
    "type_errors": [...]
  }
}
```

---

## ✅ 功能完成度

- [x] 后端 API 接口
- [x] YAML 解析和验证
- [x] 机器兼容性检查
- [x] YAML 模板对比
- [x] 前端上传组件
- [x] 分析结果展示
- [x] 统计数据展示
- [x] 对比功能
- [x] 数据库模型
- [x] 路由配置

---

## 📞 支持

如有问题，请查看：
1. Django 日志: `~/xadmin/logs/xadmin.log`
2. 浏览器控制台错误信息
3. 网络请求响应

---

**最后更新**: 2025-11-11

