#!/usr/bin/env python3
"""
Stop all local bot instances and clear potential conflicts.

This script helps resolve Telegram bot conflicts by stopping local instances.
"""

import subprocess
import sys
import os


def run_command(cmd, shell=True):
    """Run command and return output."""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def kill_python_processes():
    """Kill all Python processes that might be running the bot."""
    print("🔍 Поиск запущенных Python процессов...")
    
    # Windows
    if os.name == 'nt':
        # Find Python processes
        code, stdout, stderr = run_command('tasklist /fi "imagename eq python.exe" /fo csv')
        if code == 0 and stdout:
            lines = stdout.strip().split('\n')[1:]  # Skip header
            pids = []
            for line in lines:
                if line.strip():
                    parts = line.split(',')
                    if len(parts) >= 2:
                        pid = parts[1].strip('"')
                        pids.append(pid)
            
            if pids:
                print(f"📍 Найдено {len(pids)} Python процессов: {', '.join(pids)}")
                for pid in pids:
                    print(f"   Останавливаю PID {pid}...")
                    run_command(f'taskkill /F /PID {pid}')
            else:
                print("✅ Активных Python процессов не найдено")
    else:
        # Linux/Unix
        code, stdout, stderr = run_command("ps aux | grep python")
        if code == 0:
            processes = [line for line in stdout.split('\n') if 'app.main' in line or 'schedulebot' in line]
            if processes:
                print(f"📍 Найдено {len(processes)} процессов бота")
                for process in processes:
                    pid = process.split()[1]
                    print(f"   Останавливаю PID {pid}...")
                    run_command(f"kill -9 {pid}")
            else:
                print("✅ Активных процессов бота не найдено")


def check_ports():
    """Check if ports are occupied."""
    print("\n🔍 Проверка занятых портов...")
    
    ports_to_check = [8000, 5000, 3000]
    
    for port in ports_to_check:
        if os.name == 'nt':
            code, stdout, stderr = run_command(f'netstat -ano | findstr ":{port}"')
        else:
            code, stdout, stderr = run_command(f"lsof -i :{port}")
        
        if code == 0 and stdout.strip():
            print(f"⚠️  Порт {port} занят:")
            for line in stdout.strip().split('\n'):
                print(f"     {line}")
        else:
            print(f"✅ Порт {port} свободен")


def clear_telegram_webhook():
    """Clear Telegram webhook if set."""
    print("\n🧹 Очистка Telegram webhook...")
    
    # Try to get bot token from environment or config
    bot_token = None
    
    # Check environment variable
    bot_token = os.environ.get('BOT_TOKEN')
    
    # Try to read from config if available
    if not bot_token:
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
            from app.config import settings
            bot_token = settings.BOT_TOKEN
        except:
            pass
    
    if bot_token:
        import requests
        try:
            # Delete webhook
            url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    print("✅ Webhook удален")
                else:
                    print(f"⚠️  Ошибка удаления webhook: {data.get('description', 'Неизвестная ошибка')}")
            else:
                print(f"⚠️  HTTP {response.status_code} при удалении webhook")
                
            # Check webhook status
            url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    webhook_info = data.get('result', {})
                    webhook_url = webhook_info.get('url', '')
                    if webhook_url:
                        print(f"⚠️  Webhook все еще установлен: {webhook_url}")
                    else:
                        print("✅ Webhook не установлен")
            
        except Exception as e:
            print(f"❌ Ошибка при работе с webhook: {e}")
    else:
        print("⚠️  BOT_TOKEN не найден, пропускаю очистку webhook")


def main():
    """Main function."""
    print("=" * 60)
    print("🛑 AGU ScheduleBot - Остановка локальных экземпляров")
    print("=" * 60)
    
    kill_python_processes()
    check_ports()
    clear_telegram_webhook()
    
    print("\n" + "=" * 60)
    print("✅ Очистка завершена!")
    print("\n💡 Рекомендации:")
    print("   1. Убедись, что бот запущен только на Render")
    print("   2. Проверь переменные окружения на Render")
    print("   3. Если проблема повторяется - перезапусти сервис на Render")
    print("=" * 60)


if __name__ == "__main__":
    main()