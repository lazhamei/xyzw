# XYZW Web Helper 部署指南

## 架构说明

本项目现在采用前后端分离架构：

- **前端**: Vue 3 + Vite (端口: 3000)
- **后端**: Node.js + Express + SQLite (端口: 8787)
- **API**: `/api/v1/*` 前缀
- **WebSocket**: `/ws` 路径

## 快速开始

### 1. 安装依赖

```bash
# 安装前端依赖
npm install

# 安装后端依赖
cd backend
npm install
cd ..
```

### 2. 配置环境变量

复制 `backend/.env.example` 为 `backend/.env`，并修改其中的密钥：

```bash
cp backend/.env.example backend/.env
```

编辑 `backend/.env`，修改以下内容：
```env
JWT_SECRET=your-very-secure-jwt-secret-key-here
AES_KEY=your-very-secure-aes-encryption-key-here
```

### 3. 初始化管理员账号

```bash
cd backend
npm run init-admin
cd ..
```

默认管理员账号：
- 用户名: admin
- 密码: admin123

**请立即修改默认密码！**

### 4. 启动开发环境

#### 方式一：分别启动

```bash
# 启动后端 (终端1)
npm run backend:dev

# 启动前端 (终端2)
npm run dev
```

#### 方式二：同时启动（需要先安装 concurrently）

```bash
npm run dev:all
```

### 5. 访问应用

- 前端: http://localhost:3000
- 后端健康检查: http://localhost:8787/health

## Docker 部署

### 使用 Docker Compose

1. 创建 `.env` 文件（可选）：
```env
JWT_SECRET=your-production-jwt-secret
AES_KEY=your-production-aes-key
CORS_ORIGINS=https://your-domain.com
```

2. 构建并启动：
```bash
docker-compose up -d --build
```

3. 停止服务：
```bash
docker-compose down
```

4. 查看日志：
```bash
docker-compose logs -f
```

### 单独构建镜像

```bash
# 构建后端镜像
docker build -f Dockerfile.backend -t xyzw-backend .

# 构建前端镜像
docker build -f Dockerfile.frontend -t xyzw-frontend .
```

## 项目结构

```
.
├── backend/              # 后端代码
│   ├── src/
│   │   ├── db/          # 数据库相关
│   │   ├── middleware/  # 中间件
│   │   ├── routes/      # API路由
│   │   └── index.js     # 入口文件
│   ├── .env            # 环境变量
│   └── package.json
├── src/                 # 前端代码
│   ├── api/            # API调用
│   ├── stores/         # Pinia状态管理
│   └── ...
├── docker/             # Docker配置
├── Dockerfile.backend
├── Dockerfile.frontend
└── docker-compose.yml
```

## API 端点

### 认证 (/api/v1/auth)
- `POST /register` - 注册
- `POST /login` - 登录
- `POST /logout` - 登出
- `GET /user` - 获取用户信息
- `POST /refresh` - 刷新token

### 游戏角色 (/api/v1)
- `GET /gamerole_list` - 获取角色列表
- `POST /gameroles` - 添加角色
- `GET /gameroles/:id` - 获取角色详情
- `PUT /gameroles/:id` - 更新角色
- `DELETE /gameroles/:id` - 删除角色

### 日常任务 (/api/v1)
- `GET /daily-tasks` - 获取任务列表
- `GET /daily-tasks/status` - 获取任务状态
- `POST /daily-tasks/:id/complete` - 完成任务
- `GET /daily-tasks/history` - 获取任务历史

### 用户 (/api/v1)
- `GET /user/profile` - 获取用户信息
- `PUT /user/profile` - 更新用户信息
- `PUT /user/password` - 修改密码
- `GET /user/stats` - 获取统计信息

## 数据持久化

- SQLite数据库文件: `backend/data/xyzw.sqlite.bin`
- BIN文件存储: `backend/data/bin-storage`
- 错误日志: `backend/data/backend-errors.log`

## 安全建议

1. 生产环境必须修改 `JWT_SECRET` 和 `AES_KEY`
2. 使用HTTPS
3. 配置适当的CORS来源
4. 定期备份数据库
5. 启用日志监控
6. 限制管理员权限

## 故障排除

### 后端无法启动
- 检查端口8787是否被占用
- 确认 `.env` 文件存在且配置正确
- 查看后端日志

### 前端无法连接后端
- 确认后端已启动
- 检查CORS配置
- 查看浏览器控制台和网络请求

### Docker部署问题
- 检查Docker服务状态
- 确认端口未被占用
- 查看容器日志: `docker-compose logs`
