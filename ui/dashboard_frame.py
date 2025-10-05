import customtkinter as ctk
from datetime import date


class ModernStatCard(ctk.CTkFrame):
    """Современная карточка статистики с градиентом и анимацией"""
    def __init__(self, master, title, value_text, icon="📊", color="#3b82f6"):
        super().__init__(master, corner_radius=15)
        self.configure(fg_color=("white", "#1e293b"), border_width=2, border_color=(color, color))
        
        self.color = color
        self.target_value = 0
        self.current_value = 0
        
        # Верхняя часть с иконкой и заголовком
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=20, pady=(15, 5))
        
        # Иконка
        self.icon_label = ctk.CTkLabel(
            self.header_frame,
            text=icon,
            font=ctk.CTkFont(size=32),
        )
        self.icon_label.pack(side="left")
        
        # Заголовок
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="gray"
        )
        self.title_label.pack(side="left", padx=(10, 0))
        
        # Значение
        self.value_label = ctk.CTkLabel(
            self,
            text=value_text,
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color=color
        )
        self.value_label.pack(pady=(10, 20), padx=20)
        
        # Прогресс бар (декоративный)
        self.progress = ctk.CTkProgressBar(
            self,
            height=4,
            progress_color=color,
            fg_color=("#e5e7eb", "#374151")
        )
        self.progress.pack(fill="x", padx=20, pady=(0, 15))
        self.progress.set(0.7)  # Пример значения
        
        # Hover эффект
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event):
        self.configure(border_width=3)
    
    def on_leave(self, event):
        self.configure(border_width=2)
    
    def set_value(self, new_value, animate=True):
        """Установка нового значения с анимацией"""
        self.target_value = int(new_value)
        if animate:
            self.animate_value()
        else:
            self.current_value = self.target_value
            self.value_label.configure(text=str(self.target_value))
    
    def animate_value(self):
        """Анимация изменения значения"""
        if self.current_value < self.target_value:
            self.current_value += max(1, (self.target_value - self.current_value) // 10)
            self.value_label.configure(text=str(self.current_value))
            self.after(50, self.animate_value)
        elif self.current_value > self.target_value:
            self.current_value -= max(1, (self.current_value - self.target_value) // 10)
            self.value_label.configure(text=str(self.current_value))
            self.after(50, self.animate_value)
        else:
            self.value_label.configure(text=str(self.target_value))


class QuickActionButton(ctk.CTkButton):
    """Кнопка быстрого действия"""
    def __init__(self, master, text, icon, command, color="#3b82f6"):
        super().__init__(
            master,
            text=f"{icon}  {text}",
            command=command,
            height=50,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=color,
            hover_color=self.darken_color(color),
            corner_radius=10
        )
    
    @staticmethod
    def darken_color(hex_color):
        """Затемнение цвета для hover эффекта"""
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)
        return f'#{r:02x}{g:02x}{b:02x}'


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db

        # Настройка сетки
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Заголовок с приветствием
        self.create_header()
        
        # Карточки статистики
        self.create_stat_cards()
        
        # Быстрые действия
        self.create_quick_actions()
        
        # Последние активности (опционально)
        self.create_recent_activity()
        
        self.update_stats()
    
    def create_header(self):
        """Создание заголовка"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 15))
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Приветствие
        greeting = self.get_greeting()
        welcome_label = ctk.CTkLabel(
            header_frame,
            text=greeting,
            font=ctk.CTkFont(size=26, weight="bold")
        )
        welcome_label.grid(row=0, column=0, sticky="w")
        
        # Текущая дата
        today = date.today()
        date_label = ctk.CTkLabel(
            header_frame,
            text=today.strftime("%d %B %Y"),
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        date_label.grid(row=1, column=0, sticky="w", pady=(3, 0))
        
        # Кнопка обновления
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Обновить",
            command=self.update_stats,
            width=110,
            height=38,
            fg_color="transparent",
            border_width=2,
            border_color=("#3b82f6", "#2563eb"),
            text_color=("#3b82f6", "#2563eb"),
            hover_color=("#e5e7eb", "#334155"),
            font=ctk.CTkFont(size=13)
        )
        refresh_btn.grid(row=0, column=1, rowspan=2, padx=10, sticky="e")
    
    def get_greeting(self):
        """Получение приветствия в зависимости от времени"""
        from datetime import datetime
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "☀️ Доброе утро!"
        elif 12 <= hour < 17:
            return "🌤️ Добрый день!"
        elif 17 <= hour < 22:
            return "🌆 Добрый вечер!"
        else:
            return "🌙 Доброй ночи!"
    
    def create_stat_cards(self):
        """Создание карточек статистики"""
        # Свободные номера
        self.free_card = ModernStatCard(
            self,
            "Свободных номеров",
            "0",
            icon="🟢",
            color="#10b981"
        )
        self.free_card.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Занятые номера
        self.occupied_card = ModernStatCard(
            self,
            "Занято номеров",
            "0",
            icon="🔴",
            color="#ef4444"
        )
        self.occupied_card.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        # Заезды сегодня
        self.checkin_card = ModernStatCard(
            self,
            "Заездов сегодня",
            "0",
            icon="📥",
            color="#3b82f6"
        )
        self.checkin_card.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        # Выезды сегодня
        self.checkout_card = ModernStatCard(
            self,
            "Выездов сегодня",
            "0",
            icon="📤",
            color="#f59e0b"
        )
        self.checkout_card.grid(row=1, column=3, padx=10, pady=10, sticky="nsew")
    
    def create_quick_actions(self):
        """Создание панели быстрых действий"""
        actions_frame = ctk.CTkFrame(self, corner_radius=15)
        actions_frame.grid(row=2, column=0, columnspan=4, sticky="ew", padx=10, pady=10)
        
        ctk.CTkLabel(
            actions_frame,
            text="⚡ Быстрые действия",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        buttons_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 15))
        buttons_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Кнопки быстрых действий
        QuickActionButton(
            buttons_frame,
            "Новое бронирование",
            "➕",
            self.quick_new_booking,
            color="#3b82f6"
        ).grid(row=0, column=0, padx=5, sticky="ew")
        
        QuickActionButton(
            buttons_frame,
            "Добавить номер",
            "🏠",
            self.quick_add_room,
            color="#10b981"
        ).grid(row=0, column=1, padx=5, sticky="ew")
        
        QuickActionButton(
            buttons_frame,
            "Добавить гостя",
            "👤",
            self.quick_add_guest,
            color="#8b5cf6"
        ).grid(row=0, column=2, padx=5, sticky="ew")
        
        QuickActionButton(
            buttons_frame,
            "Отчеты",
            "📊",
            self.quick_reports,
            color="#f59e0b"
        ).grid(row=0, column=3, padx=5, sticky="ew")
    
    def create_recent_activity(self):
        """Создание панели последних активностей"""
        activity_frame = ctk.CTkFrame(self, corner_radius=15)
        activity_frame.grid(row=3, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)
        activity_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            activity_frame,
            text="📋 Последние активности",
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=20, pady=(15, 10))
        
        # Скроллируемая область для активностей
        self.activity_scroll = ctk.CTkScrollableFrame(
            activity_frame,
            fg_color="transparent"
        )
        self.activity_scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 15))
        
        self.load_recent_activities()
    
    def load_recent_activities(self):
        """Загрузка последних активностей"""
        # Очистка предыдущих записей
        for widget in self.activity_scroll.winfo_children():
            widget.destroy()
        
        # Получаем последние бронирования (по ID, так как created_at может отсутствовать)
        try:
            self.db.cursor.execute("""
                SELECT b.id, r.number, g.full_name, b.check_in_date, b.status
                FROM bookings b
                JOIN rooms r ON b.room_id = r.id
                JOIN guests g ON b.guest_id = g.id
                ORDER BY b.id DESC
                LIMIT 5
            """)
            
            recent_bookings = self.db.cursor.fetchall()
        except Exception as e:
            print(f"Ошибка загрузки активностей: {e}")
            recent_bookings = []
        
        if not recent_bookings:
            ctk.CTkLabel(
                self.activity_scroll,
                text="Нет последних активностей",
                text_color="gray",
                font=ctk.CTkFont(size=13)
            ).pack(pady=20)
            return
        
        for booking in recent_bookings:
            self.create_activity_item(booking)
    
    def create_activity_item(self, booking):
        """Создание элемента активности"""
        booking_id, room_number, guest_name, check_in, status = booking
        
        item_frame = ctk.CTkFrame(
            self.activity_scroll,
            corner_radius=10,
            fg_color=("#f3f4f6", "#374151")
        )
        item_frame.pack(fill="x", pady=5)
        
        # Иконка в зависимости от статуса
        status_icons = {
            "Активно": "✅",
            "Завершено": "✔️",
            "Отменено": "❌"
        }
        icon = status_icons.get(status, "📋")
        
        # Левая часть - иконка и информация
        left_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        ctk.CTkLabel(
            left_frame,
            text=icon,
            font=ctk.CTkFont(size=24)
        ).pack(side="left", padx=(0, 10))
        
        info_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)
        
        ctk.CTkLabel(
            info_frame,
            text=f"Бронь #{booking_id} - Номер {room_number}",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            info_frame,
            text=f"Гость: {guest_name} | Заезд: {check_in}",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        ).pack(anchor="w")
        
        # Правая часть - статус
        status_colors = {
            "Активно": "#10b981",
            "Завершено": "#6b7280",
            "Отменено": "#ef4444"
        }
        
        ctk.CTkLabel(
            item_frame,
            text=status,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=status_colors.get(status, "gray"),
            width=100
        ).pack(side="right", padx=15)
    
    def update_stats(self):
        """Обновление статистики с анимацией"""
        stats = self.db.get_dashboard_stats()
        
        self.free_card.set_value(stats["free"], animate=True)
        self.occupied_card.set_value(stats["occupied"], animate=True)
        self.checkin_card.set_value(stats["check_ins"], animate=True)
        self.checkout_card.set_value(stats["check_outs"], animate=True)
        
        # Обновление прогресс-баров (пример: загруженность)
        total_rooms = stats["free"] + stats["occupied"]
        if total_rooms > 0:
            occupancy_rate = stats["occupied"] / total_rooms
            self.free_card.progress.set(1 - occupancy_rate)
            self.occupied_card.progress.set(occupancy_rate)
        
        # Обновляем активности
        self.load_recent_activities()
    
    def quick_new_booking(self):
        """Быстрое создание бронирования"""
        from tkinter import messagebox
        messagebox.showinfo(
            "Быстрое действие",
            "Переход к созданию нового бронирования...",
            parent=self
        )
        # Здесь можно добавить переход к разделу бронирований
    
    def quick_add_room(self):
        """Быстрое добавление номера"""
        from tkinter import messagebox
        messagebox.showinfo(
            "Быстрое действие",
            "Переход к добавлению номера...",
            parent=self
        )
        # Здесь можно добавить переход к разделу номеров
    
    def quick_add_guest(self):
        """Быстрое добавление гостя"""
        from tkinter import messagebox
        messagebox.showinfo(
            "Быстрое действие",
            "Переход к добавлению гостя...",
            parent=self
        )
        # Здесь можно добавить переход к разделу гостей
    
    def quick_reports(self):
        """Быстрые отчеты"""
        from tkinter import messagebox
        
        # Подсчет статистики для отчета
        stats = self.db.get_dashboard_stats()
        total_rooms = stats["free"] + stats["occupied"]
        
        if total_rooms > 0:
            occupancy_rate = (stats["occupied"] / total_rooms) * 100
        else:
            occupancy_rate = 0
        
        # Получаем общее количество гостей и броней
        self.db.cursor.execute("SELECT COUNT(*) FROM guests")
        total_guests = self.db.cursor.fetchone()[0]
        
        self.db.cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = ?", 
                              (self.db.BOOKING_STATUS_ACTIVE,))
        active_bookings = self.db.cursor.fetchone()[0]
        
        report = f"""
📊 КРАТКИЙ ОТЧЕТ
{'='*40}

🏨 Номера:
  • Всего: {total_rooms}
  • Свободно: {stats['free']}
  • Занято: {stats['occupied']}
  • Загруженность: {occupancy_rate:.1f}%

📅 Сегодня:
  • Заездов: {stats['check_ins']}
  • Выездов: {stats['check_outs']}

👥 База данных:
  • Всего гостей: {total_guests}
  • Активных броней: {active_bookings}
        """
        
        messagebox.showinfo("Краткий отчет", report.strip(), parent=self)