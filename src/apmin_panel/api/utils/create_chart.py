import base64
import io
from typing import List
from matplotlib import pyplot as plt
import seaborn as sns

def create_income_chart_by_date(completed_bookings: List):
    # Подсчитываем доход для каждого бронирования
    income_data = {}
    for booking in completed_bookings:
        apartment_income = (booking.end_date - booking.start_date).days * booking.apartment_rel.price_per_day
        income_data[booking.apartment_id] = income_data.get(booking.apartment_id, 0) + apartment_income

    # Создаем DataFrame для Seaborn
    import pandas as pd
    df = pd.DataFrame(list(income_data.items()), columns=['Apartment ID', 'Income'])

    # Создаем график
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Apartment ID', y='Income', data=df, palette='Blues_d')

    plt.title('Доход по Апартаментам', fontsize=16)
    plt.xlabel('ID Апартамента', fontsize=14)
    plt.ylabel('Доход (₽)', fontsize=14)
    plt.xticks(rotation=45)

    # Сохраняем график в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    # Кодируем график в base64
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf8')
    
    return f"data:image/png;base64,{img_base64}"
