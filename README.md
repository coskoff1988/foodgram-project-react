# Foodgram

Foodgram - это приложение для обмена рецептами, где пользователи могут создавать и делиться рецептами, подписываться на других пользователей и отслеживать новые рецепты.

## Запуск проекта  

Инструкция по запуску проекта локально для разработки и тестирования.

### Требования

- Docker and Docker Compose

### Установка

1. Клонируйте репозиторий:

```
git clone https://github.com/coskoff1988/foodgram-project-react
```

2. Создайте файл `.env` со следующими переменными:  

```
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432  
SECRET_KEY=<secret-key>
DEBUG=False
ALLOWED_HOSTS=localhost 127.0.0.1 
```

3. Запустите контейнеры:

```
docker-compose up -d --build
```

4. Примените миграции:

```
docker-compose exec backend python manage.py migrate
```

5. Соберите статику:

```  
docker-compose exec backend python manage.py collectstatic
```

Приложение должно быть доступно по адресу http://localhost:9080  

## Использованные технологии

- [Django](https://www.djangoproject.com/) - Веб фреймворк
- [Django REST Framework](https://www.django-restframework.org/) - Фреймворк для REST API   
- [React](https://reactjs.org/) - Фреймворк для frontend
- [PostgreSQL](https://www.postgresql.org/) - База данных  
- [Docker](https://www.docker.com/) - Контейнеризация


## Данные для проверки работы проекта

- ip: 51.250.19.172:9080
- login: admin@mail.ru
- password: admin

## Автор  

*Леонид Косков*

