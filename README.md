# Solar System Explorer

A real-time solar system exploration webpage displaying information about planets, moons, and artificial spacecraft. Demo: [Solar System Explorer](https://solar.p-chao.com)

## Features

- Hierarchical table showing planets, moons, and spacecraft
- Real-time data updates every 0.5 seconds
- Position coordinates, distances, and velocities relative to Sun and Earth
- Wikipedia links for all celestial bodies and spacecraft
- Collapsed display for inactive spacecraft
- SQLite database for data storage
- Responsive design with mobile card layout

## Quick Start (Local Development)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python init_database.py
```

### 3. Run Web Server
```bash
python3 app.py
```

### 4. Open Browser
Navigate to: http://localhost:5001

## Database Maintenance

- **`init_database.py`** - Initialize database with initial data
- **`update_database.py`** - Update spacecraft status and information
  - Run to update spacecraft mission phases automatically
  - Add new spacecraft to database
  - Update spacecraft status (active/inactive)
  - Example: `python update_database.py`

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **Orbital calculations**: Custom Python calculations based on orbital elements

---

# Deployment Guide

## Option 1: OneinStack Deployment (Recommended)

OneinStack provides automated deployment with pre-configured Nginx and SSL support.

### Prerequisites

- Linux server with OneinStack installed ([oneinstack.com](http://oneinstack.com))
- Python 3.8+ (included with OneinStack)
- Root or sudo access

### Automated Deployment

Use the provided deployment script:

```bash
# Upload project to server
cd /data/wwwroot
git clone <your-repository-url> solar-system-explore

# Make script executable and run
cd solar-system-explore
chmod +x deploy_oneinstack.sh
sudo ./deploy_oneinstack.sh
```

The script automatically:
- Sets up Python virtual environment
- Installs dependencies
- Initializes database
- Configures systemd service
- Sets up Nginx reverse proxy with SSL

### Manual OneinStack Steps

If you prefer manual configuration:

```bash
# 1. Setup environment
cd /data/wwwroot/solar-system-explore
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn
python init_database.py

# 2. Set permissions
chown -R www:www /data/wwwroot/solar-system-explore
chmod -R 755 /data/wwwroot/solar-system-explore
chmod 640 /data/wwwroot/solar-system-explore/solar_system.db

# 3. Install service
cp solar-app.service /etc/systemd/system/
systemctl daemon-reload
systemctl start solar-app
systemctl enable solar-app

# 4. Configure Nginx via OneinStack
cd /root/oneinstack
./vhost.sh
# Follow prompts: Add virtual host → Enter domain → Set webroot → Add SSL

# 5. Add proxy settings to Nginx config
vi /www/server/panel/vhost/nginx/your-domain.conf
# Add proxy configuration (see below)

# 6. Test and reload
nginx -t
systemctl reload nginx
```

**Nginx proxy configuration:**
```nginx
location / {
    proxy_pass http://127.0.0.1:5001;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_redirect off;
    
    proxy_connect_timeout 300;
    proxy_send_timeout 300;
    proxy_read_timeout 300;
    send_timeout 300;
}
```

---

## Option 2: Manual Deployment (Traditional)

For servers without OneinStack or custom setups.

### Prerequisites

- Linux server (Ubuntu 20.04+ or CentOS 7+)
- Python 3.8+
- Root or sudo access
- Domain name (optional, for SSL)

### Quick Deployment

```bash
# 1. Update and install packages
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git nginx

# 2. Upload and setup project
cd /opt
sudo git clone <your-repo-url> SolarSystemExplore
sudo chown -R $USER:$USER SolarSystemExplore
cd SolarSystemExplore

# 3. Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn
python init_database.py

# 4. Create systemd service
sudo nano /etc/systemd/system/solar-app.service
```

**Service configuration (`/etc/systemd/system/solar-app.service`):**
```ini
[Unit]
Description=Solar System Explorer Flask Application
After=network.target

[Service]
User=solarapp
Group=solarapp
WorkingDirectory=/opt/SolarSystemExplore
Environment="PATH=/opt/SolarSystemExplore/venv/bin"
ExecStart=/opt/SolarSystemExplore/venv/bin/gunicorn -w 4 -b 127.0.0.1:5001 --timeout 120 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 5. Start service
sudo systemctl daemon-reload
sudo systemctl start solar-app
sudo systemctl enable solar-app

# 6. Configure Nginx
sudo nano /etc/nginx/sites-available/solar-app
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

```bash
# 7. Enable site and reload Nginx
sudo ln -s /etc/nginx/sites-available/solar-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL Configuration (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Test renewal
sudo certbot renew --dry-run
```

---

# Management & Maintenance

## Service Management

```bash
# Systemd service commands
sudo systemctl start solar-app      # Start service
sudo systemctl stop solar-app       # Stop service
sudo systemctl restart solar-app    # Restart service
sudo systemctl status solar-app     # Check status

# View logs
sudo journalctl -u solar-app -f    # Real-time logs
sudo journalctl -u solar-app -n 100  # Last 100 lines
```

## Application Updates

```bash
# Using Git
cd /path/to/SolarSystemExplore
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart solar-app

# Manual update
# Upload new files, then restart service
sudo systemctl restart solar-app
```

## Database Backup

```bash
# Manual backup
cp solar_system.db solar_system.db.backup.$(date +%Y%m%d)

# Automated backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/solar-app"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp /path/to/solar_system.db $BACKUP_DIR/solar_system.db.$DATE
find $BACKUP_DIR -name "solar_system.db.*" -mtime +7 -delete
EOF

chmod +x backup.sh
# Add to crontab for daily execution: 0 2 * * * /path/to/backup.sh
```

## Performance Tuning

Adjust Gunicorn workers based on CPU cores:
- Formula: `(2 × CPU cores) + 1` workers
- Edit `ExecStart` in systemd service file

**Example for 4-core server:**
```ini
ExecStart=/path/to/venv/bin/gunicorn -w 9 -b 127.0.0.1:5001 --timeout 120 app:app
```

---

# Troubleshooting

## Service Issues

```bash
# Check service status
sudo systemctl status solar-app

# View error logs
sudo journalctl -u solar-app -n 50

# Check if port is in use
sudo netstat -tlnp | grep 5001
```

## Application Not Accessible

```bash
# Test locally
curl http://127.0.0.1:5001/api/health

# Check Nginx configuration
sudo nginx -t

# View Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## Database Issues

```bash
# Check database file
ls -la solar_system.db

# Verify database structure
sqlite3 solar_system.db ".tables"

# Reinitialize if needed
mv solar_system.db solar_system.db.old
python init_database.py
```

## Permission Issues

```bash
# Fix ownership
sudo chown -R www:www /path/to/SolarSystemExplore  # OneinStack
# or
sudo chown -R solarapp:solarapp /opt/SolarSystemExplore  # Manual

# Fix permissions
sudo chmod -R 755 /path/to/SolarSystemExplore
sudo chmod 640 /path/to/SolarSystemExplore/solar_system.db
```

---

# Security Considerations

1. **Keep system updated**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Restrict file permissions**
   - Set appropriate ownership for application directory
   - Use 640 permissions for database file

3. **Firewall configuration**
   ```bash
   # Ubuntu/Debian (UFW)
   sudo ufw allow 'Nginx Full'
   
   # CentOS/RHEL (firewalld)
   sudo firewall-cmd --permanent --add-service=http
   sudo firewall-cmd --permanent --add-service=https
   sudo firewall-cmd --reload
   ```

4. **Disable direct port access**
   - Block port 5001 from external access
   - Only allow access through Nginx proxy

5. **Use SSL/HTTPS**
   - Always use HTTPS in production
   - Configure auto-renewal for Let's Encrypt certificates

---

# File Structure

```
SolarSystemExplore/
├── app.py                      # Flask application
├── init_database.py             # Database initialization
├── update_database.py           # Database update script
├── orbital_calculations.py      # Orbital calculations
├── solar_system.db              # SQLite database (created after init)
├── requirements.txt             # Python dependencies
├── solar-app.service           # Systemd service file
├── deploy_oneinstack.sh        # OneinStack deployment script
├── oneinstack_nginx.conf      # OneinStack Nginx config
└── templates/
    └── index.html             # Main webpage
```

---

# Additional Resources

- **OneinStack**: [oneinstack.com](http://oneinstack.com)
- **Gunicorn**: [docs.gunicorn.org](https://docs.gunicorn.org/)
- **Nginx**: [nginx.org/en/docs/](https://nginx.org/en/docs/)
- **Flask**: [flask.palletsprojects.com](https://flask.palletsprojects.com/)
- **Project Issues**: Report bugs or request features via your repository's issue tracker
