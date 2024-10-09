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

# Открываем порт 8000 для входа в контейнер
EXPOSE 8000

# Запускаем команду для запуска бота
CMD ["python", "-m", "src.__main__"]

