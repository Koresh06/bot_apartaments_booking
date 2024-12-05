1. Включение UFW - sudo ufw enable
2. Проверить статус UFW - sudo ufw status
3. Открыть порт 5432 - sudo ufw allow 5432
4. Создание контейнеров - docker-compose up --build -d
4. Зайти в контейнер web и сделать миграции БД - docker-compose exec web alembic upgrade head

Создание супер пользователя
6. docker exec -it bot_apartaments_booking-web-1 sh
7. python /src/scripts/create_superuser.py
8. Указать tg_id, который будет супер пользователем (@getmy_idbot - бот в тг, где можно глянуть свой tg_id)
