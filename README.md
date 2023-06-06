# TSK.Network

## Запуск проекта для разработки

Команды нужно выполнять в папке проекта /djproject

Сначала рекомендуется создать виртуальное окружение, например, с помощью следующих команд:

- `python -m venv venv` - создание виртуального окружения
- `source venv/bin/activate` - войти в виртуальное окружение

Далее:

- `pip install -r requirements.txt` - установка зависимостей
- `docker-compose up -d` – запуск баз данных Neo4j и PostgreSQL
- `python manage.py migrate` – применение миграций к PostgreSQL
- `python manage.py runserver` - запустить сервер для разработки на http://127.0.0.1:8000
