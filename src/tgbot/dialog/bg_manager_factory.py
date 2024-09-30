from typing import Optional
from aiogram import Bot
from aiogram_dialog import BaseDialogManager, BgManagerFactory




class MyDialogManager(BaseDialogManager):
    def __init__(self, bot: Bot, user_id: int, chat_id: int):
        super().__init__()
        self.bot = bot
        self.user_id = user_id  # Сохраняем user_id
        self.chat_id = chat_id
        self.current_state = None
        self.data = {}

    async def done(self, result=None, show_mode=None):
        """Завершает диалог и возвращает результат."""
        if result:
            print("Диалог завершен с результатом:", result)
        self.current_state = None  # Убираем текущее состояние

    async def start(self, state, data=None, mode=None, show_mode=None, access_settings=None):
        """Запускает новый диалог."""
        self.current_state = state  # Устанавливаем новое состояние
        self.data = data if data else {}

        # Инициализация диалога
        print("Диалог начат с состоянием:", state, "и данными:", data)

        # Отправка сообщения пользователю
        await self.send_message("Диалог начат!")

    async def switch_to(self, new_state: str, data: Optional[dict] = None):
        """Переключает на новое состояние диалога."""
        self.current_state = new_state  # Устанавливаем новое состояние
        if data:
            self.data.update(data)  # Обновляем данные

        print("Переключение на новое состояние:", new_state)

        # Отправляем сообщение о переключении
        await self.send_message(f"Переключение на состояние: {new_state}")

    async def update(self, **kwargs):
        """Обновляет состояние диалога."""
        self.data.update(kwargs)

        print("Обновление состояния:", kwargs)

        await self.send_message("Состояние обновлено!")

    async def send_message(self, text: str):
        """Отправка сообщения пользователю."""
        await self.bot.send_message(self.chat_id, text)
        print("Отправка сообщения:", text)

    async def bg(self, *args, **kwargs):
        """Логика для обработки состояния в фоновом режиме."""
        # Здесь вы можете реализовать необходимую логику
        print("Фоновая логика обработки...")

        # Например, вы можете отправить сообщение
        await self.send_message("Фоновая обработка завершена!")

    async def load_state(self, user_id: int):
        """Загружает состояние пользователя из базы данных."""
        # Здесь вы можете реализовать логику загрузки состояния из БД
        # Например, возвращаем фиксированное состояние
        return {
            "current_state": "initial_state",
            "data": {"key": "value"},
        }


class MyBgManagerFactory(BgManagerFactory):
    async def bg(
        self,
        bot: Bot,
        user_id: int,
        chat_id: int,
        stack_id: Optional[str] = None,
        thread_id: Optional[int] = None,
        business_connection_id: Optional[str] = None,
        load: bool = False,
    ) -> "BaseDialogManager":
        # Создаем экземпляр DialogManager для пользователя
        dialog_manager = MyDialogManager(
            bot=bot,
            user_id=user_id,
            chat_id=chat_id,
            stack_id=stack_id,
            thread_id=thread_id,
            business_connection_id=business_connection_id,
            load=load,
        )

        # Здесь вы можете установить параметры, если нужно
        if load:
            # Логика загрузки состояния пользователя и чата
            pass

        # Возвращаем экземпляр
        return dialog_manager
