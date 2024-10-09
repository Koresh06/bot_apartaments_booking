PYTHON_CMD = python
FASTAPI_APP = src.run_fastapi:app
MAIN_MODULE = src.__main__

# Запуск FastAPI
start_fastapi:
	$(PYTHON_CMD) -m uvicorn $(FASTAPI_APP) --reload &

# Запуск бота
start_bot:
	$(PYTHON_CMD) -m $(MAIN_MODULE) &

# Запуск обоих приложений
start_all:
	$(MAKE) start_fastapi
	$(MAKE) start_bot

# Остановка всех приложений
stop:
	@pkill -f 'uvicorn' || true
	@pkill -f 'python -m src.__main__' || true

