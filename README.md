# Chisato

An osu! collection showcase and backup.

# About Chisato

This is the next version of [beattpsetto](https://github.com/beattosetto/beattosetto) which is a collection showcase and backup for osu!.
This project's structure has changed a lot from the previous version, allow more flexibility and easier to add the functionality to it.

Current this project is in beta phase (usable now but some function is not available yet), you can try it out at [chisato.app](https://chisato.app).

You can report any issue or suggestion by creating a new issue in this repository.

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

Export `requirements.txt`

```bash
poetry export --without-hashes --format=requirements.txt > requirements.txt
```