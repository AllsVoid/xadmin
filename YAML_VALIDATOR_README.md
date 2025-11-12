# YAML 验证器集成说明

## 📋 功能说明

已成功将 TPGen.html 中的 YAML 验证逻辑移植到 xadmin 后端，提供严格的语法和兼容性验证。

## 🆕 新增文件

### 1. `xadmin_auth/yaml_validator.py`
完整的 YAML 验证器，包括：
- ✅ **语法验证** - 检测 YAML 格式错误
- ✅ **E001 验证** - 检查必需字段是否存在
- ✅ **E002 验证** - 检查必需字段是否为空
- ✅ **E101 验证** - 检查值类型是否正确 (string, boolean, array, etc.)
- ✅ **E102 验证** - 检查值是否在允许范围内（白名单）
- ✅ **E300 验证** - 检查无效组合 (如 RHEL 7 + Kernel 6.1)

### 2. `xadmin_auth/api_test_plan_yaml.py` (已修改)
集成了新的验证器，在上传时进行严格验证

## 🔄 同步文件到 WSL

### 方法 1: 使用 WSL 命令行

```bash
# 复制验证器
cp /mnt/c/Users/kuntian/xadmin/xadmin/xadmin_auth/yaml_validator.py \
   ~/xadmin_1111/xadmin_auth/yaml_validator.py

# 复制 API 文件
cp /mnt/c/Users/kuntian/xadmin/xadmin/xadmin_auth/api_test_plan_yaml.py \
   ~/xadmin_1111/xadmin_auth/api_test_plan_yaml.py

# 验证文件已存在
ls -lh ~/xadmin_1111/xadmin_auth/yaml_validator.py
ls -lh ~/xadmin_1111/xadmin_auth/api_test_plan_yaml.py
```

### 方法 2: 使用 Windows 文件资源管理器

**源文件位置：**
```
C:\Users\kuntian\xadmin\xadmin\xadmin_auth\yaml_validator.py
C:\Users\kuntian\xadmin\xadmin\xadmin_auth\api_test_plan_yaml.py
```

**目标位置：**
```
\\wsl.localhost\Ubuntu-22.04\home\kuntian\xadmin_1111\xadmin_auth\
```

拖拽复制这两个文件并替换。

## 🚀 启动服务

### 1. 后端不需要重启
Django 开发服务器会自动检测到文件变更并重新加载。

如果后端没有自动重载，按 `Ctrl+C` 停止后重新启动：
```bash
cd ~/xadmin_1111
uv run python manage.py runserver 0.0.0.0:8000
```

### 2. 前端不需要修改
前端已有的错误显示逻辑会自动显示后端返回的详细错误信息。

## 🧪 测试验证

### 测试用例 1: 有语法错误的 YAML

使用 `amd_gpu_config_debian_Debian_11.yaml` 文件（图1中的文件）

**预期结果：**
- ❌ 上传失败
- 显示：`YAML Syntax Errors Found`
- 显示行号：`Line 4 [ERROR]`
- 显示错误：`Invalid YAML syntax. Expected key-value pair...`

### 测试用例 2: 缺少必需字段

创建一个缺少 `metadata` 字段的 YAML 文件

**预期结果：**
- ❌ 上传失败
- 显示：`E001 Unsupported: missing mandatory field "Metadata" [metadata]`

### 测试用例 3: 类型错误

将 `firmware.comparison` 设为字符串而不是布尔值

**预期结果：**
- ❌ 上传失败
- 显示：`E101 Unsupported: value type error...Expected boolean, got string`

### 测试用例 4: 无效组合

设置 RHEL 7 + Kernel 6.1

**预期结果：**
- ❌ 上传失败
- 显示：`E300 Unsupported: invalid combination detected...`

### 测试用例 5: 正确的 YAML

使用 TPGen 生成的标准 YAML 文件

**预期结果：**
- ✅ 上传成功
- 显示文件名和分析结果

## 📊 验证规则详情

### 必需字段 (E001)

```
metadata
  ├─ generated
  └─ version

hardware
  ├─ cpu
  ├─ gpu
  └─ machines

environment
  ├─ os
  │  └─ method
  └─ kernel
     └─ method

firmware
  ├─ gpu_version
  └─ comparison

test_suites
```

### 值类型要求 (E101)

| 字段 | 类型 |
|------|------|
| `metadata.generated` | string |
| `metadata.version` | string |
| `firmware.comparison` | **boolean** (true/false, 不是字符串) |
| `hardware.machines` | array |
| `test_suites` | array |

### 值范围限制 (E102)

| 字段 | 允许的值 |
|------|----------|
| `hardware.cpu` | Ryzen Threadripper, Ryzen 9, Ryzen 7, EPYC |
| `hardware.gpu` | Radeon RX 7900 Series, Radeon RX 6800 Series, ... |
| `environment.os.method` | same, individual |
| `environment.kernel.type` | DKMS, Mainline, Custom Build, LTS |

### 无效组合 (E300)

- ❌ RHEL 7 + LTS Kernel 6.1
- ❌ RHEL 7 + Mainline Kernel 6.0/6.1/6.2

## 🐛 故障排除

### 问题 1: `ImportError: No module named 'yaml_validator'`

**解决方案：**
```bash
# 确保文件已复制到正确位置
ls ~/xadmin_1111/xadmin_auth/yaml_validator.py

# 如果文件不存在，重新复制
cp /mnt/c/Users/kuntian/xadmin/xadmin/xadmin_auth/yaml_validator.py \
   ~/xadmin_1111/xadmin_auth/yaml_validator.py
```

### 问题 2: 后端没有自动重载

**解决方案：**
```bash
# 手动重启后端
cd ~/xadmin_1111
# 按 Ctrl+C 停止
uv run python manage.py runserver 0.0.0.0:8000
```

### 问题 3: 验证器返回的错误前端没有正确显示

**解决方案：**
检查前端控制台（F12）查看完整的 API 响应，确认错误信息格式。

## 📝 API 响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "File uploaded and analyzed successfully",
  "data": {
    "id": 1,
    "file_name": "test_plan.yaml",
    "is_valid": true,
    ...
  }
}
```

### 错误响应（语法错误）
```json
{
  "code": 400,
  "message": "YAML Syntax Errors Found",
  "data": {
    "error_code": "SYNTAX_ERROR",
    "error_message": "Line 4 [ERROR]\nInvalid YAML syntax...",
    "line_number": 4,
    "errors": ["Invalid YAML syntax..."]
  }
}
```

### 错误响应（验证错误）
```json
{
  "code": 400,
  "message": "YAML Syntax Errors Found",
  "data": {
    "error_code": "E001",
    "error_message": "[ERROR]\nE001 Unsupported: missing mandatory field...",
    "line_number": null,
    "errors": ["E001 Unsupported..."]
  }
}
```

## ✅ 验证流程

```
上传 YAML 文件
    ↓
1. 文件类型检查 (.yaml/.yml)
    ↓
2. 文件大小检查 (< 5MB)
    ↓
3. 语法验证 (SYNTAX_ERROR)
    ↓
4. 必需字段验证 (E001)
    ↓
5. 非空字段验证 (E002)
    ↓
6. 类型验证 (E101)
    ↓
7. 值范围验证 (E102)
    ↓
8. 无效组合验证 (E300)
    ↓
9. 兼容性分析
    ↓
10. 保存到数据库
    ↓
返回结果
```

## 🎯 总结

- ✅ TPGen.html 的 JavaScript 验证逻辑已完整移植到 Python 后端
- ✅ 支持所有错误类型：SYNTAX_ERROR, E001, E002, E101, E102, E300
- ✅ 提供详细的错误信息和行号定位
- ✅ 与前端完全兼容，无需前端修改

---

**完成时间**: 2025-11-12  
**参考文件**: TPGen.html (行 3773-5355)

