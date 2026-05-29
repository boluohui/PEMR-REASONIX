# 🚀 生产部署指南

> 使用 **Gunicorn** + **Nginx** 部署个人电子病历档案系统 (PEMR)

---

## 目录

1. [部署架构](#1-部署架构)
2. [安装 Gunicorn](#2-安装-gunicorn)
3. [创建 WSGI 入口](#3-创建-wsgi-入口)
4. [创建 Systemd 服务](#4-创建-systemd-服务)
5. [安装配置 Nginx](#5-安装配置-nginx)
6. [配置静态文件目录](#6-配置静态文件目录)
7. [启动与验证](#7-启动与验证)
8. [管理命令](#8-管理命令)
9. [日志查看](#9-日志查看)
10. [故障排查](#10-故障排查)

---

## 1. 部署架构

```
                        公网 :5300              内网 :8000
用户浏览器 ──────────────→ Nginx ───────────────→ Gunicorn ──→ Flask App ──→ SQLite
                          │
                          └── /static/ ──→ 直接返回 CSS 文件（不经过 Python）
```

| 层级 | 组件 | 职责 |
|------|------|------|
| **反向代理** | Nginx | 监听公网端口，分发请求，缓存静态资源 |
| **应用服务器** | Gunicorn | 运行 Flask，处理业务逻辑 |
| **守护进程** | systemd | 开机自启、进程守护、崩溃自动恢复 |
| **数据库** | SQLite | 本地文件存储，无需额外服务 |

---

## 2. 安装 Gunicorn

在项目的虚拟环境中安装：

```bash
# 进入项目目录
cd /path/to/PEMR-REASONIX

# 激活虚拟环境（如已创建）
source venv/bin/activate

# 安装 gunicorn
pip install gunicorn

# 验证安装
which gunicorn        # 输出: .../venv/bin/gunicorn
gunicorn --version    # 输出: gunicorn (version 25.1.0)
```

---

## 3. 创建 WSGI 入口

Gunicorn 需要一个 Python 模块来加载 Flask 应用实例。

创建 `wsgi.py`（项目根目录）：

```python
"""Gunicorn 入口文件"""
from app import create_app

app = create_app()
```

> **说明**：`wsgi:app` 表示「从 `wsgi.py` 模块中导入 `app` 变量」。Gunicorn 通过这个变量启动 Flask 应用。

---

## 4. 创建 Systemd 服务

使用 systemd 管理 Gunicorn 进程，实现开机自启和崩溃自动恢复。

### 4.1 创建日志目录

```bash
mkdir -p /var/log/pemr
```

### 4.2 创建服务单元文件

创建 `/etc/systemd/system/pemr.service`：

```ini
[Unit]
Description=个人电子病历档案系统 (PEMR)
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/path/to/PEMR-REASONIX
Environment="PATH=/path/to/PEMR-REASONIX/venv/bin"
ExecStart=/path/to/PEMR-REASONIX/venv/bin/gunicorn \
    --workers 2 \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/pemr/access.log \
    --error-logfile /var/log/pemr/error.log \
    wsgi:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**配置项说明：**

| 参数 | 值 | 说明 |
|------|-----|------|
| `WorkingDirectory` | 项目根目录 | Gunicorn 的工作目录 |
| `Environment` | 指向 venv/bin | 让 Gunicorn 使用虚拟环境的 Python |
| `ExecStart` | venv/bin/gunicorn | 启动命令 |
| `--workers 2` | 2 个 worker | 个人使用 2 个 worker 足够 |
| `--bind 127.0.0.1:8000` | 内网端口 | 仅本机可访问，不暴露到公网 |
| `wsgi:app` | 模块:变量 | 加载 Flask 应用 |
| `Restart=always` | — | 进程退出后自动重启 |
| `RestartSec=5` | 5 秒 | 重启前的等待时间 |

### 4.3 启动服务

```bash
# 重新加载 systemd 配置
systemctl daemon-reload

# 启用开机自启
systemctl enable pemr

# 启动服务
systemctl start pemr

# 查看状态
systemctl status pemr
```

预期输出示例：

```
● pemr.service - 个人电子病历档案系统 (PEMR)
     Loaded: loaded (/etc/systemd/system/pemr.service; enabled; preset: enabled)
     Active: active (running) since Fri 2026-05-29 10:57:44 CST; 9s ago
   Main PID: 1266373 (gunicorn)
      Tasks: 4 (limit: 2276)
     Memory: 96.0M (peak: 96.3M)
```

---

## 5. 安装配置 Nginx

### 5.1 安装 Nginx

```bash
apt-get update
apt-get install -y nginx

# 验证安装
nginx -v   # 输出: nginx version: nginx/1.24.0 (Ubuntu)
```

### 5.2 创建站点配置

创建 `/etc/nginx/sites-available/pemr`：

```nginx
server {
    listen 5300;
    server_name your-server-ip;

    # 日志
    access_log /var/log/pemr/nginx-access.log;
    error_log  /var/log/pemr/nginx-error.log;

    # 静态文件 (由 Nginx 直接处理，不经过 Gunicorn)
    location /static/ {
        alias /var/www/pemr/static/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    # 所有其他请求转发给 Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

> 将 `server_name` 替换为你的服务器 IP 或域名。

### 5.3 启用站点

```bash
# 创建软链接启用站点
ln -sf /etc/nginx/sites-available/pemr /etc/nginx/sites-enabled/

# 移除默认站点（避免端口冲突）
rm -f /etc/nginx/sites-enabled/default

# 测试配置是否正确
nginx -t
```

预期输出：

```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

---

## 6. 配置静态文件目录

Nginx 以 `www-data` 用户运行，而项目文件位于 `/root/` 目录下，`www-data` 没有权限访问。需要将静态文件复制到 Nginx 可读的位置。

```bash
# 创建静态文件目录
mkdir -p /var/www/pemr/static

# 复制 CSS/JS 等静态文件
cp /path/to/PEMR-REASONIX/static/style.css /var/www/pemr/static/

# 若有其他静态文件，一并复制
# cp -r /path/to/PEMR-REASONIX/static/* /var/www/pemr/static/

# 设置所有者
chown -R www-data:www-data /var/www/pemr
```

> **为什么这样做？** Nginx 的 worker 进程以 `www-data` 用户运行，该用户没有 `/root/` 目录的读权限。将静态文件移到 `/var/www/` 下是标准做法。

### 关于静态文件同步

每次更新 `style.css` 后，需要手动同步到 Nginx 目录：

```bash
cp /path/to/PEMR-REASONIX/static/style.css /var/www/pemr/static/
```

---

## 7. 启动与验证

### 7.1 启动所有服务

```bash
# 重启 Nginx 加载新配置
systemctl restart nginx

# 确保 Gunicorn 已启动
systemctl start pemr
```

### 7.2 验证各层

```bash
# 测试 Nginx → Gunicorn → Flask 完整链路
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5300/
# 预期: 200

# 测试路由
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5300/records/
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5300/exams/
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5300/prescriptions/

# 测试静态文件（由 Nginx 直接处理）
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5300/static/style.css
# 预期: 200
```

如果所有返回 `200`，部署成功。

---

## 8. 管理命令

### 应用服务 (pemr)

```bash
systemctl status pemr      # 查看状态
systemctl start pemr       # 启动
systemctl stop pemr        # 停止
systemctl restart pemr     # 重启
systemctl enable pemr      # 启用开机自启
systemctl disable pemr     # 关闭开机自启
```

### Nginx

```bash
systemctl status nginx     # 查看状态
systemctl restart nginx    # 重启
systemctl reload nginx     # 重新加载配置（不中断连接）
nginx -t                   # 测试配置文件语法
```

---

## 9. 日志查看

### 应用日志

```bash
# Gunicorn 访问日志（每行一个 HTTP 请求）
tail -f /var/log/pemr/access.log

# Gunicorn 错误日志（应用异常、报错）
tail -f /var/log/pemr/error.log
```

### Nginx 日志

```bash
tail -f /var/log/pemr/nginx-access.log
tail -f /var/log/pemr/nginx-error.log
```

---

## 10. 故障排查

### 10.1 静态文件 403

**现象**：访问 `/static/style.css` 返回 403  
**原因**：Nginx 用户（www-data）无权读取静态文件路径  
**解决**：将静态文件移到 `/var/www/pemr/static/` 并设置正确所有者

```bash
mkdir -p /var/www/pemr/static
cp /path/to/PEMR-REASONIX/static/* /var/www/pemr/static/
chown -R www-data:www-data /var/www/pemr
```

### 10.2 502 Bad Gateway

**现象**：Nginx 返回 502  
**原因**：Gunicorn 没有运行或端口 8000 无法连接  
**解决**：

```bash
systemctl status pemr           # 检查 Gunicorn 是否运行
journalctl -u pemr -n 20        # 查看 Gunicorn 最近的日志
systemctl restart pemr          # 重启 Gunicorn
```

### 10.3 Gunicorn 启动失败

**现象**：`systemctl start pemr` 失败  
**解决**：

```bash
# 检查配置文件路径是否正确
cat /etc/systemd/system/pemr.service

# 手动运行 Gunicorn 测试（看错误输出）
cd /path/to/PEMR-REASONIX
venv/bin/gunicorn --workers 2 --bind 127.0.0.1:8000 wsgi:app

# 查看详细的 systemd 日志
journalctl -u pemr -n 50 --no-pager
```

### 10.4 端口冲突

**现象**：Nginx 启动失败，提示 `address already in use`  
**解决**：

```bash
# 查看 5300 端口被谁占用
ss -tlnp | grep 5300

# 如果是旧的 Flask 开发服务器，停止它
kill <PID>

# 重启 Nginx
systemctl restart nginx
```

---

## 附：开发 vs 生产对比

| 项目 | 开发模式 | 生产模式 |
|------|---------|---------|
| 启动方式 | `python app.py` | `systemctl start pemr` |
| 服务器 | Flask 内置 Werkzeug | Gunicorn |
| 静态文件 | Flask 直接提供 | Nginx 直接提供 |
| 端口 | `5300`（直接暴露） | Nginx `5300` → Gunicorn `8000` |
| 进程管理 | 手动 Ctrl+C | systemd 自动管理 |
| 自动重启 | Flask 自动重载 | systemd + `Restart=always` |
| 日志 | 终端输出 | 文件日志 (`/var/log/pemr/`) |
| Debug 模式 | 开启 | 关闭 |

---

## 附：文件清单

部署过程中创建/修改的文件：

| 文件 | 说明 |
|------|------|
| `wsgi.py` | Gunicorn 入口（项目根目录） |
| `/etc/systemd/system/pemr.service` | Systemd 服务单元 |
| `/etc/nginx/sites-available/pemr` | Nginx 站点配置 |
| `/etc/nginx/sites-enabled/pemr` | 站点配置软链接 |
| `/var/www/pemr/static/style.css` | 静态文件副本 |
| `/var/log/pemr/` | 日志目录 |

---

> **下一篇**：[项目说明文档 (README.md)](README.md)
