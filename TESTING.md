# 测试用例使用说明

本文档说明如何运行项目中的 pytest 测试用例。

## 📁 测试用例结构

项目包含以下测试模块：

### 后端测试

1. **tpgen 模块测试** (`/home/zx/xadmin_zx/tpgen/tests/`)
   - `test_models.py` - 测试 SutDevice、OsConfig、TestType、TestCase 等模型
   - `test_api.py` - 测试 API 端点（设备、OS配置、测试类型等）

2. **yaml_test_plan 模块测试** (`/home/zx/xadmin_zx/yaml_test_plan/tests/`)
   - `test_validator.py` - 测试 YAML 验证器功能
   - `test_api.py` - 测试 YAML 上传、查询、删除等 API

3. **myTP 模块测试** (`/home/zx/xadmin_zx/web/src/views/tpgen/myTP/tests/`)
   - `test_saved_plan_api.py` - 测试保存的测试计划 CRUD API

4. **tpdb 模块测试** (`/home/zx/xadmin_zx/web/src/views/tpdb/tests/`)
   - `test_tpdb_api.py` - 测试 TPDB 前端对应的后端 API

5. **online 模块测试** (`/home/zx/xadmin_zx/web/src/views/tpgen/online/tests/`)
   - `test_online_api.py` - 测试在线生成器 API

### 通用测试

- `/home/zx/xadmin_zx/tests/` - 项目级通用测试
  - `test_database_connection.py` - 数据库连接测试
  - `test_routes.py` - 路由注册测试
  - 等等

## 🚀 运行测试

### 前提条件

1. 激活 Python 虚拟环境：
```bash
cd /home/zx/xadmin_zx
source .venv/bin/activate
```

2. 确保已安装所有依赖：
```bash
pip install pytest pytest-django pytest-cov
```

### 运行所有测试

```bash
# 运行所有测试
pytest

# 运行所有测试并显示详细输出
pytest -v

# 运行所有测试并显示覆盖率报告
pytest --cov

# 运行所有测试并生成 HTML 覆盖率报告
pytest --cov --cov-report=html
```

### 运行特定模块的测试

```bash
# 运行 tpgen 模块测试
pytest tpgen/tests/ -v

# 运行 yaml_test_plan 模块测试
pytest yaml_test_plan/tests/ -v

# 运行前端对应的后端 API 测试
pytest web/src/views/tpgen/myTP/tests/ -v
pytest web/src/views/tpdb/tests/ -v

# 运行在线生成器测试（无需用户认证的数据获取测试）
# 注意：部分测试会被跳过，因为对应的 API 需要认证或尚未实现
pytest web/src/views/tpgen/online/tests/ -v --tb=short
```

> **注意**：`web/src/views/tpgen/online/tests/` 中的测试被设计为无需用户认证即可运行。
> 这些测试主要验证数据获取 API 的可用性。如果 API 需要认证或返回 404，测试会自动跳过。

### 运行特定测试文件

```bash
# 运行模型测试
pytest tpgen/tests/test_models.py -v

# 运行 API 测试
pytest tpgen/tests/test_api.py -v

# 运行 YAML 验证器测试
pytest yaml_test_plan/tests/test_validator.py -v
```

### 运行特定测试类或测试函数

```bash
# 运行特定测试类
pytest tpgen/tests/test_models.py::TestSutDeviceModel -v

# 运行特定测试函数
pytest tpgen/tests/test_models.py::TestSutDeviceModel::test_create_sut_device -v

# 运行包含特定关键词的测试
pytest -k "device" -v
pytest -k "yaml" -v
pytest -k "api" -v
```

### 运行标记的测试

```bash
# 只运行需要数据库的测试
pytest -m django_db -v

# 跳过慢速测试
pytest -m "not slow" -v
```

## 📊 测试覆盖率

### 生成覆盖率报告

```bash
# 生成终端覆盖率报告
pytest --cov=tpgen --cov=yaml_test_plan --cov=xadmin_tpgen

# 生成 HTML 覆盖率报告
pytest --cov=tpgen --cov=yaml_test_plan --cov=xadmin_tpgen --cov-report=html

# 查看 HTML 报告
# 报告生成在 htmlcov/index.html，使用浏览器打开
```

### 覆盖率选项

```bash
# 显示缺失的行号
pytest --cov --cov-report=term-missing

# 只显示未覆盖的文件
pytest --cov --cov-report=term:skip-covered

# 设置覆盖率阈值
pytest --cov --cov-fail-under=70
```

## 🔍 调试测试

### 查看详细输出

```bash
# 显示 print 语句输出
pytest -s

# 显示详细信息
pytest -v

# 显示非常详细的信息
pytest -vv

# 组合使用
pytest -svv
```

### 在失败时停止

```bash
# 第一个失败后停止
pytest -x

# 失败 N 次后停止
pytest --maxfail=3
```

### 运行上次失败的测试

```bash
# 只运行上次失败的测试
pytest --lf

# 先运行上次失败的，然后运行其他
pytest --ff
```

### 使用调试器

```bash
# 在失败时进入调试器
pytest --pdb

# 在测试开始时进入调试器
pytest --trace
```

## 📝 测试用例编写规范

### 测试文件命名

- 测试文件必须以 `test_` 开头或以 `_test.py` 结尾
- 例如：`test_models.py`, `test_api.py`

### 测试类命名

- 测试类必须以 `Test` 开头
- 例如：`TestSutDeviceModel`, `TestAPIEndpoint`

### 测试函数命名

- 测试函数必须以 `test_` 开头
- 使用描述性名称，清楚表达测试内容
- 例如：`test_create_sut_device`, `test_invalid_yaml_syntax`

### 使用 Fixtures

```python
@pytest.fixture
def sample_device(db):
    """创建示例设备"""
    return SutDevice.objects.create(
        hostname='test-machine',
        product_name='navi10'
    )

def test_device_creation(sample_device):
    """测试使用 fixture"""
    assert sample_device.hostname == 'test-machine'
```

### 使用 Markers

```python
@pytest.mark.django_db
def test_database_operation():
    """需要数据库的测试"""
    pass

@pytest.mark.slow
def test_slow_operation():
    """慢速测试"""
    pass
```

## 🛠️ 常见问题

### 1. 数据库错误

**问题**：测试报错 `django.db.utils.ProgrammingError: relation does not exist`

**解决**：
```bash
# 运行迁移
python manage.py migrate
python manage.py migrate --database=tpdb  # 如果使用多数据库
```

### 2. 导入错误

**问题**：`ModuleNotFoundError: No module named 'xxx'`

**解决**：
```bash
# 确保在虚拟环境中
source .venv/bin/activate

# 安装缺失的依赖
pip install -r requirements.txt
```

### 3. 权限错误

**问题**：测试需要认证但失败

**解决**：使用 `force_login` fixture 或创建测试用户

```python
@pytest.fixture
def auth_client(api_client, test_user):
    api_client.force_login(test_user)
    return api_client
```

### 4. 测试数据库配置

确保 `pytest.ini` 或 `setup.cfg` 中配置了 Django 设置：

```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = xadmin.settings
python_files = tests.py test_*.py *_tests.py
```

## 📈 最佳实践

1. **每个测试应该独立**
   - 不依赖其他测试的执行顺序
   - 使用 fixtures 准备测试数据

2. **测试应该快速**
   - 避免不必要的数据库操作
   - 使用 mock 代替真实的外部调用

3. **测试应该清晰**
   - 一个测试只验证一个功能点
   - 使用描述性的测试名称

4. **使用断言消息**
   ```python
   assert value > 0, f"Value should be positive, got {value}"
   ```

5. **清理测试数据**
   - 使用 `@pytest.mark.django_db(transaction=True)` 自动回滚
   - 或在 fixture 中使用 `yield` 进行清理

## 🎯 持续集成

将测试集成到 CI/CD 流程：

```yaml
# .gitlab-ci.yml 或 .github/workflows/test.yml 示例
test:
  script:
    - source .venv/bin/activate
    - pytest --cov --cov-report=xml --cov-report=html
    - pytest --junitxml=report.xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      junit: report.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

## 📚 更多资源

- [pytest 官方文档](https://docs.pytest.org/)
- [pytest-django 文档](https://pytest-django.readthedocs.io/)
- [Django 测试文档](https://docs.djangoproject.com/en/stable/topics/testing/)

---

## 🔗 相关命令快速参考

```bash
# 基础命令
pytest                           # 运行所有测试
pytest -v                        # 详细模式
pytest -s                        # 显示 print 输出
pytest -x                        # 首次失败后停止
pytest --lf                      # 只运行上次失败的测试
pytest -k "keyword"              # 运行匹配关键词的测试

# 覆盖率
pytest --cov                     # 显示覆盖率
pytest --cov --cov-report=html   # 生成 HTML 报告

# 调试
pytest --pdb                     # 失败时进入调试器
pytest --trace                   # 开始时进入调试器

# 并行运行（需要 pytest-xdist）
pytest -n auto                   # 自动并行
pytest -n 4                      # 使用 4 个进程
```
