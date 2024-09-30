from aiogram import F
from aiogram.types import ContentType
from aiogram_dialog import Dialog, StartMode, Window
from aiogram_dialog.widgets.text import Format, Const, Multi
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Next,
    Row,
    Back,
    Group,
    SwitchTo,
    Start,
    NumberedPager,
    StubScroll,
)

from .states import (
    EditApartmentSG,
    MenuLandlordSG,
    RegisterApartmentSG,
    LandlordApartmentsSG,
)
from .getters import (
    getter_catalog_landlord_apartments,
    getter_confirm_edit_photos,
    getter_edit_apartment,
    getter_edit_apartment_photos,
    getter_get_media,
    getter_apartment_details,
    getter_is_available,
)
from .handlers import (
    confirm_photos,
    edit_data,
    handle_update_is_available,
    on_delete,
    on_delete_apartment,
    on_input_photo,
    on_next,
    on_prev,
    skip_apartment_number_handler,
    error_handler,
    update_apartment_information,
    close_dialog,
    handle_update_apartment_photos,
)


menu_loandlord_dialog = Dialog(
    Window(
        Const("Меню арендодателя"),
        Start(
            Const("Регистрация апартамента"),
            id="register_apartament",
            state=RegisterApartmentSG.city,
        ),
        Start(
            Const("Мои апартаменты"),
            id="current_apartments",
            state=LandlordApartmentsSG.catalog,
        ),
        state=MenuLandlordSG.start,
    ),
)


register_apartament_dialog = Dialog(
    Window(
        Multi(
            Const("Укажите название города:"),
            Format("Название города: {name}", when="name"),
            sep="\n\n",
        ),
        TextInput(
            id="city",
            type_factory=str,
            on_success=Next(),
            on_error=error_handler,
        ),
        Row(
            Start(
                Const("◀️ Назад"),
                id="cancel_form_register",
                state=MenuLandlordSG.start,
                show_mode=StartMode.RESET_STACK,
            ),
            Next(when="name"),
        ),
        state=RegisterApartmentSG.city,
    ),
    Window(
        Multi(
            Const("Отправьте название улицы:"),
            Format("Название улицы: {street}", when="street"),
            sep="\n\n",
        ),
        TextInput(
            id="street",
            type_factory=str,
            on_success=Next(),
            on_error=error_handler,
        ),
        Row(
            Back(Const("⬅️ Назад")),
            Next(when="street"),
        ),
        state=RegisterApartmentSG.street,
    ),
    Window(
        Multi(
            Const("Отправьте номер дома:"),
            Format("Номер дома: {house_number}", when="house_number"),
            sep="\n\n",
        ),
        TextInput(
            id="house_number",
            type_factory=int,
            on_success=Next(),
            on_error=error_handler,
        ),
        Row(
            Back(Const("⬅️ Назад")),
            Next(when="house_number"),
        ),
        state=RegisterApartmentSG.house_number,
    ),
    Window(
        Multi(
            Const("Отправьте номер квартиры (если необходимо!):"),
            Format("Номер квартиры: {apartment_number}", when="apartment_number"),
            sep="\n\n",
        ),
        TextInput(
            id="apartment_number",
            type_factory=int,
            on_success=Next(),
            on_error=error_handler,
        ),
        Button(Const("Пропустить"), id="skip", on_click=skip_apartment_number_handler),
        Back(Const("◀️ Назад")),
        Next(when="apartment_number"),
        state=RegisterApartmentSG.apartment_number,
    ),
    Window(
        Multi(
            Const("Отправьте цену за день:"),
            Format("Цена за день: {price_per_day}", when="price_per_day"),
            sep="\n\n",
        ),
        TextInput(
            id="price_per_day",
            type_factory=float,
            on_success=Next(),
            on_error=error_handler,
        ),
        Row(
            Back(Const("⬅️ Назад")),
            Next(when="price_per_day"),
        ),
        state=RegisterApartmentSG.price_per_day,
    ),
    Window(
        Multi(
            Const("Отправьте количество комнат:"),
            Format("Количество комнат: {rooms}", when="rooms"),
            sep="\n\n",
        ),
        TextInput(
            id="rooms",
            type_factory=int,
            on_success=Next(),
            on_error=error_handler,
        ),
        Row(
            Back(Const("⬅️ Назад")),
            Next(when="rooms"),
        ),
        state=RegisterApartmentSG.rooms,
    ),
    Window(
        Multi(
            Const("Отправьте описание вашего апартамента:"),
            Format("Описание апартамента: {description}", when="description"),
            sep="\n\n",
        ),
        TextInput(
            id="description",
            type_factory=str,
            on_success=Next(),
            on_error=error_handler,
        ),
        Row(
            Back(Const("⬅️ Назад")),
            Next(when="description"),
        ),
        state=RegisterApartmentSG.description,
    ),
    Window(
        Const("Отправьте фото вашего апартамента (можно сразу группой фото)"),
        DynamicMedia(selector="media"),
        StubScroll(id="pages", pages="media_count"),
        Group(
            NumberedPager(scroll="pages", when=F["pages"] > 1),
            width=8,
        ),
        Button(
            Format("🗑️ Удалить фото #{media_number}"),
            id="del",
            on_click=on_delete,
            when="media_count",
            # Alternative F['media_count']
        ),
        MessageInput(content_types=[ContentType.PHOTO], func=on_input_photo),
        Next(Const("Далее"), id="confirm_photos", when="confirm"),
        Back(Const("◀️ Назад"), id="back"),
        state=RegisterApartmentSG.photo,
        getter=getter_get_media,
    ),
    Window(
        Format(
            "<b>Город: {city}</b>\n"
            "<b>Улица: {street}</b>\n"
            "<b>Дом: {house_number}</b>\n"
            "<b>Квартира: {apartment_number}</b>\n"
            "<b>Цена за день: {price_per_day}</b>\n"
            "<b>Комнат: {rooms}</b>\n"
            "<b>Описание: {description}</b>\n"
        ),
        DynamicMedia(selector="media"),
        StubScroll(id="pages", pages="media_count"),
        Group(
            NumberedPager(scroll="pages", when=F["pages"] > 1),
            width=8,
        ),
        Button(Const("Подтвердить"), id="confirm", on_click=confirm_photos),
        Start(
            Const("❌ Отмена"),
            id="cancel_form_register",
            state=MenuLandlordSG.start,
            show_mode=StartMode.RESET_STACK,
        ),
        state=RegisterApartmentSG.confirm,
        getter=getter_get_media,
    ),
)


my_apartmernt_landlord_dialog = Dialog(
    Window(
        Format(
            "<b>Город: {apartment[city]}</b>\n"
            "<b>Улица: {apartment[street]}</b>\n"
            "<b>Дом: {apartment[house_number]}</b>\n"
            "<b>Квартира: {apartment[apartment_number]}</b>\n"
            "<b>Цена за день: {apartment[price_per_day]}</b>\n"
            "<b>Комнат: {apartment[rooms]}</b>\n"
            "<b>Описание: {apartment[description]}</b>\n"
            "<b> Статус: {apartment[is_available]}</b>\n"
        ),
        DynamicMedia(selector="media"),
        Next(Const("Детали"), id="details"),
        Row(
            Button(Const("◀️ Назад"), id="next", on_click=on_prev),
            Button(
                Format("{current_page}/{count_page}"),
                id="paginator",
            ),
            Button(Const("Вперед ▶️"), id="prev", on_click=on_next),
            when="is_apartments",
        ),
        Button(Const("Редактировать"), id="edit", on_click=edit_data),
        Button(Const("Удалить"), id="delete", on_click=on_delete_apartment),
        Start(
            Const("◀️ Назад"),
            id="back",
            state=MenuLandlordSG.start,
            show_mode=StartMode.RESET_STACK,
        ),
        state=LandlordApartmentsSG.catalog,
        getter=getter_catalog_landlord_apartments,
    ),
    Window(
        Format(
            "<b>Город: {apartment[city]}</b>\n"
            "<b>Улица: {apartment[street]}</b>\n"
            "<b>Дом: {apartment[house_number]}</b>\n"
            "<b>Квартира: {apartment[apartment_number]}</b>\n"
            "<b>Цена за день: {apartment[price_per_day]}</b>\n"
            "<b>Комнат: {apartment[rooms]}</b>\n"
            "<b>Описание: {apartment[description]}</b>\n"
            "<b> Статус: {apartment[is_available]}</b>\n"
        ),
        DynamicMedia(selector="media"),
        StubScroll(id="pages", pages="media_count"),
        Group(
            NumberedPager(scroll="pages", when=F["pages"] > 1),
            width=8,
        ),
        Back(Const("◀️ Назад"), id="back", show_mode=StartMode.RESET_STACK),
        state=LandlordApartmentsSG.details,
        getter=getter_apartment_details,
    ),
)


edit_apartment_dialog = Dialog(
    Window(
        Format("Панель редактирования апартамента: #{apartment_id}"),
        Group(
            SwitchTo(Const("Город"), id="city", state=EditApartmentSG.city),
            SwitchTo(Const("Улица"), id="street", state=EditApartmentSG.street),
            SwitchTo(
                Const("Дом"), id="house_number", state=EditApartmentSG.house_number
            ),
            SwitchTo(
                Const("Квартира"),
                id="apartment_number",
                state=EditApartmentSG.apartment_number,
            ),
            SwitchTo(
                Const("Цена за день"),
                id="price_per_day",
                state=EditApartmentSG.price_per_day,
            ),
            SwitchTo(Const("Комнат"), id="rooms", state=EditApartmentSG.rooms),
            SwitchTo(
                Const("Описание"), id="description", state=EditApartmentSG.description
            ),
            SwitchTo(Const("Фото"), id="photo", state=EditApartmentSG.photo),
            id="edit_group",
            width=4,
        ),
        Button(
            Format("Статус: {is_available}"),
            id="is_available",
            on_click=handle_update_is_available,
        ),
        Start(
            Const("◀️ Назад"),
            id="cancel_form_edit",
            state=LandlordApartmentsSG.catalog,
            show_mode=StartMode.RESET_STACK,
        ),
        state=EditApartmentSG.edit,
        getter=getter_is_available,
    ),
    Window(
        Multi(
            Format("<b>Ваше текущий город: {apartment[city]}</b>"),
            Const("Укажите новый город: "),
            sep="\n\n",
        ),
        TextInput(
            id="city",
            type_factory=update_apartment_information,
            on_error=error_handler,
        ),
        SwitchTo(Const("Назад"), id="back", state=EditApartmentSG.edit),
        state=EditApartmentSG.city,
    ),
    Window(
        Multi(
            Format("Ваша текущая улица: <b>{apartment[street]}</b>"),
            Const("Укажите новую улицу:"),
            sep="\n\n",
        ),
        TextInput(
            id="street",
            type_factory=str,
            on_success=update_apartment_information,
            on_error=error_handler,
        ),
        SwitchTo(Const("Назад"), id="back", state=EditApartmentSG.edit),
        state=EditApartmentSG.street,
    ),
    Window(
        Multi(
            Format("Ваш текущий номер дом: <b>{apartment[house_number]}</b>"),
            Const("Укажите новый номер дома:"),
            sep="\n\n",
        ),
        TextInput(
            id="house_number",
            type_factory=int,
            on_success=update_apartment_information,
            on_error=error_handler,
        ),
        SwitchTo(Const("Назад"), id="back", state=EditApartmentSG.edit),
        state=EditApartmentSG.house_number,
    ),
    Window(
        Multi(
            Format("Ваш текущий номер квартира: <b>{apartment[apartment_number]}</b>"),
            Const("Укажите новый номер квартиры:"),
            sep="\n\n",
        ),
        TextInput(
            id="apartment_number",
            type_factory=int,
            on_success=update_apartment_information,
            on_error=error_handler,
        ),
        SwitchTo(Const("Назад"), id="back", state=EditApartmentSG.edit),
        state=EditApartmentSG.apartment_number,
    ),
    Window(
        Multi(
            Format("Ваша текущая цена за день: <b>{apartment[price_per_day]}</b>"),
            Const("Укажите новую цену за день:"),
            sep="\n\n",
        ),
        TextInput(
            id="price_per_day",
            type_factory=float,
            on_success=update_apartment_information,
            on_error=error_handler,
        ),
        SwitchTo(Const("Назад"), id="back", state=EditApartmentSG.edit),
        state=EditApartmentSG.price_per_day,
    ),
    Window(
        Multi(
            Format("Ваше текущее количество комнат: <b>{apartment[rooms]}</b>"),
            Const("Укажите новое количество комнат:"),
            sep="\n\n",
        ),
        TextInput(
            id="rooms",
            type_factory=int,
            on_success=update_apartment_information,
            on_error=error_handler,
        ),
        SwitchTo(Const("Назад"), id="back", state=EditApartmentSG.edit),
        state=EditApartmentSG.rooms,
    ),
    Window(
        Multi(
            Format("Ваше текущее описание: <b>{apartment[description]}</b>"),
            Const("Укажите новое описание:"),
            sep="\n\n",
        ),
        TextInput(
            id="description",
            type_factory=str,
            on_success=update_apartment_information,
            on_error=error_handler,
        ),
        SwitchTo(Const("Назад"), id="back", state=EditApartmentSG.edit),
        state=EditApartmentSG.description,
    ),
    Window(
        Format("Ваши текущие фото:"),
        DynamicMedia(selector="media"),
        StubScroll(id="pages", pages="media_count"),
        Group(
            NumberedPager(scroll="pages", when=F["pages"] > 1),
            width=8,
        ),
        Next(Const("Изменить фото"), id="edit_photo"),
        SwitchTo(Const("Назад"), id="back", state=EditApartmentSG.edit),
        state=EditApartmentSG.photo,
        getter=getter_edit_apartment_photos,
    ),
    Window(
        Const(
            "Отправьте фото вашего апартамента (можно сразу группой фото)", when="text"
        ),
        DynamicMedia(selector="media"),
        StubScroll(id="pages", pages="media_count"),
        Group(
            NumberedPager(scroll="pages", when=F["pages"] > 1),
            width=8,
        ),
        Button(
            Format("🗑️ Удалить фото #{media_number}"),
            id="del",
            on_click=on_delete,
            when="media_count",
            # Alternative F['media_count']
        ),
        MessageInput(content_types=[ContentType.PHOTO], func=on_input_photo),
        Button(
            Const("Подтвердить"),
            id="confirm_photos",
            on_click=handle_update_apartment_photos,
            when="confirm",
        ),
        Back(Const("◀️ Назад"), id="back"),
        state=EditApartmentSG.confirm_photos,
        getter=getter_confirm_edit_photos,
    ),
    getter=getter_edit_apartment,
    on_close=close_dialog,
)
