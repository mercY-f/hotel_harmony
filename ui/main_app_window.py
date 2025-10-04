import customtkinter as ctk
from PIL import Image

from .dashboard_frame import DashboardFrame
from .rooms_frame import RoomsFrame
from .bookings_frame import BookingsFrame
from .guests_frame import GuestsFrame # <-- Импортируем новый фрейм

class MainAppWindow(ctk.CTk):
    def __init__(self, db):
        super().__init__()
        self.db = db

        self.title("Hotel Harmony")
        self.geometry("1280x720")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # --- Загрузка иконок ---
        try:
            self.dashboard_icon = ctk.CTkImage(Image.open("assets/images/dashboard.png"), size=(20, 20))
            self.rooms_icon = ctk.CTkImage(Image.open("assets/images/rooms.png"), size=(20, 20))
            self.bookings_icon = ctk.CTkImage(Image.open("assets/images/bookings.png"), size=(20, 20))
            self.guests_icon = ctk.CTkImage(Image.open("assets/images/guest_icon.png"), size=(20, 20)) # <-- Иконка для гостей
        except FileNotFoundError:
            self.dashboard_icon, self.rooms_icon, self.bookings_icon, self.guests_icon = None, None, None, None
            print("Warning: Image files not found in assets/images/. Please create them.")

        # --- Навигационная панель ---
        self.nav_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.nav_frame.grid(row=0, column=0, sticky="nsew")
        self.nav_frame.grid_rowconfigure(5, weight=1) # <-- Увеличиваем на 1

        self.nav_title = ctk.CTkLabel(self.nav_frame, text="Hotel Harmony", font=ctk.CTkFont(size=20, weight="bold"))
        self.nav_title.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.dashboard_button = ctk.CTkButton(self.nav_frame, text="Панель", image=self.dashboard_icon, compound="left", command=lambda: self.select_frame("dashboard"))
        self.dashboard_button.grid(row=1, column=0, padx=20, pady=10, sticky="ew")

        self.rooms_button = ctk.CTkButton(self.nav_frame, text="Номера", image=self.rooms_icon, compound="left", command=lambda: self.select_frame("rooms"))
        self.rooms_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        self.bookings_button = ctk.CTkButton(self.nav_frame, text="Бронирования", image=self.bookings_icon, compound="left", command=lambda: self.select_frame("bookings"))
        self.bookings_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self.guests_button = ctk.CTkButton(self.nav_frame, text="Гости", image=self.guests_icon, compound="left", command=lambda: self.select_frame("guests")) # <-- Новая кнопка
        self.guests_button.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        # --- Фреймы-экраны ---
        self.dashboard_frame = DashboardFrame(self, self.db)
        self.rooms_frame = RoomsFrame(self, self.db)
        self.bookings_frame = BookingsFrame(self, self.db)
        self.guests_frame = GuestsFrame(self, self.db) # <-- Создаем экземпляр нового фрейма

        self.select_frame("dashboard")

    def select_frame(self, name):
        # Сначала скрываем все фреймы
        self.dashboard_frame.grid_forget()
        self.rooms_frame.grid_forget()
        self.bookings_frame.grid_forget()
        self.guests_frame.grid_forget() # <-- Скрываем новый фрейм

        # Показываем выбранный
        if name == "dashboard":
            self.dashboard_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
            self.dashboard_frame.update_stats()
        elif name == "rooms":
            self.rooms_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
            self.rooms_frame.refresh_rooms_display()
        elif name == "bookings":
            self.bookings_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
            self.bookings_frame.refresh_bookings_table()
        elif name == "guests": # <-- Логика для отображения фрейма гостей
            self.guests_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
            self.guests_frame.refresh_guests_table()