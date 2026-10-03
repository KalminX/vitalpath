# VitalPath Education — Production Deployment Guide

This guide details step-by-step instructions for deploying the **VitalPath Education** platform to a standard Linux VPS (Ubuntu 22.04/24.04 LTS or Debian) or container environment.

---

## 1. System Requirements & Architecture

- **Operating System**: Ubuntu 22.04 LTS / 24.04 LTS or Debian 12
- **Python**: 3.11, 3.12, or 3.13
- **Database**: PostgreSQL 15+ (or managed RDS/Neon/Supabase)
- **Web Server / Proxy**: Nginx or Caddy with automated HTTPS (Let's Encrypt)
- **Application Server**: Gunicorn
- **Static Assets**: WhiteNoise (automated caching and compression)

---

## 2. Server Provisioning & Dependencies

SSH into your Linux server and install core packages:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv libpq-dev postgresql postgresql-contrib nginx curl git
```

### PostgreSQL Setup

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE vitalpath_db;
CREATE USER vitalpath_user WITH PASSWORD 'your_secure_db_password';
GRANT ALL PRIVILEGES ON DATABASE vitalpath_db TO vitalpath_user;
ALTER DATABASE vitalpath_db OWNER TO vitalpath_user;
\q
```

---

## 3. Application Setup

Clone the repository into `/var/www/vitalpath`:

```bash
sudo mkdir -p /var/www/vitalpath
sudo chown -R $USER:$USER /var/www/vitalpath
git clone <your-repo-url> /var/www/vitalpath
cd /var/www/vitalpath

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Production Environment Configuration

Create `/var/www/vitalpath/.env`:

```ini
# Django Core
SECRET_KEY=generate_a_random_50_char_secret_key_here
DEBUG=False
ALLOWED_HOSTS=vitalpath.edu,www.vitalpath.edu,your_server_ip

# Database
DATABASE_URL=postgres://vitalpath_user:your_secure_db_password@127.0.0.1:5432/vitalpath_db

# Stripe Settings (Live or Test Mode)
STRIPE_PUBLISHABLE_KEY=pk_live_your_actual_publishable_key
STRIPE_SECRET_KEY=sk_live_your_actual_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_actual_webhook_signing_secret
STRIPE_CURRENCY=usd

# Domain & Site Identity
SITE_URL=https://vitalpath.edu
SITE_NAME=VitalPath Education

# Email Delivery (e.g. SendGrid, Amazon SES, Postmark, Resend)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your_sendgrid_api_key
DEFAULT_FROM_EMAIL=VitalPath Education <hello@vitalpath.edu>
NOTIFICATION_EMAIL=creator@vitalpath.edu

# SSL & Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

Run migrations, collect static files, and seed initial demo data:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py seed_demo
```

---

## 5. Systemd Service Configuration (Gunicorn)

Create `/etc/systemd/system/vitalpath.service`:

```ini
[Unit]
Description=VitalPath Gunicorn Daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/vitalpath
ExecStart=/var/www/vitalpath/.venv/bin/gunicorn \
          --access-logfile /var/log/vitalpath_access.log \
          --error-logfile /var/log/vitalpath_error.log \
          --workers 3 \
          --bind unix:/run/vitalpath.sock \
          vitalpath.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo chown -R www-data:www-data /var/www/vitalpath
sudo systemctl daemon-reload
sudo systemctl enable vitalpath
sudo systemctl start vitalpath
sudo systemctl status vitalpath
```

---

## 6. Nginx & HTTPS Configuration

Create `/etc/nginx/sites-available/vitalpath`:

```nginx
server {
    server_name vitalpath.edu www.vitalpath.edu;

    client_max_body_size 20M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/vitalpath/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

    location /media/ {
        alias /var/www/vitalpath/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/vitalpath.sock;
    }
}
```

Enable site and install Certbot for SSL:

```bash
sudo ln -s /etc/nginx/sites-available/vitalpath /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Automated SSL Certificate via Let's Encrypt
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d vitalpath.edu -d www.vitalpath.edu
```

---

## 7. Stripe Webhook Production Configuration

1. In your **Stripe Dashboard**, navigate to **Developers → Webhooks**.
2. Click **Add Endpoint**.
3. **Endpoint URL**: `https://vitalpath.edu/webhooks/stripe/`
4. **Events to Listen to**:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
5. Copy the **Signing secret** (starts with `whsec_...`) into your `.env` file under `STRIPE_WEBHOOK_SECRET`.
6. Restart Gunicorn: `sudo systemctl restart vitalpath`.

---

## 8. Alternative: Docker Deployment

You can also deploy with Docker & Docker Compose:

```bash
docker-compose up -d --build
```
