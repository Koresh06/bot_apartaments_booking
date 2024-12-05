# Используем образ Python 3.11
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /src

# Копируем файлы проекта, необходимые для установки зависимостей
COPY pyproject.toml poetry.lock /src/

# Устанавливаем Poetry
RUN pip install --upgrade pip
RUN pip install poetry

# Устанавливаем зависимости без создания виртуальной среды
RUN poetry config virtualenvs.create false && poetry install --no-dev

# Копируем остальной код проекта в контейнер
COPY . /src

# Открываем порт 8000 для входа в контейнер
EXPOSE 8000
