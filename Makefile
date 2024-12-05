# Переменные
PYTHON_CMD = python
MAIN_BOT_MODULE = src.main_bot
MAIN_FASTAPI_MODULE = src.main_fastapi
CREATE_SUPERUSER_SCRIPT = scripts.create_superuser

# Запуск FastAPI
start_fastapi:
	$(PYTHON_CMD) -m $(MAIN_FASTAPI_MODULE)

# Запуск бота
start_bot:
	$(PYTHON_CMD) -m $(MAIN_BOT_MODULE)

# Запуск обоих приложений (бот и FastAPI)
start_all:
	$(MAKE) start_bot & $(MAKE) start_fastapi

# Создание суперпользователя
create-superuser:
	$(PYTHON_CMD) -m $(CREATE_SUPERUSER_SCRIPT)
