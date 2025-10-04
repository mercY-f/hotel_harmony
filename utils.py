"""
Вспомогательные функции для Hotel Management System
"""
from datetime import datetime, date, timedelta
import re
from typing import Optional, Tuple


def validate_phone(phone: str) -> bool:
    """
    Валидация номера телефона
    Принимает форматы: +7XXXXXXXXXX, 8XXXXXXXXXX, 7XXXXXXXXXX
    """
    if not phone:
        return True  # Телефон опционален
    
    # Удаляем все нечисловые символы кроме +
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Проверяем различные форматы
    patterns = [
        r'^\+7\d{10}$',  # +7XXXXXXXXXX
        r'^8\d{10}$',     # 8XXXXXXXXXX
        r'^7\d{10}$',     # 7XXXXXXXXXX
    ]
    
    return any(re.match(pattern, cleaned) for pattern in patterns)


def format_phone(phone: str) -> str:
    """Форматирование телефона в красивый вид"""
    if not phone:
        return ""
    
    # Удаляем все кроме цифр
    digits = re.sub(r'\D', '', phone)
    
    # Если начинается с 8, меняем на 7
    if digits.startswith('8'):
        digits = '7' + digits[1:]
    
    # Форматируем как +7 (XXX) XXX-XX-XX
    if len(digits) == 11 and digits.startswith('7'):
        return f"+7 ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:11]}"
    
    return phone


def validate_email(email: str) -> bool:
    """Валидация email адреса"""
    if not email:
        return True  # Email опционален
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def calculate_nights(check_in: date, check_out: date) -> int:
    """Расчет количества ночей между датами"""
    if check_out <= check_in:
        return 0
    return (check_out - check_in).days


def calculate_total_price(price_per_night: float, check_in: date, check_out: date) -> float:
    """Расчет общей стоимости бронирования"""
    nights = calculate_nights(check_in, check_out)
    return price_per_night * nights


def format_currency(amount: float, currency: str = "руб") -> str:
    """Форматирование суммы в валюту"""
    return f"{amount:,.2f} {currency}".replace(',', ' ')


def parse_date(date_str: str) -> Optional[date]:
    """Парсинг строки в дату"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def format_date(d: date, format_str: str = "%d.%m.%Y") -> str:
    """Форматирование даты в строку"""
    return d.strftime(format_str)


def get_date_range(start_date: date, end_date: date) -> list:
    """Получение списка дат в диапазоне"""
    delta = end_date - start_date
    return [start_date + timedelta(days=i) for i in range(delta.days + 1)]


def is_date_in_range(check_date: date, start_date: date, end_date: date) -> bool:
    """Проверка попадания даты в диапазон"""
    return start_date <= check_date <= end_date


def validate_room_number(number: str) -> Tuple[bool, str]:
    """
    Валидация номера комнаты
    Возвращает (валидность, сообщение об ошибке)
    """
    if not number or not number.strip():
        return False, "Номер комнаты не может быть пустым"
    
    number = number.strip()
    
    # Проверка длины
    if len(number) > 10:
        return False, "Номер комнаты слишком длинный"
    
    # Разрешаем цифры, буквы и дефисы
    if not re.match(r'^[A-Za-z0-9\-]+$', number):
        return False, "Номер может содержать только буквы, цифры и дефисы"
    
    return True, ""


def validate_price(price_str: str) -> Tuple[bool, Optional[float], str]:
    """
    Валидация цены
    Возвращает (валидность, значение, сообщение об ошибке)
    """
    if not price_str or not price_str.strip():
        return False, None, "Цена не может быть пустой"
    
    try:
        price = float(price_str.strip().replace(',', '.'))
        
        if price <= 0:
            return False, None, "Цена должна быть больше нуля"
        
        if price > 1000000:
            return False, None, "Цена слишком большая"
        
        return True, price, ""
    except ValueError:
        return False, None, "Некорректный формат цены"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Обрезка текста с добавлением многоточия"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def sanitize_input(text: str) -> str:
    """Очистка ввода от потенциально опасных символов"""
    # Удаляем специальные символы SQL
    dangerous_chars = ["'", '"', ';', '--', '/*', '*/']
    for char in dangerous_chars:
        text = text.replace(char, '')
    return text.strip()


class DateRange:
    """Класс для работы с диапазонами дат"""
    
    def __init__(self, start: date, end: date):
        if end < start:
            raise ValueError("Дата окончания не может быть раньше даты начала")
        self.start = start
        self.end = end
    
    def overlaps(self, other: 'DateRange') -> bool:
        """Проверка пересечения двух диапазонов дат"""
        return not (self.end <= other.start or self.start >= other.end)
    
    def contains(self, check_date: date) -> bool:
        """Проверка содержания даты в диапазоне"""
        return self.start <= check_date <= self.end
    
    def duration(self) -> int:
        """Длительность диапазона в днях"""
        return (self.end - self.start).days
    
    def __str__(self):
        return f"{format_date(self.start)} - {format_date(self.end)}"


class ValidationError(Exception):
    """Кастомное исключение для ошибок валидации"""
    pass


def validate_booking_dates(check_in: date, check_out: date) -> Tuple[bool, str]:
    """
    Комплексная валидация дат бронирования
    Возвращает (валидность, сообщение об ошибке)
    """
    today = date.today()
    
    if check_in < today:
        return False, "Дата заезда не может быть в прошлом"
    
    if check_out <= check_in:
        return False, "Дата выезда должна быть позже даты заезда"
    
    # Проверка максимального срока бронирования (например, 365 дней)
    max_duration = 365
    if (check_out - check_in).days > max_duration:
        return False, f"Максимальный срок бронирования - {max_duration} дней"
    
    # Проверка минимального срока (например, 1 день)
    if (check_out - check_in).days < 1:
        return False, "Минимальный срок бронирования - 1 день"
    
    return True, ""


def get_season(check_date: date) -> str:
    """Определение сезона по дате"""
    month = check_date.month
    
    if month in [12, 1, 2]:
        return "Зима"
    elif month in [3, 4, 5]:
        return "Весна"
    elif month in [6, 7, 8]:
        return "Лето"
    else:
        return "Осень"


def calculate_discount(total: float, nights: int) -> Tuple[float, float]:
    """
    Расчет скидки в зависимости от длительности
    Возвращает (сумма скидки, итоговая сумма)
    """
    discount_rate = 0
    
    if nights >= 30:
        discount_rate = 0.20  # 20% за месяц и более
    elif nights >= 14:
        discount_rate = 0.15  # 15% за 2 недели
    elif nights >= 7:
        discount_rate = 0.10  # 10% за неделю
    
    discount = total * discount_rate
    final_total = total - discount
    
    return discount, final_total