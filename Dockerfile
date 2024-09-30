# Используем образ Python 3.11
FROM python:3.11-slim

# Устанавливаем необходимые системные библиотеки
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    make \  # Устанавливаем make
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
ENV POETRY_VERSION=1.8.0
RUN curl -sSL https://install.python-poetry.org | python3 - --version $POETRY_VERSION \
    && echo "export PATH=\"/root/.local/bin:$PATH\"" >> /root/.bashrc \
    && /root/.local/bin/poetry --version  # Проверка установки

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости
RUN /root/.local/bin/poetry install --no-root --only main

# Копируем код приложения
COPY . .

# Запуск Alembic для миграций
RUN /root/.local/bin/poetry run alembic upgrade head

# Указываем команду для запуска Makefile
CMD ["make", "start_all"]
