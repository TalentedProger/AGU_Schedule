# 🚀 Руководство по деплою AGU ScheduleBot

Данное руководство описывает развёртывание бота и админ-панели на VPS с Ubuntu/Debian.

## Предварительные требования

- VPS с Ubuntu 20.04+ или Debian 11+
- Минимум 1 GB RAM, 1 CPU
- Доступ по SSH с правами sudo
- Доменное имя (опционально, для HTTPS)

## 1. Подготовка сервера

### Обновление системы

```bash
sudo apt update && sudo apt upgrade -y
```

### Установка Python 3.11+

```bash
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
```

### Установка дополнительных пакетов

```bash
sudo apt install -y git nginx certbot python3-certbot-nginx
```

## 2. Создание пользователя для бота

```bash
sudo useradd -m -s /bin/bash schedulebot
sudo su - schedulebot
```

## 3. Клонирование проекта

```bash
cd /home/schedulebot
git clone <repository-url> AGU_Schedule
cd AGU_Schedule
```

## 4. Настройка виртуального окружения

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Настройка конфигурации

```bash
cp .env.example .env
nano .env
```

Заполните все необходимые переменные:
```env
BOT_TOKEN=your_bot_token_from_botfather
ADMIN_TG_ID=your_telegram_id
ADMIN_PASSWORD=secure_password_here
SECRET_KEY=generate_with_python_secrets_token_hex_32
DEBUG=False
```

Генерация SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 6. Инициализация базы данных

```bash
python -m app.db.init_db
```

## 7. Создание systemd сервисов

### Сервис для Telegram бота

Создайте файл `/etc/systemd/system/schedulebot.service`:

```bash
sudo nano /etc/systemd/system/schedulebot.service
```

Содержимое:
```ini
[Unit]
Description=AGU ScheduleBot Telegram Bot
After=network.target

[Service]
Type=simple
User=schedulebot
Group=schedulebot
WorkingDirectory=/home/schedulebot/AGU_Schedule
ExecStart=/home/schedulebot/AGU_Schedule/.venv/bin/python -m app.main
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Environment
Environment="PATH=/home/schedulebot/AGU_Schedule/.venv/bin"

[Install]
WantedBy=multi-user.target
```

### Сервис для админ-панели

Создайте файл `/etc/systemd/system/schedulebot-admin.service`:

```bash
sudo nano /etc/systemd/system/schedulebot-admin.service
```

Содержимое:
```ini
[Unit]
Description=AGU ScheduleBot Admin Panel
After=network.target

[Service]
Type=simple
User=schedulebot
Group=schedulebot
WorkingDirectory=/home/schedulebot/AGU_Schedule
ExecStart=/home/schedulebot/AGU_Schedule/.venv/bin/python -m app.main admin
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Environment
Environment="PATH=/home/schedulebot/AGU_Schedule/.venv/bin"

[Install]
WantedBy=multi-user.target
```

### Активация сервисов

```bash
sudo systemctl daemon-reload
sudo systemctl enable schedulebot
sudo systemctl enable schedulebot-admin
sudo systemctl start schedulebot
sudo systemctl start schedulebot-admin
```

### Проверка статуса

```bash
sudo systemctl status schedulebot
sudo systemctl status schedulebot-admin
```

### Просмотр логов

```bash
# Логи бота
sudo journalctl -u schedulebot -f

# Логи админ-панели
sudo journalctl -u schedulebot-admin -f
```

## 8. Настройка Nginx (опционально)

Если вы хотите использовать доменное имя и HTTPS:

### Создание конфигурации Nginx

```bash
sudo nano /etc/nginx/sites-available/schedulebot
```

Содержимое:
```nginx
server {
    listen 80;
    server_name admin.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Активация конфигурации

```bash
sudo ln -s /etc/nginx/sites-available/schedulebot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Установка SSL сертификата

```bash
sudo certbot --nginx -d admin.yourdomain.com
```

## 9. Настройка файрвола

```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS (если используете)
sudo ufw enable
```

## 10. Автоматическое резервное копирование

### Создание cron-задачи для бэкапов

```bash
crontab -e
```

Добавьте строку (ежедневно в 3:00):
```
0 3 * * * /home/schedulebot/AGU_Schedule/.venv/bin/python /home/schedulebot/AGU_Schedule/scripts/backup_db.py create --keep 7
```

## 11. Обновление проекта

```bash
cd /home/schedulebot/AGU_Schedule
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart schedulebot
sudo systemctl restart schedulebot-admin
```

## 12. Мониторинг

### Полезные команды

```bash
# Статус сервисов
sudo systemctl status schedulebot schedulebot-admin

# Перезапуск
sudo systemctl restart schedulebot
sudo systemctl restart schedulebot-admin

# Остановка
sudo systemctl stop schedulebot schedulebot-admin

# Логи в реальном времени
sudo journalctl -u schedulebot -u schedulebot-admin -f

# Использование ресурсов
htop
```

### Проверка здоровья

```bash
# Проверка что бот работает
curl -s http://127.0.0.1:8000/admin/login | head -c 100

# Проверка процессов
ps aux | grep python
```

## Устранение неполадок

### Бот не запускается

1. Проверьте логи: `sudo journalctl -u schedulebot -n 50`
2. Проверьте токен бота в `.env`
3. Убедитесь что нет другого экземпляра: `pkill -f "app.main"`

### Админ-панель недоступна

1. Проверьте порт: `netstat -tlnp | grep 8000`
2. Проверьте файрвол: `sudo ufw status`
3. Проверьте логи Nginx: `sudo tail -f /var/log/nginx/error.log`

### База данных заблокирована

```bash
# Перезапустите сервисы
sudo systemctl restart schedulebot schedulebot-admin
```

## Безопасность

⚠️ **Важные рекомендации:**

1. Используйте сложный `ADMIN_PASSWORD` (минимум 16 символов)
2. Установите `DEBUG=False` в production
3. Регулярно обновляйте зависимости
4. Настройте fail2ban для защиты от брутфорса
5. Используйте HTTPS для админ-панели
6. Ограничьте доступ к SSH по IP (файрвол)
7. Регулярно проверяйте логи на подозрительную активность

---

**Последнее обновление:** December 2025
