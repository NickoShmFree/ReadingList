# сервис «Reading List»

Пользователи ведут списки материалов (книги/статьи) с метками и статусами.

## Структура проекта

```
ReadingList/
├── src/
│   ├── api/                    # FastAPI эндпоинты
│   │   ├── dependencies/       # FastAPI зависимости
│   │   ├── auth.py            # Аутентификация
│   │   ├── items.py           # CRUD элементов
│   │   └── item.py            # Работа с одним элементом
│   ├── cfg/                   # Конфигурация
│   │   ├── app.py             # Настройки приложения
│   │   ├── auth.py            # Настройки аутентификации
│   │   ├── db.py              # Настройки базы данных
│   │   └── logging.py         # Настройки логирования
│   ├── db/                    # Работа с базой данных
│   │   ├── models/            # SQLAlchemy модели
│   │   ├── repo/              # Паттерн Repository
│   │   ├── services_db/       # Сервисы уровня БД
│   │   ├── connector.py       # Подключение к БД
│   │   └── provider.py        # Провайдер сервисов
│   ├── schemas/               # Pydantic схемы
│   ├── services/              # Бизнес-логика
│   │   ├── auth/              # Сервисы аутентификации
│   │   └── items.py           # Сервис элементов
│   ├── secrets/               # Секреты и конфигурации
│   │   ├── certs/             # SSL/JWT сертификаты
│   │   ├── db.env             # Конфиг базы данных
│   │   └── run_cfg.env        # Конфиг приложения
│   ├── utils/                 # Утилиты
│   └── main.py                # Точка входа
├── alembic_files/             # Миграции базы данных
├── docker-compose.yml         # Docker Compose конфиг
├── Dockerfile                 # Docker образ приложения
└── pyproject.toml             # Зависимости
```

## Старт приложения

1. Переименовать secrets_example в secrets (mv src/secrets_example src/secrets)
2. Создать папку mkdir -p src/secrets/certs
3. Перейти в нее (cd src/secrets/certs)
4. Сгенерировать приватный и публичный ключи:

   ### Генерация RSA приватного ключа (2048 бит)

   openssl genrsa -out jwt-private.pem 2048

   ### Извлечение публичного ключа из пары

   openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem

5. Вернуться в исходную папку (cd ../../..)
6. Запустить приложение (docker-compose up -d)
7. Проверить работоспособность
   - Приложение доступно по адресу: http://localhost:8000
   - Документация API (Swagger): http://localhost:8000/docs
   - Альтернативная документация (ReDoc): http://localhost:8000/redoc

в миграции e0c62369b82d\_.py находятся данные для тестирования при развертывании автоматически занесутся в БД

### Данные аунтификации для тестирования

         Логин       │  Пароль  │       Имя
    ivan@example.com │  secret  │  Иван Тестовый (id=1)
    anna@example.com │  secret  │  Анна Тестова (id=2)
