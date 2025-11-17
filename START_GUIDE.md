# 🚀 xadmin 快速启动指南

## 📋 启动步骤

### 方法 1: 使用启动脚本（推荐）

#### 终端 1 - 启动后端

```bash
cd /mnt/c/Users/kuntian/xadmin/xadmin
chmod +x start_xadmin.sh
./start_xadmin.sh
```

#### 终端 2 - 启动前端（新终端）

```bash
cd /mnt/c/Users/kuntian/xadmin/xadmin/web
chmod +x start_frontend.sh
./start_frontend.sh
```

---

### 方法 2: 手动启动

#### 步骤 1: 启动服务

```bash
sudo service postgresql start
sudo service redis-server start
```

#### 步骤 2: 启动后端（终端 1）

```bash
cd /mnt/c/Users/kuntian/xadmin/xadmin
uv run python manage.py runserver 0.0.0.0:8000
```

#### 步骤 3: 启动前端（终端 2）

```bash
cd /mnt/c/Users/kuntian/xadmin/xadmin/web
pnpm dev
```

---

## 🌐 访问地址

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:5173 |
| 后端 API | http://127.0.0.1:8000 |
| API 文档 | http://127.0.0.1:8000/system/docs |
| YAML 上传 | http://localhost:5173/#/system/testplan-yaml |

---

## 🔑 登录信息

- 用户名: `admin`
- 密码: `admin123`

---

## ⚠️ 常见问题

### 端口被占用

```bash
# 杀死占用端口的进程
kill -9 $(lsof -ti:8000)  # 后端
kill -9 $(lsof -ti:5173)  # 前端
```

### 服务未启动

```bash
sudo service postgresql status
sudo service postgresql restart

sudo service redis-server status
sudo service redis-server restart
```

---

## 📝 新功能: 测试计划 YAML 上传

1. 登录系统
2. 访问: http://localhost:5173/#/system/testplan-yaml
3. 上传 YAML 文件进行分析

详细文档: `TESTPLAN_YAML_README.md`

---

**创建日期**: 2025-11-11

