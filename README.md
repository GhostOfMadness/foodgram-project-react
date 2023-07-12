#  Foodgram

## О проекте

Foodgram - сервис, позволяющий вам полностью погрузиться в удивительный мир кулинарии. Здесь вы найдете рецепты для любого повода, изысканный ужин с лобстерами или сырники с малиновым соусом на завтрак - решать только вам. Добавляйте понравившиеся рецепты в избранное, чтобы не потерять их, подписывайтесь на интересных авторов. А когда решите что-то приготовить, обязательно добавьте рецепты в список покупок, чтобы скачать полный список необходимых ингредиентов.


## Технологии

Frontend проекта написан на [React](https://ru.legacy.reactjs.org) (JS), backend - на [Django](https://www.djangoproject.com) (Python).
При развертывании проекта использован веб-сервер [NGINX](https://nginx.org/ru/), WSGI-сервер [Gunicorn](https://gunicorn.org) и [Docker](https://www.docker.com).

## Конфигурация

Контейнеры Docker:
1. db
2. backend
3. frontend
4. nginx

Файлы docker-compose:
1. `infra/docker-compose.yml` - для локального запуска.
2. `docker-compose.production.yml` - для запуска на сервере.

## Локальный запуск

Для локального запуска контейнеров Docker необходимо создать файл `.env` в корне проекта:
```shell
cp .env.exemple .env
```

Переменные окружения в .env.example:
```shell
ENV=.env

# Django settings
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=<host1 host2 host3 ...>
DJANGO_SECRET_KEY=<your-django-secret-key>
DJANGO_CSRF_TRUSTED_ORIGINS=<trusted-hosts>
MODEL_STR_MAX_LENGTH=30 # длина строки при вызове метода str() моделей
ADMIN_INLINE_LEN=1 # количество строк под ManyToMany поля в админ-зоне

# Django Rest Framework
DEFAULT_PAGE_SIZE=6

# Database
POSTGRES_USER=db_user_username
POSTGRES_PASSWORD=db_user_password
POSTGRES_NAME=db_name
DB_HOST=db_container_name
DB_PORT=5432
```

Далее необходимо перейти в директорию `infra` и выполнить следующие команды:
```shell
docker compose build
docker compose up
```

## Дополнительные возможности

Помимо имеющихся команд Django добавлена возможность загрузки данных из файлов внутри директории `/backend/data/`. Для быстрого заполнения базы данных выполните представленную ниже команду из директории `infra`:
```shell
docker compose exec backend python manage.py upload_json
```
Если необходимо полностью очистить базу данных от всех записей используйте:
```shell
docker compose exec backend python manage.py clear_database
```

## Информация

* *Адрес проекта*: https://ghostofmadnessnn.hopto.org/
* *Логин администратора*: admin@foodgram.com
* *Пароль администратора*: admin
