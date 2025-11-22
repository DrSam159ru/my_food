# Foodgram — продуктовый помощник

Foodgram — это онлайн-сервис для публикации рецептов и управления покупками.  
Пользователи могут:

- регистрироваться и авторизоваться;
- создавать и редактировать рецепты;
- добавлять рецепты в избранное;
- формировать список покупок и выгружать его в `.txt`;
- подписываться на авторов и следить за их новыми рецептами;
- делиться короткими ссылками на рецепты.

Проект состоит из **Django REST API** (backend) и **React-SPA** (frontend), упакованных в Docker и готовых к деплою за nginx.

---

## Содержание

- [Технологии](#технологии)
- [Архитектура и структура проекта](#архитектура-и-структура-проекта)
- [Основной функционал](#основной-функционал)
- [API и документация](#api-и-документация)
- [Переменные окружения](#переменные-окружения)
- [Запуск в Docker (prod)](#запуск-в-docker-prod)
- [Локальный запуск backend без Docker](#локальный-запуск-backend-без-docker)
- [Импорт ингредиентов](#импорт-ингредиентов)
- [Модели данных](#модели-данных)
- [Проверка качества кода](#проверка-качества-кода)
- [Полезные команды](#полезные-команды)

---

## Технологии

### Backend

- Python 3.10
- Django 5.1
- Django REST Framework
- Djoser (аутентификация по токену)
- drf-spectacular (OpenAPI/Swagger/Redoc)
- PostgreSQL
- Gunicorn
- Nginx
- Docker / Docker Compose

### Frontend

- React 17 (CRA)
- React Router
- Сборка через `react-scripts`
- Сборка и отдача статики через отдельный Docker-контейнер

---

## Архитектура и структура проекта

Корень проекта:

```text
foodgram/
├─ backend/          # Django-проект (API + админка)
├─ frontend/         # React-приложение
├─ infra/            # Docker Compose и конфиг nginx
├─ docs/             # OpenAPI схема и HTML-версия документации
├─ data/             # Данные для импорта ингредиентов
├─ .env              # Переменные окружения (пример для dev)
└─ README.md         # Описание проекта

--> Основные приложения backend:

users — кастомная модель пользователя, аватары, подписки (Follow).

recipes — рецепты, ингредиенты, теги, связь рецепт–ингредиенты.

favorites — избранные рецепты.

shopping — список покупок.

shortlinks — короткие ссылки на рецепты.

api — маршруты и фильтры DRF.

core — общие утилиты, пагинация, permissions.

--> Основной функционал

- Пользователи
Регистрация и авторизация по email/паролю (через Djoser + authtoken).

Профиль пользователя:

username, first_name, last_name, email;

аватар (хранится в медиа, путь avatars/<user_id>/...);

флаг is_subscribed в API.

Изменение пароля.

Получение данных о текущем пользователе (/api/users/me/).

- Подписки
Подписка на автора: POST /api/users/{id}/subscribe/

- Отписка: DELETE /api/users/{id}/subscribe/

- Список подписок: GET /api/users/subscriptions/

В списке подписок показываются рецепты автора (с возможностью ограничить количество рецептов параметром recipes_limit).

- Рецепты
Рецепт включает:

название;
автора;
изображение;
текстовое описание;
время приготовления (с валидацией на минимальное значение);
теги;
ингредиенты (через промежуточную модель с количеством).

- Операции:

Список рецептов: GET /api/recipes/
Получение одного рецепта: GET /api/recipes/{id}/
Создание рецепта: POST /api/recipes/
Обновление рецепта: PATCH /api/recipes/{id}/
Удаление рецепта: DELETE /api/recipes/{id}/

- Рецепт можно пометить как:

избранный (POST/DELETE /api/recipes/{id}/favorite/);
в корзине (POST/DELETE /api/recipes/{id}/shopping_cart/).

- Фильтрация:

по автору: ?author=<user_id>;
по тегам (slug тегов): ?tags=breakfast&tags=lunch;
только избранные: ?is_favorited=1;
только в списке покупок: ?is_in_shopping_cart=1.

- Ингредиенты и теги
GET /api/tags/, GET /api/tags/{id}/
GET /api/ingredients/ — поиск по началу названия:
GET /api/ingredients/?name=сах найдёт «Сахар» и т.п.

- Импорт ингредиентов из файла (см. Импорт ингредиентов).

## Избранное
Добавление рецепта в избранное:
POST /api/recipes/{id}/favorite/

Удаление:
DELETE /api/recipes/{id}/favorite/

Фильтр is_favorited=1 возвращает только избранные рецепты текущего пользователя.

- Список покупок
Добавление рецепта в список покупок:
POST /api/recipes/{id}/shopping_cart/

Удаление:
DELETE /api/recipes/{id}/shopping_cart/

Выгрузка общего списка ингредиентов по всем рецептам в корзине:
GET /api/recipes/download_shopping_cart/

Возвращается текстовый файл shopping_list.txt с агрегированными количествами.

- Короткие ссылки
Для рецепта генерируется короткая ссылка:
GET /api/recipes/{id}/get-link/ → {"short-link": "https://<host>/s/<code>"}.

Переход по короткой ссылке:
GET /s/<code>/ — редирект на страницу рецепта на фронтенде (FRONTEND_BASE_URL/recipes/{id}).

- API и документация
Базовый префикс API: https://<host>/api/.

- Основные группы маршрутов:
api/auth/token/login/ — получить токен (email + пароль).
api/auth/token/logout/ — удалить токен.
api/users/ — пользователи.
api/users/me/ — текущий пользователь.
api/users/subscriptions/ — подписки.
api/users/{id}/subscribe/ — подписка/отписка.
api/recipes/, api/recipes/{id}/ — рецепты.
api/tags/, api/ingredients/ — справочники.

- Документация:

Swagger UI: GET /api/docs/
ReDoc: GET /api/redoc/
OpenAPI схема: GET /api/schema/

--> Переменные окружения
Все переменные читаются из .env. Основные:

DJANGO_SECRET_KEY
DJANGO_DEBUG
DJANGO_SETTINGS_MODULE
ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS
DB_ENGINE
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
DB_HOST
DB_PORT	
TIME_ZONE
SHORTLINK_CODE_LENGTH
SHORTLINK_MAX_ATTEMPTS
FRONTEND_BASE_URL
BACKEND_BASE_URL
USE_SECURE_PROXY


*** Запуск в Docker (prod)
- Предварительные требования - установлен Docker и Docker Compose;
- настроен DNS/домен (в nginx-конфиге используется food-gram.hopto.org, при необходимости поменяйте в infra/nginx/nginx.conf и docker-compose.prod.yml);
- заполнен файл .env в корне проекта.

-> Шаги
- Клонировать репозиторий и перейти в папку проекта:

git clone <url-репозитория> foodgram
cd foodgram

- Отредактировать .env под своё окружение.

- Запустить Docker-сервисы:

cd infra
docker compose -f docker-compose.prod.yml up -d --build

Будут подняты контейнеры:

db — PostgreSQL;
backend — Django + Gunicorn;
frontend — сборка React + копирование статики;
nginx — отдача статики и проксирование на backend;
certbot — обновление SSL-сертификатов (при наличии корректного домена).

Проверить, что всё работает:

Админка: https://<host>/admin/
API: https://<host>/api/recipes/
Документация: https://<host>/api/docs/ или https://<host>/api/redoc/

Backend при старте автоматически:

применяет миграции;
собирает статику;
пытается импортировать ингредиенты из backend/data/ingredients.json или backend/data/ingredients.csv.

*** Локальный запуск backend без Docker (Альтернатива для разработки).

Создать и активировать виртуальное окружение:

cd backend
python -m venv venv
source venv/bin/activate      # Linux/macOS
# или
venv\Scripts\activate         # Windows

Установить зависимости:

pip install --upgrade pip
pip install -r requirements.txt
Создать .env в корне проекта (где manage.py) и прописать переменные окружения.

Применить миграции и импортировать ингредиенты:

python manage.py migrate
python manage.py load_ingredients --path data/ingredients.json
# или
python manage.py load_ingredients --path data/ingredients.csv

Создать суперпользователя:

python manage.py createsuperuser
Запустить сервер разработки:

python manage.py runserver
Backend будет доступен по адресу http://127.0.0.1:8000/.

--> Импорт ингредиентов
Для удобства заполнения базы есть management-команда:

python manage.py load_ingredients --path data/ingredients.json
# или
python manage.py load_ingredients --path data/ingredients.csv
Поддерживаются форматы JSON и CSV.

Требуемые поля: name, measurement_unit.

Команда пропускает дубликаты с тем же name + measurement_unit.

В Docker-окружении импорт выполняется автоматически при старте backend (см. backend/recipes/management/commands/backend-entrypoint.sh).

Автор: Andrew Moshchuk
GitHub: https://github.com/DrSam159ru/foodgram
Москва - 2025