"""
Конфигурационный файл для Hotel Management System
ВАЖНО: Этот файл должен быть в корневой директории проекта (рядом с main.py)
"""

class AppConfig:
    """Основные настройки приложения"""
    APP_NAME = "Hotel Harmony"
    APP_VERSION = "2.0"
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 720
    MIN_WIDTH = 1024
    MIN_HEIGHT = 600
    
    # Пути
    DB_FILE = "hotel.db"
    ASSETS_PATH = "assets/images/"
    LOGS_PATH = "logs/"
    
    # Темы
    APPEARANCE_MODE = "System"  # "System", "Dark", "Light"
    COLOR_THEME = "blue"  # "blue", "green", "dark-blue"
    
    # Типы номеров
    ROOM_TYPES = [
        "Одноместный",
        "Двухместный", 
        "Двухместный Делюкс",
        "Люкс",
        "Президентский Люкс"
    ]
    
    # Цвета статусов
    STATUS_COLORS = {
        "Свободен": "#2ECC71",
        "Занят": "#E74C3C",
        "На уборке": "#F1C40F",
        "Ремонт": "#95A5A6"
    }