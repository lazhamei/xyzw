# XYZW Web Helper

<div align="center">

![XYZW Logo](public/xiaoyugan.png)

**🎮 咸鱼自动化web平台**

[![Vue 3](https://img.shields.io/badge/Vue-3.4+-4FC08D?style=flat&logo=vue.js&logoColor=white)](https://vuejs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0+-646CFF?style=flat&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Node.js](https://img.shields.io/badge/Node.js-20+-339933?style=flat&logo=nodedotjs&logoColor=white)](https://nodejs.org/)
[![Express](https://img.shields.io/badge/Express-4.18+-000000?style=flat&logo=express&logoColor=white)](https://expressjs.com/)
[![License](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg?style=flat)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

基于前后端分离架构的现代化XYZW游戏辅助工具，支持Token管理、WebSocket通信、游戏自动化等功能。

</div>

---

## 📋 目录

- [项目介绍](#-项目介绍)
- [核心特性](#-核心特性)
- [技术架构](#️-技术架构)
- [快速开始](#-快速开始)
- [部署指南](#-部署指南)
- [API 文档](#-api-文档)
- [贡献指南](#-贡献指南)
- [许可证](#-许可证)

---

## 📖 项目介绍

**XYZW Web Helper** 是一个面向《咸鱼之王》游戏玩家的Web辅助工具集。项目采用现代化的前后端分离架构，提供完整的用户认证、Token管理、日常任务自动化等功能。

### 架构升级

项目已从纯前端模式升级为完整的前后端分离架构：

- **前端**: Vue 3 + Vite - 负责用户界面和交互
- **后端**: Node.js + Express + SQLite - 负责数据管理、用户认证和业务逻辑
- **数据存储**: SQLite 数据库 - 持久化存储用户和游戏数据
- **通信协议**: RESTful API + WebSocket

---

## ✨ 核心特性

### 🔐 用户认证系统
- **安全登录**: JWT token 认证
- **用户注册**: 支持新用户注册
- **密码管理**: 安全的密码加密和修改
- **权限管理**: 支持普通用户和管理员角色
- **会话管理**: 自动token刷新

### 🎮 Token管理系统
- **多角色管理**: 同时管理多个游戏账号
- **多种导入方式**: 手动输入、URL获取、BIN文件导入
- **安全存储**: 加密存储在服务器端数据库
- **Token刷新**: 支持自动刷新机制
- **分组管理**: 支持Token分组归类

### 🌐 WebSocket通信
- **BON协议支持**: 内置Binary Object Notation协议编解码
- **多重加密**: 支持LX、X、XTM等多种加密方式
- **自动重连**: 智能断线重连机制
- **消息队列**: 内置消息队列系统

### 📊 日常任务管理
- **任务自动化**: 支持日常任务自动执行
- **任务追踪**: 实时任务状态和进度追踪
- **历史记录**: 完整的任务执行历史
- **统计分析**: 用户数据统计和分析

### 🎨 主题系统
- **深色/浅色主题**: 无缝切换，自动适应系统偏好
- **实时响应**: 主题切换立即生效
- **统一设计**: 完整支持Naive UI组件库

---

## 🏗️ 技术架构

### 技术栈

```
前端 (Frontend)
├── Vue 3.4+           # 渐进式JavaScript框架
├── Vite 5.0+          # 现代化构建工具
├── Naive UI 2.38+     # Vue 3组件库
├── Pinia 2.1+         # 状态管理
└── Vue Router 4+      # 路由管理

后端 (Backend)
├── Node.js 20+        # JavaScript运行时
├── Express 4.18+      # Web应用框架
├── SQLite 3+          # 轻量级数据库
├── JWT                # JSON Web Token认证
└── WebSocket          # 实时通信

部署 (DevOps)
├── Docker             # 容器化
├── Docker Compose     # 容器编排
└── Nginx              # 反向代理
```

### 项目结构

```
.
├── backend/                    # 后端代码
│   ├── src/
│   │   ├── db/                # 数据库相关
│   │   │   └── index.js       # 数据库初始化和连接
│   │   ├── middleware/        # 中间件
│   │   │   └── auth.js        # 认证中间件
│   │   ├── routes/            # API路由
│   │   │   ├── auth.js        # 认证路由
│   │   │   ├── gameRoles.js   # 游戏角色路由
│   │   │   ├── dailyTasks.js  # 日常任务路由
│   │   │   └── user.js        # 用户路由
│   │   ├── scripts/           # 脚本
│   │   │   └── init-admin.js  # 初始化管理员脚本
│   │   └── index.js           # 后端入口
│   ├── data/                  # 数据目录（git忽略）
│   ├── .env                   # 环境变量
│   ├── .env.example           # 环境变量示例
│   └── package.json
│
├── src/                        # 前端代码
│   ├── api/                   # API调用
│   │   └── index.js
│   ├── stores/                # Pinia状态管理
│   │   ├── auth.js           # 认证状态
│   │   ├── tokenStore.ts     # Token状态（服务端版本）
│   │   └── ...
│   ├── views/                 # 页面组件
│   ├── components/            # 可复用组件
│   └── main.js
│
├── docker/                     # Docker配置
│   └── nginx.conf            # Nginx配置
│
├── Dockerfile.backend         # 后端Dockerfile
├── Dockerfile.frontend        # 前端Dockerfile
├── docker-compose.yml         # Docker Compose配置
├── vite.config.js            # Vite配置
├── package.json              # 前端依赖
├── DEPLOYMENT.md             # 详细部署文档
└── README.md                 # 项目说明
```

---

## 🚀 快速开始

### 环境要求

- **Node.js**: >= 20.19 < 23
- **npm**: >= 10
- **Git**: 最新版本
- **Docker**: (可选，用于容器化部署)

### 1. 克隆项目

```bash
git clone <repository-url>
cd xyzw
```

### 2. 安装依赖

```bash
# 安装前端依赖
npm install

# 安装后端依赖
cd backend
npm install
cd ..
```

### 3. 配置环境变量

```bash
# 复制环境变量示例文件
cd backend
cp .env.example .env
```

编辑 `backend/.env` 文件，修改以下关键配置：

```env
# 必须修改的配置
JWT_SECRET=your-very-secure-jwt-secret-key-here
AES_KEY=your-very-secure-aes-encryption-key-here

# 可选配置
BACKEND_PORT=8787
CORS_ORIGINS=http://localhost:3000
LOG_REQUESTS=true
```

### 4. 初始化数据库和管理员

```bash
cd backend
npm run init-admin
cd ..
```

默认管理员账号：
- **用户名**: `admin`
- **密码**: `admin123`

⚠️ **重要**: 请登录后立即修改默认密码！

### 5. 启动开发环境

#### 方式一：分别启动（推荐）

打开两个终端窗口：

**终端1 - 启动后端：**
```bash
npm run backend:dev
```

**终端2 - 启动前端：**
```bash
npm run dev
```

#### 方式二：同时启动

```bash
npm run dev:all
```

### 6. 访问应用

- **前端地址**: http://localhost:3000
- **后端健康检查**: http://localhost:8787/health
- **API文档**: 见下文 [API 文档](#-api-文档)

---

## 📦 部署指南

### 开发环境部署

见上文 [快速开始](#-快速开始)

### 生产环境部署 - Docker Compose（推荐）

#### 1. 准备环境变量

在项目根目录创建 `.env` 文件：

```env
# .env
JWT_SECRET=your-production-jwt-secret-key
AES_KEY=your-production-aes-key
CORS_ORIGINS=https://your-domain.com
```

#### 2. 构建并启动

```bash
# 构建镜像并启动容器
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 停止并删除数据卷（谨慎使用）
docker-compose down -v
```

#### 3. 访问应用

- **前端**: http://your-server-ip:3000
- **后端**: http://your-server-ip:8787

### 生产环境部署 - 手动部署

#### 1. 构建前端

```bash
npm run build
```

#### 2. 配置后端

```bash
cd backend
npm install --production

# 确保 .env 配置正确
# 确保 data 目录有写权限
mkdir -p data
```

#### 3. 初始化管理员

```bash
npm run init-admin
```

#### 4. 使用 PM2 启动后端

```bash
npm install -g pm2
pm2 start src/index.js --name xyzw-backend
pm2 save
pm2 startup
```

#### 5. 配置 Nginx 代理前端

将 `dist` 目录内容部署到 Web 服务器，并配置 Nginx：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
    }

    # API代理
    location /api/v1 {
        proxy_pass http://localhost:8787;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket代理
    location /ws {
        proxy_pass http://localhost:8787;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

### 数据备份

重要数据位于 `backend/data/` 目录：

```bash
# 备份数据库
cp backend/data/xyzw.sqlite.bin backup-$(date +%Y%m%d).sqlite.bin

# Docker环境下备份
docker run --rm -v xyzw_backend-data:/data -v $(pwd):/backup alpine tar czf /backup/xyzw-data-$(date +%Y%m%d).tar.gz /data
```

---

## 📡 API 文档

### 认证接口 (`/api/v1/auth`)

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| POST | `/register` | 用户注册 | ❌ |
| POST | `/login` | 用户登录 | ❌ |
| POST | `/logout` | 用户登出 | ✅ |
| GET | `/user` | 获取当前用户信息 | ✅ |
| POST | `/refresh` | 刷新访问令牌 | ✅ |

### 游戏角色接口 (`/api/v1`)

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | `/gamerole_list` | 获取游戏角色列表 | ✅ |
| POST | `/gameroles` | 添加游戏角色 | ✅ |
| GET | `/gameroles/:id` | 获取角色详情 | ✅ |
| PUT | `/gameroles/:id` | 更新角色信息 | ✅ |
| DELETE | `/gameroles/:id` | 删除游戏角色 | ✅ |

### 日常任务接口 (`/api/v1`)

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | `/daily-tasks` | 获取任务列表 | ✅ |
| GET | `/daily-tasks/status` | 获取任务状态 | ✅ |
| POST | `/daily-tasks/:id/complete` | 完成任务 | ✅ |
| GET | `/daily-tasks/history` | 获取任务历史 | ✅ |

### 用户接口 (`/api/v1`)

| 方法 | 路径 | 描述 | 认证 |
|------|------|------|------|
| GET | `/user/profile` | 获取用户资料 | ✅ |
| PUT | `/user/profile` | 更新用户资料 | ✅ |
| PUT | `/user/password` | 修改用户密码 | ✅ |
| GET | `/user/stats` | 获取用户统计 | ✅ |

### WebSocket 端点

- **连接地址**: `ws://localhost:8787/ws`
- **协议**: WSS (生产环境推荐使用)

### 响应格式

所有API响应统一使用以下格式：

```json
{
  "success": true,
  "message": "操作成功",
  "data": {}
}
```

错误响应：

```json
{
  "success": false,
  "message": "错误描述"
}
```

---

## 🔧 开发指南

### 可用命令

```bash
# 前端
npm run dev              # 启动开发服务器
npm run build            # 构建生产版本
npm run preview          # 预览构建结果
npm run lint             # 代码检查

# 后端
npm run backend:dev      # 启动后端开发服务
npm run backend:start    # 启动后端生产服务
npm run backend:install  # 安装后端依赖
npm run backend:init-admin  # 初始化管理员

# 前后端
npm run dev:all          # 同时启动前后端（需要concurrently）
```

### 开发模式代理

Vite 开发服务器已配置代理：
- `/api/v1` → `http://localhost:8787`
- `/ws` → `ws://localhost:8787`

### 数据库迁移

当前使用 SQLite，无需复杂迁移。如需重置数据库：

```bash
# 删除数据库文件
rm backend/data/xyzw.sqlite.bin

# 重新初始化
cd backend
npm run init-admin
```

---

## 🔐 安全建议

1. **修改默认密钥**: 生产环境必须修改 `JWT_SECRET` 和 `AES_KEY`
2. **使用HTTPS**: 生产环境必须使用HTTPS
3. **配置CORS**: 仅允许信任的域名访问
4. **定期备份**: 设置自动数据库备份
5. **限制访问**: 使用防火墙限制不必要的端口访问
6. **日志监控**: 监控错误日志，及时发现异常
7. **密码策略**: 强制用户使用强密码
8. **会话管理**: 设置合理的token过期时间

---

## 🐛 故障排除

### 后端无法启动

1. 检查端口 8787 是否被占用：
   ```bash
   netstat -ano | findstr :8787  # Windows
   lsof -i :8787                 # macOS/Linux
   ```

2. 确认 `.env` 文件存在且配置正确

3. 查看后端日志获取详细错误信息

### 前端无法连接后端

1. 确认后端已正常启动
2. 检查 CORS 配置
3. 查看浏览器控制台和网络请求
4. 确认 Vite 代理配置正确

### Docker 部署问题

1. 检查 Docker 服务状态：
   ```bash
   docker --version
   docker-compose --version
   ```

2. 查看容器日志：
   ```bash
   docker-compose logs -f
   ```

3. 检查端口占用：
   ```bash
   docker-compose ps
   ```

---

## 🤝 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发规范

- 使用 ESLint 进行代码检查
- 遵循 Conventional Commits 提交规范
- 保持代码简洁，添加必要注释
- 更新文档以反映代码变更

---

## 📄 许可证

本项目基于 [CC BY-NC-SA 4.0 International License](LICENSE) 许可证。

**⚠️ 重要声明**:
- ✅ **允许**: 个人学习、研究、修改和分享
- ❌ **禁止**: 商业用途、销售、商业化运营
- 📝 **要求**: 署名、相同许可证分享、标注修改

---

## 📞 联系方式

- **项目主页**: [GitHub Repository](https://github.com/wingera/xyzw-1)
- **问题反馈**: [GitHub Issues](https://github.com/wingera/xyzw-1/issues)
- **详细文档**: [DEPLOYMENT.md](./DEPLOYMENT.md)

---

## ⭐ 支持项目

如果这个项目对你有帮助，请给它一个 Star！

Made with ❤️ by the XYZW Team
