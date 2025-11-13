# TPDB - Test Plan Database Management

测试计划数据库管理系统，用于管理测试相关的基础数据。

## 📁 项目结构

```
tpdb/
├── index.vue                       # 主入口页面
├── index.scss                      # 全局样式
├── types.ts                        # TypeScript 类型定义
├── README.md                       # 项目文档
└── components/                     # 组件目录
    ├── SutDeviceManager.vue       # SUT测试设备管理
    ├── OsConfigManager.vue        # 操作系统配置管理
    ├── TestTypeManager.vue        # 测试类型管理
    ├── TestComponentManager.vue   # 测试组件管理
    └── TestCaseManager.vue        # 测试用例管理
```

## 🎯 功能概述

TPDB 提供了完整的测试计划数据库管理功能，包括：

### 1. SUT 测试设备管理
- **功能**：管理所有测试设备（System Under Test）
- **数据项**：
  - 主机名（hostname）
  - IP 地址
  - ASIC 名称
  - 设备 ID 和版本 ID
  - GPU 系列和型号
- **操作**：
  - 新增、编辑、删除设备
  - 按主机名和 GPU 型号搜索
  - 批量删除
  - 设备列表分页展示

### 2. 操作系统配置管理
- **功能**：管理支持的操作系统配置
- **数据项**：
  - 操作系统家族（如 Ubuntu, RHEL, CentOS）
  - 版本号
  - 镜像下载链接
- **操作**：
  - 新增、编辑、删除配置
  - 按操作系统家族搜索
  - 分页展示

### 3. 测试类型管理
- **功能**：管理测试类型分类
- **数据项**：
  - 测试类型名称（如 Benchmark, Functional, Performance, Stress）
- **操作**：
  - 新增、编辑、删除测试类型
  - 列表展示

### 4. 测试组件管理
- **功能**：管理测试类型下的具体测试组件
- **数据项**：
  - 所属测试类型
  - 组件分类（如 Media, Compute）
  - 组件名称（如 ffmpeg, clpeak）
- **操作**：
  - 新增、编辑、删除组件
  - 按测试类型和组件分类过滤
  - 级联展示测试类型和组件的关系

### 5. 测试用例管理
- **功能**：管理具体的测试用例
- **数据项**：
  - 所属测试组件
  - 测试用例名称
  - 用例配置（JSON 格式）
- **操作**：
  - 新增、编辑、删除测试用例
  - 通过级联选择器选择测试类型和组件
  - JSON 配置编辑和查看
  - 分页展示

## 🎨 界面设计

### 布局结构
```
┌─────────────────────────────────────────┐
│  TPDB - Test Plan Database              │  ← 顶部标题栏
│  测试计划数据库管理                      │
├─────────────────────────────────────────┤
│  [测试设备] [OS配置] [测试类型]         │  ← Tab 切换
│   [测试组件] [测试用例]                 │
├─────────────────────────────────────────┤
│  [搜索框] [操作按钮]                    │  ← 工具栏
├─────────────────────────────────────────┤
│                                          │
│  数据表格                                │  ← 主要内容区
│                                          │
│  [分页器]                                │
└─────────────────────────────────────────┘
```

### 颜色主题
- 主题色：紫色渐变（#667eea → #764ba2）
- 标签颜色：
  - 测试设备：arcoblue
  - 操作系统：green / blue
  - 测试类型：purple
  - 测试组件：blue / green
  - 测试用例：blue

## 🔧 技术栈

- **Vue 3** - Composition API
- **TypeScript** - 类型安全
- **Arco Design Vue** - UI 组件库
- **Axios** - HTTP 请求
- **SCSS** - 样式预处理

## 📡 API 集成

### API 基础路径
```typescript
const BASE_URL = '/tp/api'
```

### API 模块
所有 API 请求定义在 `@/apis/tpdb/index.ts` 中：

```typescript
import * as tpdbApi from '@/apis/tpdb'

// 示例调用
await tpdbApi.listSutDevices(query)
await tpdbApi.createSutDevice(data)
await tpdbApi.updateSutDevice(id, data)
await tpdbApi.deleteSutDevice(id)
```

### 响应格式
```typescript
interface ApiRes<T> {
  success: boolean
  code: number
  msg: string
  data: T
}

interface PageRes<T> {
  total: number
  list: T
}
```

## 💡 使用指南

### 1. 访问页面
在路由配置中添加 TPDB 路由：
```typescript
{
  path: '/tpdb',
  name: 'TPDBManagement',
  component: () => import('@/views/tpdb/index.vue'),
  meta: {
    title: 'TPDB管理',
    icon: 'database',
  }
}
```

### 2. 数据管理流程

#### 推荐的数据创建顺序：
1. **测试类型** → 创建测试分类（如 Benchmark, Functional）
2. **测试组件** → 在测试类型下创建具体组件（如 ffmpeg）
3. **测试用例** → 为测试组件创建具体的测试用例
4. **SUT 设备** → 添加测试设备信息
5. **OS 配置** → 添加支持的操作系统配置

#### 级联关系：
```
测试类型 (TestType)
  └─ 测试组件 (TestComponent)
      └─ 测试用例 (TestCase)
```

### 3. 常见操作

#### 新增设备
1. 点击"新增设备"按钮
2. 填写设备信息（主机名为必填）
3. 点击确定保存

#### 搜索和筛选
- 使用搜索框输入关键词
- 使用下拉选择器进行分类筛选
- 点击"查询"按钮应用筛选
- 点击"重置"按钮清除筛选条件

#### 批量操作
1. 勾选表格中的多个项目
2. 点击"批量删除"按钮
3. 确认删除操作

## 🎯 最佳实践

### 1. 数据完整性
- 确保主机名、测试类型名称等关键字段的唯一性
- 在删除测试类型或组件前，确认没有关联的子数据
- 定期备份重要配置数据

### 2. 命名规范
- 主机名：使用清晰的命名规则（如 `gpu-test-01`）
- 测试类型：使用标准化的类型名称
- 测试组件：使用业界通用的组件名称
- 测试用例：使用描述性的用例名称

### 3. JSON 配置
测试用例配置应使用标准 JSON 格式：
```json
{
  "timeout": 300,
  "retries": 3,
  "parameters": {
    "resolution": "1920x1080",
    "codec": "h264"
  }
}
```

## 🔍 故障排查

### 常见问题

1. **数据加载失败**
   - 检查后端 API 是否正常运行
   - 查看浏览器控制台的网络请求
   - 确认 API 路径配置正确

2. **无法删除数据**
   - 检查是否存在外键约束
   - 确认用户是否有删除权限
   - 查看后端返回的错误信息

3. **JSON 配置格式错误**
   - 使用 JSON 验证工具检查格式
   - 确保所有引号和括号匹配
   - 避免使用单引号

## 📝 开发说明

### 添加新的管理模块

1. 在 `types.ts` 中添加类型定义
2. 在 `@/apis/tpdb/index.ts` 中添加 API 函数
3. 在 `components/` 中创建新的管理组件
4. 在 `index.vue` 中添加新的 Tab

### 组件模板
每个管理组件通常包含：
- 搜索和操作工具栏
- 数据表格
- 添加/编辑弹窗
- CRUD 操作函数

## 🚀 后续优化

### 计划功能
- [ ] 数据导入导出功能
- [ ] 批量编辑功能
- [ ] 数据变更历史记录
- [ ] 高级搜索和过滤
- [ ] 数据统计和可视化
- [ ] 操作日志记录

### 性能优化
- [ ] 虚拟滚动大数据表格
- [ ] 数据缓存机制
- [ ] 懒加载和分页优化

## 📖 相关文档

- [TPGEN API 文档](../../tpgen/TPGEN_API_DOCUMENT.md)
- [后端 Models 定义](../../tpgen/models.py)
- [API Schemas](../../tpgen/schemas.py)

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

---

**最后更新**: 2025-11-12  
**版本**: v1.0.0

