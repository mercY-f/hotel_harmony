import customtkinter as ctk
from PIL import Image
import os

from .dashboard_frame import DashboardFrame
from .rooms_frame import RoomsFrame
from .bookings_frame import BookingsFrame
from .guests_frame import GuestsFrame


class ModernButton(ctk.CTkButton):
    """Кастомная кнопка навигации с анимацией"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.default_fg_color = self.cget("fg_color")
        self.hover_fg_color = "#1f538d"
        self.active_fg_color = "#2b6cb0"
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event):
        if not self.cget("state") == "disabled":
            self.configure(fg_color=self.hover_fg_color)
    
    def on_leave(self, event):
        if not self.cget("state") == "disabled":
            self.configure(fg_color=self.default_fg_color)
    
    def set_active(self, active=True):
        if active:
            self.configure(fg_color=self.active_fg_color, font=ctk.CTkFont(size=14, weight="bold"))
        else:
            self.configure(fg_color=self.default_fg_color, font=ctk.CTkFont(size=14))


class MainAppWindow(ctk.CTk):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.title("Hotel Harmony - Система управления отелем")
        self.geometry("1400x800")
        self.minsize(1024, 600)
        
        # Центрирование окна
        self.center_window()
        
        # Переменные состояния
        self.sidebar_expanded = True
        self.current_frame_name = None
        
        # Настройка сетки
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Загрузка иконок
        self.load_icons()
        
        # Создание элементов интерфейса
        self.create_sidebar()
        self.create_top_bar()
        self.create_main_content()
        
        # Привязка событий изменения размера
        self.bind("<Configure>", self.on_window_resize)
        
        # Показываем дашборд по умолчанию
        self.select_frame("dashboard")
    
    def center_window(self):
        """Центрирование окна на экране"""
        self.update_idletasks()
        width = 1400
        height = 800
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_icons(self):
        """Загрузка иконок с обработкой ошибок"""
        icon_size = (24, 24)
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
            self.menu_icon = ctk.CTkImage(
                Image.open("assets/images/menu.png") if os.path.exists("assets/images/menu.png") 
                else Image.new('RGB', (24, 24), color='white'), 
                size=icon_size
            )
        except FileNotFoundError:
            print("⚠️ Иконки не найдены, используется текстовый режим")
            self.dashboard_icon = None
            self.rooms_icon = None
            self.bookings_icon = None
            self.guests_icon = None
            self.menu_icon = None
    
    def create_sidebar(self):
        """Создание боковой панели навигации"""
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)
        self.sidebar.grid_propagate(False)
        
        # Заголовок приложения
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.grid(row=0, column=0, padx=20, pady=(30, 20), sticky="ew")
        
        self.logo_label = ctk.CTkLabel(
            self.logo_frame,
            text="🏨 Hotel Harmony",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=("#1f538d", "#3b82f6")
        )
        self.logo_label.pack()
        
        self.subtitle_label = ctk.CTkLabel(
            self.logo_frame,
            text="Система управления",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.subtitle_label.pack()
        
        # Разделитель
        ctk.CTkFrame(self.sidebar, height=2, fg_color=("#d1d5db", "#374151")).grid(
            row=1, column=0, padx=20, pady=(0, 20), sticky="ew"
        )
        
        # Кнопки навигации
        self.nav_buttons = {}
        
        self.nav_buttons["dashboard"] = ModernButton(
            self.sidebar,
            text="  Панель управления",
            image=self.dashboard_icon,
            compound="left",
            command=lambda: self.select_frame("dashboard"),
            height=50,
            anchor="w",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("#e5e7eb", "#374151")
        )
        self.nav_buttons["dashboard"].grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        self.nav_buttons["rooms"] = ModernButton(
            self.sidebar,
            text="  Номера",
            image=self.rooms_icon,
            compound="left",
            command=lambda: self.select_frame("rooms"),
            height=50,
            anchor="w",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("#e5e7eb", "#374151")
        )
        self.nav_buttons["rooms"].grid(row=3, column=0, padx=15, pady=5, sticky="ew")

        self.nav_buttons["bookings"] = ModernButton(
            self.sidebar,
            text="  Бронирования",
            image=self.bookings_icon,
            compound="left",
            command=lambda: self.select_frame("bookings"),
            height=50,
            anchor="w",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("#e5e7eb", "#374151")
        )
        self.nav_buttons["bookings"].grid(row=4, column=0, padx=15, pady=5, sticky="ew")

        self.nav_buttons["guests"] = ModernButton(
            self.sidebar,
            text="  Гости",
            image=self.guests_icon,
            compound="left",
            command=lambda: self.select_frame("guests"),
            height=50,
            anchor="w",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("#e5e7eb", "#374151")
        )
        self.nav_buttons["guests"].grid(row=5, column=0, padx=15, pady=5, sticky="ew")
        
        # Нижняя панель с настройками
        self.settings_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.settings_frame.grid(row=7, column=0, padx=15, pady=20, sticky="ew")
        
        # Переключатель темы
        self.theme_label = ctk.CTkLabel(
            self.settings_frame,
            text="Тема:",
            font=ctk.CTkFont(size=12)
        )
        self.theme_label.pack(anchor="w", pady=(0, 5))
        
        self.theme_switch = ctk.CTkSegmentedButton(
            self.settings_frame,
            values=["Светлая", "Темная", "Системная"],
            command=self.change_theme
        )
        self.theme_switch.set("Системная")
        self.theme_switch.pack(fill="x")
        
        # Информация о версии
        self.version_label = ctk.CTkLabel(
            self.settings_frame,
            text="Версия 2.0",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.version_label.pack(pady=(15, 0))
    
    def create_top_bar(self):
        """Создание верхней панели"""
        self.top_bar = ctk.CTkFrame(self, height=60, corner_radius=0)
        self.top_bar.grid(row=0, column=1, sticky="ew", padx=0, pady=0)
        self.top_bar.grid_columnconfigure(1, weight=1)
        self.top_bar.grid_propagate(False)
        
        # Кнопка сворачивания меню
        self.toggle_btn = ctk.CTkButton(
            self.top_bar,
            text="☰",
            width=50,
            height=50,
            command=self.toggle_sidebar,
            fg_color="transparent",
            hover_color=("#e5e7eb", "#374151"),
            font=ctk.CTkFont(size=24)
        )
        self.toggle_btn.grid(row=0, column=0, padx=10, pady=5)
        
        # Заголовок текущей страницы
        self.page_title = ctk.CTkLabel(
            self.top_bar,
            text="Панель управления",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.page_title.grid(row=0, column=1, padx=20, sticky="w")
        
        # Информационная панель
        self.info_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.info_frame.grid(row=0, column=2, padx=20, sticky="e")
        
        # Текущая дата и время
        self.update_datetime()
    
    def update_datetime(self):
        """Обновление даты и времени"""
        from datetime import datetime
        now = datetime.now()
        date_str = now.strftime("%d.%m.%Y")
        time_str = now.strftime("%H:%M")
        
        if hasattr(self, 'datetime_label'):
            self.datetime_label.configure(text=f"📅 {date_str}  🕐 {time_str}")
        else:
            self.datetime_label = ctk.CTkLabel(
                self.info_frame,
                text=f"📅 {date_str}  🕐 {time_str}",
                font=ctk.CTkFont(size=13)
            )
            self.datetime_label.pack()
        
        # Обновляем каждые 60 секунд
        self.after(60000, self.update_datetime)
    
    def create_main_content(self):
        """Создание основной области контента"""
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=1, column=1, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Создание фреймов для каждого раздела
        self.dashboard_frame = DashboardFrame(self.content_frame, self.db)
        self.rooms_frame = RoomsFrame(self.content_frame, self.db)
        self.bookings_frame = BookingsFrame(self.content_frame, self.db)
        self.guests_frame = GuestsFrame(self.content_frame, self.db)
    
    def toggle_sidebar(self):
        """Сворачивание/разворачивание боковой панели"""
        if self.sidebar_expanded:
            # Сворачиваем
            self.sidebar.configure(width=80)
            self.logo_label.configure(text="🏨")
            self.subtitle_label.pack_forget()
            
            # Скрываем текст на кнопках
            for btn in self.nav_buttons.values():
                btn.configure(text="")
            
            self.theme_label.pack_forget()
            self.theme_switch.pack_forget()
            self.version_label.pack_forget()
            
            self.sidebar_expanded = False
        else:
            # Разворачиваем
            self.sidebar.configure(width=280)
            self.logo_label.configure(text="🏨 Hotel Harmony")
            self.subtitle_label.pack()
            
            # Показываем текст на кнопках
            self.nav_buttons["dashboard"].configure(text="  Панель управления")
            self.nav_buttons["rooms"].configure(text="  Номера")
            self.nav_buttons["bookings"].configure(text="  Бронирования")
            self.nav_buttons["guests"].configure(text="  Гости")
            
            self.theme_label.pack(anchor="w", pady=(0, 5))
            self.theme_switch.pack(fill="x")
            self.version_label.pack(pady=(15, 0))
            
            self.sidebar_expanded = True
    
    def change_theme(self, value):
        """Смена темы интерфейса"""
        if value == "Светлая":
            ctk.set_appearance_mode("light")
        elif value == "Темная":
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("system")
    
    def select_frame(self, name):
        """Переключение между разделами"""
        # Обновляем заголовок
        titles = {
            "dashboard": "Панель управления",
            "rooms": "Управление номерами",
            "bookings": "Бронирования",
            "guests": "База гостей"
        }
        self.page_title.configure(text=titles.get(name, ""))
        
        # Обновляем активную кнопку
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == name:
                btn.configure(
                    fg_color=("#3b82f6", "#2563eb"),
                    text_color="white"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=("gray10", "gray90")
                )
        
        # Скрываем все фреймы
        self.dashboard_frame.grid_forget()
        self.rooms_frame.grid_forget()
        self.bookings_frame.grid_forget()
        self.guests_frame.grid_forget()

        # Показываем выбранный фрейм
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
    
    def on_window_resize(self, event):
        """Обработка изменения размера окна"""
        if event.widget == self:
            window_width = event.width
            
            # Автоматическое сворачивание sidebar при узком окне
            if window_width < 1200 and self.sidebar_expanded:
                self.toggle_sidebar()
            elif window_width >= 1200 and not self.sidebar_expanded:
                self.toggle_sidebar()