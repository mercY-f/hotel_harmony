import customtkinter as ctk
from datetime import date


class CompactStatCard(ctk.CTkFrame):
    """Компактная карточка статистики"""
    def __init__(self, master, title, value_text, color="#3b82f6"):
        super().__init__(master, corner_radius=12, fg_color=("white", "#1e293b"))
        self.configure(border_width=0)
        
        self.color = color
        self.target_value = 0
        self.current_value = 0
        
        # Контейнер с отступами
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Верхняя часть - заголовок
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x")
        
        ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="gray",
            anchor="w"
        ).pack(side="left", fill="x", expand=True)
        
        # Значение
        self.value_label = ctk.CTkLabel(
            content,
            text=value_text,
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color=color
        )
        self.value_label.pack(pady=(8, 0))
        
        # Hover эффект
        self.bind("<Enter>", lambda e: self.configure(fg_color=("#f8fafc", "#334155")))
        self.bind("<Leave>", lambda e: self.configure(fg_color=("white", "#1e293b")))
    
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


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db

        # Настройка сетки
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # Приветствие
        self.create_greeting()
        
        # Карточки статистики
        self.create_stat_cards()
        
        # Последние активности
        self.create_recent_activity()
        
        self.update_stats()
    
    def create_greeting(self):
        """Создание приветствия"""
        greeting_frame = ctk.CTkFrame(self, fg_color="transparent")
        greeting_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 15))
        greeting_frame.grid_columnconfigure(0, weight=1)
        
        greeting = self.get_greeting()
        today = date.today()
        
        combined_text = f"{greeting}  •  {today.strftime('%d %B %Y')}"
        
        ctk.CTkLabel(
            greeting_frame,
            text=combined_text,
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            greeting_frame,
            text="Обновить",
            command=self.update_stats,
            width=80,
            height=32,
            font=ctk.CTkFont(size=12)
        ).pack(side="right")
    
    def get_greeting(self):
        """Получение приветствия"""
        from datetime import datetime
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "Доброе утро"
        elif 12 <= hour < 17:
            return "Добрый день"
        elif 17 <= hour < 22:
            return "Добрый вечер"
        else:
            return "Доброй ночи"
    
    def create_stat_cards(self):
        """Создание карточек статистики"""
        self.free_card = CompactStatCard(
            self, "Свободных номеров", "0", color="#10b981"
        )
        self.free_card.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.occupied_card = CompactStatCard(
            self, "Занято номеров", "0", color="#ef4444"
        )
        self.occupied_card.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        self.checkin_card = CompactStatCard(
            self, "Заездов сегодня", "0", color="#3b82f6"
        )
        self.checkin_card.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")

        self.checkout_card = CompactStatCard(
            self, "Выездов сегодня", "0", color="#f59e0b"
        )
        self.checkout_card.grid(row=1, column=3, padx=5, pady=5, sticky="nsew")
    
    def create_recent_activity(self):
        """Последние активности"""
        activity_frame = ctk.CTkFrame(self, corner_radius=12, fg_color=("white", "#1e293b"))
        activity_frame.grid(row=2, column=0, columnspan=4, sticky="nsew", padx=5, pady=5)
        activity_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            activity_frame,
            text="Последние бронирования",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        self.activity_scroll = ctk.CTkScrollableFrame(
            activity_frame,
            fg_color="transparent"
        )
        self.activity_scroll.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 15))
        
        self.load_recent_activities()
    
    def load_recent_activities(self):
        """Загрузка последних активностей"""
        for widget in self.activity_scroll.winfo_children():
            widget.destroy()
        
        try:
            self.db.cursor.execute("""
                SELECT b.id, r.number, g.full_name, b.check_in_date, b.status
                FROM bookings b
                JOIN rooms r ON b.room_id = r.id
                JOIN guests g ON b.guest_id = g.id
                ORDER BY b.id DESC
                LIMIT 8
            """)
            
            recent_bookings = self.db.cursor.fetchall()
        except:
            recent_bookings = []
        
        if not recent_bookings:
            ctk.CTkLabel(
                self.activity_scroll,
                text="Нет последних бронирований",
                text_color="gray",
                font=ctk.CTkFont(size=12)
            ).pack(pady=20)
            return
        
        for booking in recent_bookings:
            self.create_activity_item(booking)
    
    def create_activity_item(self, booking):
        """Элемент активности"""
        booking_id, room_number, guest_name, check_in, status = booking
        
        item = ctk.CTkFrame(
            self.activity_scroll,
            corner_radius=8,
            fg_color=("#f8fafc", "#334155"),
            height=60
        )
        item.pack(fill="x", pady=3)
        item.pack_propagate(False)
        
        status_icons = {
            "Активно": "✅",
            "Завершено": "✔️",
            "Отменено": "❌"
        }
        icon = status_icons.get(status, "📋")
        
        # Левая часть
        left = ctk.CTkFrame(item, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=12, pady=8)
        
        ctk.CTkLabel(
            left,
            text=icon,
            font=ctk.CTkFont(size=20)
        ).pack(side="left", padx=(0, 8))
        
        info = ctk.CTkFrame(left, fg_color="transparent")
        info.pack(side="left", fill="both", expand=True)
        
        ctk.CTkLabel(
            info,
            text=f"Бронь #{booking_id} • Номер {room_number}",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            info,
            text=f"{guest_name} • {check_in}",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            anchor="w"
        ).pack(anchor="w")
        
        # Статус
        status_colors = {
            "Активно": "#10b981",
            "Завершено": "#6b7280",
            "Отменено": "#ef4444"
        }
        
        ctk.CTkLabel(
            item,
            text=status,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=status_colors.get(status, "gray"),
            width=70
        ).pack(side="right", padx=12)
    
    def update_stats(self):
        """Обновление статистики"""
        stats = self.db.get_dashboard_stats()
        
        self.free_card.set_value(stats["free"], animate=True)
        self.occupied_card.set_value(stats["occupied"], animate=True)
        self.checkin_card.set_value(stats["check_ins"], animate=True)
        self.checkout_card.set_value(stats["check_outs"], animate=True)
        
        self.load_recent_activities()