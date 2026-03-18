# 阿里云 Docker 社区版部署指南

## 📋 目录
- [部署前准备](#部署前准备)
- [方案一：完整服务部署（推荐）](#方案一完整服务部署推荐)
- [方案二：仅前端部署](#方案二仅前端部署)
- [阿里云 Docker 社区版特殊配置](#阿里云-docker-社区版特殊配置)
- [常见问题](#常见问题)

---

## 部署前准备

### 1. 环境要求
- 阿里云 Docker 社区版（Docker CE）已安装
- Docker Compose 已安装（或使用 docker compose 插件）
- 服务器端口 80/443/5000 开放
- （可选）域名已解析到服务器

### 2. 项目文件检查
确保以下文件存在：
- `Dockerfile.frontend.aliyun` - 前端镜像构建文件（阿里云优化版）
- `Dockerfile.backend` - 后端镜像构建文件
- `docker-compose.yml` - Docker Compose 配置
- `docker/nginx.conf` - Nginx 配置
- `server/app.py` - Python 后端主程序
- `server/requirements.txt` - Python 依赖文件

---

## 方案一：完整服务部署（推荐）

此方案包含前端和 Python 后端，支持完整的 Token URL 管理功能。

### 步骤 1：上传项目文件
将项目完整上传到阿里云服务器，或使用 Git 克隆：
```bash
cd /opt
git clone https://github.com/w1249178256/xyzw_web_helper.git
cd xyzw_web_helper
```

### 步骤 2：（可选）配置环境变量
创建 `.env` 文件设置密钥：
```bash
echo "SECRET_KEY=your-random-secret-key-here" > .env
```

### 步骤 3：构建并启动容器
```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 步骤 4：验证部署

#### 前端访问
- 访问 `http://<服务器IP>` 或配置的域名，确认前端页面正常显示

#### 后端管理界面
- 访问 `http://<服务器IP>/api/` 进入后端管理界面
- 默认管理员账号：`admin` / `admin123`
- **重要**：首次登录后请立即修改密码！

#### 健康检查
- 访问 `http://<服务器IP>/api/health` 应返回 `{"status": "ok"}`

---

## 方案二：仅前端部署

如果您不需要 Token URL 管理后端，可以使用此方案。

### 步骤 1：修改 docker-compose.yml
注释掉后端相关配置，只保留前端服务。

### 步骤 2：构建并启动容器
```bash
docker-compose up -d --build
```

### 步骤 3：验证部署
访问 `http://<服务器IP>` 确认页面正常显示。

---

## 后端服务功能说明

### 主要功能
1. **用户管理**
   - 用户注册/登录
   - 修改密码
   - 注销账号（管理员除外）

2. **Bin 文件管理**
   - 上传 .bin 文件
   - 删除文件
   - 生成 Token URL

3. **Token 获取 API**
   - 通过 URL 自动获取 Token
   - 支持前端自动刷新

### 默认账号
- 用户名：`admin`
- 密码：`admin123`

### 使用流程
1. 登录后端管理界面
2. 上传您的 .bin 文件
3. 复制生成的 Token URL
4. 在前端使用 URL 方式导入 Token

---

---

## 阿里云 Docker 社区版特殊配置

### 1. 防火墙配置
```bash
# 开放 80 端口
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --reload

# 或使用阿里云安全组（推荐）
# 在阿里云控制台 -> 安全组 -> 入方向规则 -> 添加 80/443 端口
```

### 2. 数据持久化（可选）
如需持久化 Nginx 日志或配置，更新 `docker-compose.yml`：
```yaml
services:
  frontend:
    # ... 其他配置 ...
    volumes:
      - ./nginx-logs:/var/log/nginx
      - ./docker/nginx.conf:/etc/nginx/conf.d/default.conf:ro
```

### 3. HTTPS 配置（推荐）
使用 Let's Encrypt 免费证书：

1. 安装 Certbot
```bash
apt install certbot python3-certbot-nginx -y
```

2. 申请证书
```bash
certbot --nginx -d your-domain.com
```

3. 更新 Nginx 配置支持 HTTPS

### 4. 阿里云容器镜像服务（可选）
如需使用阿里云镜像仓库加速：

1. 登录阿里云容器镜像服务
2. 创建命名空间和仓库
3. 构建并推送镜像：
```bash
# 登录
docker login --username=your-username registry.cn-hangzhou.aliyuncs.com

# 构建并推送
docker build -t registry.cn-hangzhou.aliyuncs.com/your-namespace/xyzw-frontend:latest -f Dockerfile.frontend .
docker push registry.cn-hangzhou.aliyuncs.com/your-namespace/xyzw-frontend:latest
```

---

## 常见问题

### Q1: 构建时 pnpm 安装失败
**解决方案：**
- 检查网络连接
- 使用国内镜像源：
```dockerfile
RUN npm config set registry https://registry.npmmirror.com
RUN npm install -g pnpm
RUN pnpm config set registry https://registry.npmmirror.com
```

### Q2: 容器启动后访问 404
**排查步骤：**
1. 检查容器是否正常运行：`docker ps`
2. 查看容器日志：`docker-compose logs frontend`
3. 验证 dist 目录是否正确复制到容器

### Q3: 阿里云端口无法访问
**解决方案：**
1. 检查安全组规则是否开放
2. 检查服务器防火墙
3. 确认没有其他服务占用 80 端口

### Q4: WebSocket 连接失败
**原因：** 项目使用的是客户端 WebSocket，直接连接游戏服务器，无需后端代理。
**注意事项：** 确保游戏服务器的 WebSocket 地址可访问。

---

## 📞 维护命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f

# 更新代码后重新构建
git pull
docker-compose up -d --build

# 清理未使用的镜像
docker image prune -a
```

---

## 📝 注意事项

1. **安全性**：
   - 不要在容器中存储敏感数据
   - 定期更新基础镜像
   - 使用 HTTPS 加密传输

2. **性能优化**：
   - 使用阿里云镜像加速
   - 配置合适的资源限制
   - 启用 Gzip 压缩

3. **监控**：
   - 监控容器运行状态
   - 配置日志轮转
   - 设置告警通知

---

*最后更新：2026-03-18*
