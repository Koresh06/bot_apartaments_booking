FROM python:3.11-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /code

RUN apt-get update && apt-get install -y python3-dev

RUN pip install --upgrade pip && \
    pip install poetry

COPY pyproject.toml poetry.lock /code/

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

EXPOSE 8050

COPY . /code/