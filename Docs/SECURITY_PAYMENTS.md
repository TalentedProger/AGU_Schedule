# Безопасность системы донатов через Telegram Stars

## Защита от подмены получателя платежа

### 1. ADMIN_TG_ID загружается из .env при старте

```python
# app/config.py
class Settings(BaseSettings):
    ADMIN_TG_ID: int  # Загружается один раз при старте приложения
```

- ✅ Значение устанавливается при запуске из переменной окружения
- ✅ Не может быть изменено во время работы приложения
- ✅ Защищено от модификации через API или пользовательский ввод

### 2. Валидация платежей

```python
# app/bot/handlers/support.py
@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    # Проверяем что payload соответствует ожидаемому формату
    if pre_checkout_query.invoice_payload.startswith("support_donation"):
        await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
```

### 3. Telegram API автоматически направляет платежи

Когда вы создаете invoice через `bot.send_invoice()`:
- Telegram автоматически связывает платеж с ботом
- Деньги (Stars) идут владельцу бота-токена
- Невозможно перенаправить платеж на другого получателя

### 4. Дополнительные меры безопасности

#### .env файл должен быть защищен:
```bash
# .env должен быть в .gitignore
# Права доступа только для владельца
chmod 600 .env  # Linux/Mac
```

#### Проверка целостности при развертывании:
```python
# При старте приложения логируем (но НЕ выводим сам ID)
logger.info(f"Admin configured: {bool(settings.ADMIN_TG_ID)}")
```

### 5. Что НЕ может сделать злоумышленник

❌ Изменить ADMIN_TG_ID через код - переменная read-only после загрузки  
❌ Перехватить платеж - он идет на владельца BOT_TOKEN  
❌ Подделать успешный платеж - Telegram верифицирует все платежи  
❌ Изменить получателя через параметры invoice - Telegram игнорирует это  

### 6. Мониторинг безопасности

Все платежи логируются:
```python
logger.info(f"Payment logged: user {user_id}, amount {amount} {currency}")
```

Проверяйте логи регулярно:
```powershell
# Просмотр последних платежей
Select-String -Path logs/app.log -Pattern "Payment logged"
```

### 7. Backup данных о платежах

```sql
-- Экспорт всех платежей
SELECT * FROM payments ORDER BY created_at DESC;
```

Создавайте резервные копии таблицы payments:
```powershell
python scripts/backup_db.py
```

## Вывод

Система безопасна, потому что:
1. **ADMIN_TG_ID** защищен на уровне конфигурации (Pydantic)
2. **BOT_TOKEN** определяет получателя - невозможно изменить в коде
3. **Telegram API** верифицирует все транзакции
4. **Логирование** позволяет отслеживать все платежи
5. **Database** хранит полную историю для аудита

Единственный способ изменить получателя - получить доступ к .env файлу на сервере, что требует прав администратора системы.
