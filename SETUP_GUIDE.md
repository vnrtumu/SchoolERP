# 🛠️ Mindwhile ERP - Complete Setup & Deployment Guide

This guide covers both **Local Development** (running on your laptop) and **Production Deployment** (running on a real server).

---

# 💻 Part 1: Local Development Guide

Follow these steps to get the project running on your local machine for development and testing.

## ✅ Prerequisites

1.  **Python 3.12+**: [Download Here](https://www.python.org/downloads/)
2.  **MySQL Server**: Local instance running on port 3306.
3.  **Redis**: [Download Here](https://redis.io/docs/install/install-redis/) (Required for caching).
4.  **Git**: [Download Here](https://git-scm.com/downloads).

## 🚀 Installation Steps

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd mindwhile-erp-fastapi
```

### 2. Create Virtual Environment
```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
Create `.env` file in the root:
```env
# Database Credentials
MASTER_DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/master_registry

# Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379

# Security
SECRET_KEY=dev-secret-key
TENANT_PASSWORD_ENCRYPTION_KEY=
```

### 5. Generate Security Key
```bash
python scripts/generate_key.py
```
Copy the output key to `TENANT_PASSWORD_ENCRYPTION_KEY` in `.env`.

## 💾 Database Setup

### 6. Initialize Master DB
```bash
python create_master_database.py
alembic -c alembic_master.ini upgrade head
```

## 🏫 Provision First Tenant

```bash
python scripts/provision_tenant.py \
    --subdomain school1 \
    --name "Local School" \
    --code SCH001 \
    --db-name school1_db \
    --db-user root \
    --db-password "password" \
    --root-password "password"
```

## ▶️ Run the App

1.  Start Redis: `redis-server`
2.  Start App: `uvicorn app.main:app --reload`
3.  Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

# 🚀 Part 2: Production Deployment Guide

This guide assumes deployment on **Ubuntu 22.04/24.04 LTS** with root access.

## 1. Server Prerequisites & Security

### Update System
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv git nginx redis-server mysql-server libmysqlclient-dev pkg-config
```

### Create System User
Run app as a limited user, not root.
```bash
sudo adduser mindwhile
sudo usermod -aG sudo mindwhile
su - mindwhile
```

### Setup Firewall (UFW)
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## 2. Application Setup

### Clone Code
```bash
cd /opt
sudo mkdir mindwhile-erp
sudo chown mindwhile:mindwhile mindwhile-erp
cd mindwhile-erp
git clone <your-repo-url> .
```

### Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn uvloop
```
*Tip: `uvloop` makes asyncio faster in production.*

### Environment Variables
Create `.env` with production keys:
```bash
nano .env
```

## 3. Database Setup (Production)

Secure MySQL:
```bash
sudo mysql_secure_installation
```

Create Master DB User:
```sql
CREATE DATABASE master_registry CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'mindwhile_user'@'localhost' IDENTIFIED BY 'StrongPass!';
GRANT ALL PRIVILEGES ON *.* TO 'mindwhile_user'@'localhost'; 
FLUSH PRIVILEGES; 
EXIT;
```
*(Note: `GRANT ALL ON *.*` is needed because the app creates new databases dynamically. In high security environments, restrict this further or use a separate provisioner.)*

Run Migrations:
```bash
source venv/bin/activate
python create_master_database.py
alembic -c alembic_master.ini upgrade head
```

## 4. Systemd Service (Process Management)

Create `mindwhile.service` to keep the app running.
```bash
sudo nano /etc/systemd/system/mindwhile.service
```

**Content:**
```ini
[Unit]
Description=Gunicorn instance to serve Mindwhile ERP
After=network.target

[Service]
User=mindwhile
Group=www-data
WorkingDirectory=/opt/mindwhile-erp
Environment="PATH=/opt/mindwhile-erp/venv/bin"
ExecStart=/opt/mindwhile-erp/venv/bin/gunicorn \
    -k uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind unix:mindwhile.sock \
    -m 007 \
    app.main:app

[Install]
WantedBy=multi-user.target
```

Start Service:
```bash
sudo systemctl start mindwhile
sudo systemctl enable mindwhile
```

## 5. Nginx Reverse Proxy

Configure Nginx to handle domains and subdomains.
```bash
sudo nano /etc/nginx/sites-available/mindwhile
```

**Content:**
```nginx
server {
    listen 80;
    server_name .your-erp-domain.com;  # Dot covers both root and subdomains

    location / {
        include proxy_params;
        proxy_pass http://unix:/opt/mindwhile-erp/mindwhile.sock;
        
        # Forward headers for Tenant Resolution
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable Site:
```bash
sudo ln -s /etc/nginx/sites-available/mindwhile /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 6. SSL Configuration (HTTPS)

Use Certbot for free Let's Encrypt certificates.
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-erp-domain.com -d *.your-erp-domain.com
```
*Note: Wildcard certs often require DNS-01 challenge verification.*

## 7. Maintenance

### View Logs
```bash
journalctl -u mindwhile -f
```

### Deploy Updates
```bash
cd /opt/mindwhile-erp
git pull
source venv/bin/activate
pip install -r requirements.txt
alembic -c alembic_master.ini upgrade head
sudo systemctl restart mindwhile
```

---
**Setup Complete!** 🚀
