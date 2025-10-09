import customtkinter as ctk
from PIL import Image
import os
from datetime import datetime

from .dashboard_frame import DashboardFrame
from .rooms_frame import RoomsFrame
from .bookings_frame import BookingsFrame
from .guests_frame import GuestsFrame


class TabButton(ctk.CTkButton):
    """Кнопка-вкладка с анимацией"""
    def __init__(self, master, text, command, icon=None):
        super().__init__(
            master,
            text=text,
            image=icon,
            compound="left",
            command=command,
            height=50,
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            text_color=("gray30", "gray70"),
            hover_color=("#e2e8f0", "#334155"),
            corner_radius=8,
            anchor="center"
        )
        self.is_active = False
    
    def set_active(self, active=True):
        """Установить активное состояние"""
        self.is_active = active
        if active:
            self.configure(
                fg_color=("#3b82f6", "#2563eb"),
                text_color="white",
                font=ctk.CTkFont(size=14, weight="bold")
            )
        else:
            self.configure(
                fg_color="transparent",
                text_color=("gray30", "gray70"),
                font=ctk.CTkFont(size=14)
            )


class MainAppWindow(ctk.CTk):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.title("Hotel Harmony - Система управления отелем")
        self.geometry("1400x850")
        self.minsize(1200, 700)
        
        # Центрирование окна
        self.center_window()
        
        # Переменные состояния
        self.current_frame_name = None
        
        # Настройка сетки - только 2 строки!
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Загрузка иконок
        self.load_icons()
        
        # Создание элементов интерфейса
        self.create_header()
        self.create_main_content()
        
        # Инициализация даты и времени после создания всех элементов
        self.update_datetime()
        
        # Показываем дашборд по умолчанию
        self.select_frame("dashboard")
    
    def center_window(self):
        """Центрирование окна на экране"""
        self.update_idletasks()
        width = 1400
        height = 850
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_icons(self):
        """Загрузка иконок с обработкой ошибок"""
        icon_size = (20, 20)
        try:
            self.dashboard_icon = ctk.CTkImage(
                Image.open("assets/images/dashboard.png"), 
                size=icon_size
            )
            self.rooms_icon = ctk.CTkImage(
                Image.open("assets/images/rooms.png"), 
                size=icon_size
            )
            self.bookings_icon = ctk.CTkImage(
                Image.open("assets/images/bookings.png"), 
                size=icon_size
            )
            self.guests_icon = ctk.CTkImage(
                Image.open("assets/images/guest_icon.png"), 
                size=icon_size
            )
        except FileNotFoundError:
            # Если иконки не найдены, используем None
            self.dashboard_icon = None
            self.rooms_icon = None
            self.bookings_icon = None
            self.guests_icon = None
    
    def update_datetime(self):
        """Обновление даты и времени"""
        now = datetime.now()
        date_str = now.strftime("%d.%m.%Y")
        time_str = now.strftime("%H:%M")
        
        # Проверяем, существует ли метка datetime_label
        if hasattr(self, 'datetime_label') and self.datetime_label:
            self.datetime_label.configure(text=f"{date_str}  {time_str}")
        
        # Обновляем каждую минуту
        self.after(60000, self.update_datetime)
    
    def create_header(self):
        """Создание шапки с вкладками"""
        # Главная шапка
        self.header = ctk.CTkFrame(
            self, 
            height=100, 
            corner_radius=0,
            fg_color=("#ffffff", "#0f172a")
        )
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)
        self.header.grid_columnconfigure(1, weight=1)
        
        # Верхняя часть шапки (логотип и инфо)
        top_section = ctk.CTkFrame(self.header, fg_color="transparent", height=50)
        top_section.grid(row=0, column=0, columnspan=3, sticky="ew", padx=20, pady=(10, 5))
        top_section.grid_columnconfigure(1, weight=1)
        
        # Логотип и название
        logo_frame = ctk.CTkFrame(top_section, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="w")
        
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="Hotel Harmony",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#3b82f6", "#60a5fa")
        )
        logo_label.pack(side="left")
        
        # Информационная панель справа
        info_frame = ctk.CTkFrame(top_section, fg_color="transparent")
        info_frame.grid(row=0, column=2, sticky="e")
        
        # Текущая дата и время
        self.datetime_label = ctk.CTkLabel(
            info_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray60")
        )
        self.datetime_label.pack(side="right", padx=(0, 10))
        
        # Переключатель темы
        self.theme_switch = ctk.CTkSegmentedButton(
            info_frame,
            values=["Светлая", "Темная", "Системная"],
            command=self.change_theme,
            width=150,
            height=32,
            font=ctk.CTkFont(size=12)
        )
        self.theme_switch.set("Системная")
        self.theme_switch.pack(side="right", padx=10)
        
        # Разделитель
        separator = ctk.CTkFrame(
            self.header, 
            height=1, 
            fg_color=("#e2e8f0", "#334155")
        )
        separator.grid(row=1, column=0, columnspan=3, sticky="ew", padx=20)
        
        # Нижняя часть - вкладки навигации
        tabs_frame = ctk.CTkFrame(self.header, fg_color="transparent", height=45)
        tabs_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=20, pady=(5, 5))
        tabs_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Создание кнопок-вкладок
        self.tab_buttons = {}
        
        self.tab_buttons["dashboard"] = TabButton(
            tabs_frame,
            "Панель управления",
            lambda: self.select_frame("dashboard"),
            icon=self.dashboard_icon
        )
        self.tab_buttons["dashboard"].grid(row=0, column=0, padx=2, sticky="ew")
        
        self.tab_buttons["rooms"] = TabButton(
            tabs_frame,
            "Номера",
            lambda: self.select_frame("rooms"),
            icon=self.rooms_icon
        )
        self.tab_buttons["rooms"].grid(row=0, column=1, padx=2, sticky="ew")
        
        self.tab_buttons["bookings"] = TabButton(
            tabs_frame,
            "Бронирования",
            lambda: self.select_frame("bookings"),
            icon=self.bookings_icon
        )
        self.tab_buttons["bookings"].grid(row=0, column=2, padx=2, sticky="ew")
        
        self.tab_buttons["guests"] = TabButton(
            tabs_frame,
            "Гости",
            lambda: self.select_frame("guests"),
            icon=self.guests_icon
        )
        self.tab_buttons["guests"].grid(row=0, column=3, padx=2, sticky="ew")
    
    def change_theme(self, value):
        """Смена темы интерфейса"""
        theme_map = {
            "Светлая": "light",
            "Темная": "dark", 
            "Системная": "system"
        }
        ctk.set_appearance_mode(theme_map.get(value, "system"))
    
    def create_main_content(self):
        """Создание основной области контента БЕЗ отступов"""
        self.content_frame = ctk.CTkFrame(
            self, 
            corner_radius=0,
            fg_color=("#f8fafc", "#020617")
        )
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Создание фреймов для каждого раздела
        self.dashboard_frame = DashboardFrame(self.content_frame, self.db)
        self.rooms_frame = RoomsFrame(self.content_frame, self.db)
        self.bookings_frame = BookingsFrame(self.content_frame, self.db)
        self.guests_frame = GuestsFrame(self.content_frame, self.db)
    
    def select_frame(self, name):
        """Переключение между разделами"""
        # Обновляем активную вкладку
        for tab_name, tab_btn in self.tab_buttons.items():
            tab_btn.set_active(tab_name == name)
        
        # Скрываем все фреймы
        self.dashboard_frame.grid_forget()
        self.rooms_frame.grid_forget()
        self.bookings_frame.grid_forget()
        self.guests_frame.grid_forget()

        # Показываем выбранный фрейм с минимальными отступами
        if name == "dashboard":
            self.dashboard_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            self.dashboard_frame.update_stats()
        elif name == "rooms":
            self.rooms_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            self.rooms_frame.refresh_rooms_display()
        elif name == "bookings":
            self.bookings_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            self.bookings_frame.refresh_bookings_table()
        elif name == "guests":
            self.guests_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            self.guests_frame.refresh_guests_table()
        
        self.current_frame_name = name