# Локальный стенд: Nginx + FastAPI + PostgreSQL + Redis

## Состав

| Сервис    | Роль                                   | Порт (host)      |
|-----------|-----------------------------------------|-------------------|
| nginx     | Reverse proxy, TLS termination          | 80 → 443 redirect, **443** |
| backend   | FastAPI-приложение                      | 8080 (только внутри сети) |
| db        | PostgreSQL 15                           | 5432 (внутри сети) |
| redis     | Redis (кэш сессий)                      | 6379 (внутри сети) |

# Быстрый старт 

## Если нет makefile
### на Linux (Ubuntu / Debian / Mint)
```bash
sudo apt install -y make
 ```
### Если ты на macOS
``` 
xcode-select --install
```

### Если ты на Windows
```
choco install make
```

# Запуск и проверка
```bash
make start
```

Ожидаемый ответ:
```json
{
  "message": "Hello from FastAPI backend",
  "redis_visits": 1,
  "postgres_status": "ok, rows=1",
  "client_headers": {
    "x-forwarded-for": "172.x.x.x",
    "x-forwarded-proto": "https",
    "x-forwarded-host": "localhost",
    "host": "localhost"
  }
}
```


## Остановка контейнеров

```bash
docker compose down  
```

## Примечания по безопасности (production-ready подход)

- Все пароли вынесены в `.env`, который добавлен в `.gitignore`.
- Backend не публикует порт наружу — доступен только через nginx по сети Docker.
- Backend-контейнер работает от непривилегированного пользователя (`app`).
- Redis защищён паролем (`--requirepass`).
- TLS 1.2/1.3 only, слабые шифры отключены.
- Для production self-signed сертификат нужно заменить на сертификат от
  реального CA (например, Let's Encrypt).
