#!/bin/bash
# AGU ScheduleBot Installation Script
# Run as root or with sudo

set -e

echo "=== AGU ScheduleBot Installation Script ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo ./install.sh)"
    exit 1
fi

# Variables
BOT_USER="schedulebot"
BOT_HOME="/home/$BOT_USER"
PROJECT_DIR="$BOT_HOME/AGU_Schedule"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}[1/8]${NC} Updating system packages..."
apt update && apt upgrade -y

echo -e "${GREEN}[2/8]${NC} Installing dependencies..."
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip git nginx

echo -e "${GREEN}[3/8]${NC} Creating bot user..."
if ! id "$BOT_USER" &>/dev/null; then
    useradd -m -s /bin/bash $BOT_USER
    echo "User $BOT_USER created"
else
    echo "User $BOT_USER already exists"
fi

echo -e "${GREEN}[4/8]${NC} Setting up project directory..."
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}Please clone the repository to $PROJECT_DIR first${NC}"
    echo "Example: git clone <repo-url> $PROJECT_DIR"
    exit 1
fi

echo -e "${GREEN}[5/8]${NC} Setting up Python virtual environment..."
cd $PROJECT_DIR
sudo -u $BOT_USER python3.11 -m venv .venv
sudo -u $BOT_USER .venv/bin/pip install --upgrade pip
sudo -u $BOT_USER .venv/bin/pip install -r requirements.txt

echo -e "${GREEN}[6/8]${NC} Setting up configuration..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    cp $PROJECT_DIR/.env.example $PROJECT_DIR/.env
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/your_secret_key_here_change_in_production/$SECRET_KEY/" $PROJECT_DIR/.env
    chown $BOT_USER:$BOT_USER $PROJECT_DIR/.env
    chmod 600 $PROJECT_DIR/.env
    echo -e "${YELLOW}Please edit $PROJECT_DIR/.env with your BOT_TOKEN and ADMIN credentials${NC}"
fi

echo -e "${GREEN}[7/8]${NC} Installing systemd services..."
cp $PROJECT_DIR/deploy/schedulebot.service /etc/systemd/system/
cp $PROJECT_DIR/deploy/schedulebot-admin.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable schedulebot
systemctl enable schedulebot-admin

echo -e "${GREEN}[8/8]${NC} Setting up directories and permissions..."
mkdir -p $PROJECT_DIR/data $PROJECT_DIR/logs $PROJECT_DIR/backups
chown -R $BOT_USER:$BOT_USER $PROJECT_DIR

echo ""
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo ""
echo "Next steps:"
echo "1. Edit $PROJECT_DIR/.env with your configuration"
echo "2. Initialize database: sudo -u $BOT_USER $PROJECT_DIR/.venv/bin/python -m app.db.init_db"
echo "3. Start services: systemctl start schedulebot schedulebot-admin"
echo "4. Check status: systemctl status schedulebot schedulebot-admin"
echo ""
echo "For Nginx setup, copy deploy/nginx.conf to /etc/nginx/sites-available/"
