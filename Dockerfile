# Используем образ Python 3.11
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /src

# Копируем файлы проекта в контейнер
COPY pyproject.toml poetry.lock /src/

# Устанавливаем Poetry и зависимости
RUN pip install poetry && poetry config virtualenvs.create false && poetry install --no-dev

# Копируем остальной код проекта в контейнер
COPY . /src

# Запускаем команду для запуска бота
CMD ["python", "-m", "__main__"]

