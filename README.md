<img src="static/chisato-icon-small.jpg" alt="Chisato" width="300" />

# Chisato

An osu! collection showcase and backup.

## Start developing Chisato

This project required

- [Python 3.11](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)

Copy `.env.example` to `.env` and fill the value

```bash
cat .env.example > .env
```

Install dependencies

```bash
poetry install
```

Migrate database

```bash
poetry run python manage.py migrate
```

Run server

```bash
poetry run python manage.py runserver
```

If you want to stay in the poetry shell, you can run

```bash
poetry shell
```

RabbitMQ Docker

```bash
docker run -d --hostname my-rabbit --name some-rabbit -p 5672:5672 -p 15672:15672 -e RABBITMQ_DEFAULT_USER=user -e RABBITMQ_DEFAULT_PASS=password rabbitmq:3-management
```