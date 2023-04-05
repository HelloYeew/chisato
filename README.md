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