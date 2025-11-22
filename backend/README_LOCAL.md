# Local Docker Setup (Foodgram)

## 1) Куда класть файлы
- `settings_prod.py` — перенеси в свой проект под `foodgram/settings_prod.py`
- `.env.local.example` — скопируй в корень проекта как `.env` и поправь значения
- Папка `infra/` — запускаем docker compose из неё
- Папка `backend/` — Dockerfile и requirements; `context: ..` ожидает, что `infra/` и `backend/` лежат рядом с проектом

Структура (рекомендуемая):
```
your-project/
├─ manage.py
├─ foodgram/
│  ├─ settings.py
│  └─ settings_prod.py     <-- из этого набора
├─ apps...
├─ requirements.txt        (ваш реальный requirements)
├─ .env                    <-- из .env.local.example
├─ backend/
│  └─ Dockerfile           <-- из набора (можно использовать ваш)
└─ infra/
   ├─ docker-compose.yml
   ├─ docker-compose.dev.yml
   ├─ nginx.conf
   ├─ backend-entrypoint.sh
   └─ backend-entrypoint.dev.sh
```

> В `docker-compose.yml` смонтирован volume `../:/app` — укажите правильный путь, чтобы внутри контейнера `backend` был **ваш** код.

## 2) .env (для локалки)
Скопируйте `.env.local.example` в `.env`. Важно:
```
DJANGO_SETTINGS_MODULE=foodgram.settings_prod
DEBUG=1
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1
POSTGRES_*  # как заданы по умолчанию
```

## 3) Первый старт
```bash
cd infra
# prod-like локально (gunicorn + nginx)
docker compose up -d --build
# или режим dev (live-reload через runserver)
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

# создать суперпользователя
docker compose exec backend python manage.py createsuperuser
```

Проверки:
- http://localhost/admin/
- http://localhost/api/tags/ , /api/ingredients/ , /api/recipes/

## 4) Полезное
- Логи: `docker compose logs -f backend` / `docker compose logs -f nginx` / `docker compose logs -f db`
- Миграции: `docker compose exec backend python manage.py makemigrations && docker compose exec backend python manage.py migrate`
- Сброс статик: `docker compose exec backend python manage.py collectstatic --noinput`
- Обновление зависимостей: изменили `requirements.txt` → пересоберите `backend` (`--build`)

## 5) Частые вопросы
- **Почему 502/404 через nginx?** Проверьте, что `backend` слушает 0.0.0.0:8000 и контейнер жив.
- **Монтирование кода:** volume `../:/app` может перекрыть файлы, скопированные на этапе `COPY` в Dockerfile — это нормально для dev.
- **SQLite vs Postgres:** В этом окружении используется Postgres (как в проде). Если хотите SQLite, запускайте без `db` и укажите в `.env` `DJANGO_SETTINGS_MODULE=foodgram.settings` (ваши dev-настройки) и поправьте `DATABASES` там.
