import re


def name_check(text: str) -> str:
    # Удаляем пробелы и лишние символы
    name = text.strip()
    
    # Проверяем, что имя состоит только из букв и пробелов
    if not re.match(r"^[A-Za-zА-Яа-яЁё\s]+$", name):
        raise ValueError("Имя должно содержать только буквы и пробелы.")
    
    # Проверяем длину имени (например, не менее 2 и не более 50 символов)
    if len(name) < 2 or len(name) > 50:
        raise ValueError("Имя должно содержать от 2 до 50 символов.")
    
    return name


def phone_check(text: str) -> str:
    # Удаляем пробелы и лишние символы
    phone_number = text.strip()
    
    # Проверяем, что номер состоит только из цифр
    if not re.match(r"^\d+$", phone_number):
        raise ValueError("Номер телефона должен содержать только цифры.")
    
    # Проверяем длину номера телефона (опционально, например, не менее 10 цифр)
    if len(phone_number) < 10:
        raise ValueError("Номер телефона должен содержать как минимум 10 цифр.")
    
    return phone_number