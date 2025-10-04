import customtkinter as ctk
from tkinter import messagebox
from config import AppConfig
from utils import validate_room_number, validate_price, format_currency


class AddRoomDialog(ctk.CTkToplevel):
    def __init__(self, master, db, on_close_callback):
        super().__init__(master)
        self.db = db
        self.on_close_callback = on_close_callback
        
        self.title("Добавить новый номер")
        self.geometry("400x400")
        self.transient(master)
        self.grab_set()
        
        # Заголовок
        ctk.CTkLabel(
            self, 
            text="Новый номер", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(padx=20, pady=(20, 10))

        # Номер комнаты
        self.number_label = ctk.CTkLabel(self, text="Номер комнаты: *")
        self.number_label.pack(padx=20, pady=(10, 5), anchor="w")
        self.number_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Например: 101, A-12",
            width=300
        )
        self.number_entry.pack(padx=20, pady=5)

        # Тип комнаты
        self.type_label = ctk.CTkLabel(self, text="Тип комнаты: *")
        self.type_label.pack(padx=20, pady=(10, 5), anchor="w")
        self.type_menu = ctk.CTkOptionMenu(
            self, 
            values=AppConfig.ROOM_TYPES,
            width=300
        )
        self.type_menu.pack(padx=20, pady=5)

        # Цена за ночь
        self.price_label = ctk.CTkLabel(self, text="Цена за ночь (руб): *")
        self.price_label.pack(padx=20, pady=(10, 5), anchor="w")
        self.price_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Например: 2500.00",
            width=300
        )
        self.price_entry.pack(padx=20, pady=5)
        
        # Подсказка
        ctk.CTkLabel(
            self, 
            text="* - обязательные поля", 
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(padx=20, pady=(10, 5))

        # Кнопки
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(padx=20, pady=20, fill="x")
        
        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Отмена",
            command=self.destroy,
            fg_color="gray",
            width=140
        )
        self.cancel_button.pack(side="left", expand=True, padx=(0, 5))
        
        self.save_button = ctk.CTkButton(
            self.button_frame,
            text="Сохранить",
            command=self.save_room,
            width=140
        )
        self.save_button.pack(side="right", expand=True, padx=(5, 0))

    def save_room(self):
        """Сохранение нового номера с валидацией"""
        number = self.number_entry.get().strip()
        r_type = self.type_menu.get()
        price_str = self.price_entry.get().strip()

        # Валидация номера
        is_valid, error_msg = validate_room_number(number)
        if not is_valid:
            messagebox.showerror("Ошибка", error_msg, parent=self)
            self.number_entry.focus()
            return

        # Валидация цены
        is_valid, price, error_msg = validate_price(price_str)
        if not is_valid:
            messagebox.showerror("Ошибка", error_msg, parent=self)
            self.price_entry.focus()
            return

        # Попытка добавить номер
        if self.db.add_room(number, r_type, price):
            messagebox.showinfo(
                "Успех", 
                f"Номер '{number}' успешно добавлен!\n"
                f"Тип: {r_type}\n"
                f"Цена: {format_currency(price)}", 
                parent=self
            )
            self.on_close_callback()
            self.destroy()
        else:
            messagebox.showerror(
                "Ошибка", 
                f"Номер '{number}' уже существует в системе.", 
                parent=self
            )


class EditRoomDialog(ctk.CTkToplevel):
    """Диалог редактирования номера"""
    def __init__(self, master, db, room_data, on_close_callback):
        super().__init__(master)
        self.db = db
        self.room_data = room_data
        self.on_close_callback = on_close_callback
        
        self.title(f"Редактировать номер {room_data[1]}")
        self.geometry("400x450")
        self.transient(master)
        self.grab_set()
        
        # Заголовок
        ctk.CTkLabel(
            self, 
            text=f"Номер {room_data[1]}", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(padx=20, pady=(20, 10))
        
        # Тип комнаты
        self.type_label = ctk.CTkLabel(self, text="Тип комнаты:")
        self.type_label.pack(padx=20, pady=(10, 5), anchor="w")
        self.type_menu = ctk.CTkOptionMenu(
            self, 
            values=AppConfig.ROOM_TYPES,
            width=300
        )
        self.type_menu.set(room_data[2])
        self.type_menu.pack(padx=20, pady=5)
        
        # Цена
        self.price_label = ctk.CTkLabel(self, text="Цена за ночь (руб):")
        self.price_label.pack(padx=20, pady=(10, 5), anchor="w")
        self.price_entry = ctk.CTkEntry(self, width=300)
        self.price_entry.insert(0, str(room_data[3]))
        self.price_entry.pack(padx=20, pady=5)
        
        # Статус
        self.status_label = ctk.CTkLabel(self, text="Статус:")
        self.status_label.pack(padx=20, pady=(10, 5), anchor="w")
        self.status_menu = ctk.CTkOptionMenu(
            self, 
            values=list(AppConfig.STATUS_COLORS.keys()),
            width=300
        )
        self.status_menu.set(room_data[4])
        self.status_menu.pack(padx=20, pady=5)
        
        # Кнопки
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(padx=20, pady=20, fill="x")
        
        self.delete_button = ctk.CTkButton(
            self.button_frame,
            text="Удалить",
            command=self.delete_room,
            fg_color="#e74c3c",
            width=90
        )
        self.delete_button.pack(side="left", padx=(0, 5))
        
        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Отмена",
            command=self.destroy,
            fg_color="gray",
            width=90
        )
        self.cancel_button.pack(side="left", padx=5)
        
        self.save_button = ctk.CTkButton(
            self.button_frame,
            text="Сохранить",
            command=self.save_changes,
            width=90
        )
        self.save_button.pack(side="right", padx=(5, 0))
    
    def save_changes(self):
        """Сохранение изменений"""
        price_str = self.price_entry.get().strip()
        
        # Валидация цены
        is_valid, price, error_msg = validate_price(price_str)
        if not is_valid:
            messagebox.showerror("Ошибка", error_msg, parent=self)
            return
        
        try:
            # Обновление типа и цены
            self.db.cursor.execute(
                "UPDATE rooms SET type = ?, price_per_night = ?, status = ? WHERE id = ?",
                (self.type_menu.get(), price, self.status_menu.get(), self.room_data[0])
            )
            self.db.conn.commit()
            
            messagebox.showinfo("Успех", "Изменения сохранены", parent=self)
            self.on_close_callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить изменения: {e}", parent=self)
    
    def delete_room(self):
        """Удаление номера"""
        if messagebox.askyesno(
            "Подтверждение",
            f"Вы уверены, что хотите удалить номер {self.room_data[1]}?\n"
            "Это действие нельзя отменить!",
            parent=self
        ):
            if self.db.delete_room(self.room_data[0]):
                messagebox.showinfo("Успех", "Номер удален", parent=self)
                self.on_close_callback()
                self.destroy()
            else:
                messagebox.showerror(
                    "Ошибка", 
                    "Нельзя удалить номер с активными бронированиями", 
                    parent=self
                )


class RoomCard(ctk.CTkFrame):
    """Карточка номера"""
    def __init__(self, master, room_data, on_click_callback):
        super().__init__(master, corner_radius=10)
        self.room_data = room_data
        self.on_click_callback = on_click_callback
        
        room_id, number, r_type, price, status = room_data
        
        # Цвет границы в зависимости от статуса
        border_color = AppConfig.STATUS_COLORS.get(status, "gray")
        self.configure(border_width=3, border_color=border_color)
        
        # Номер
        self.num_label = ctk.CTkLabel(
            self, 
            text=f"№ {number}", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.num_label.pack(pady=(15, 5))
        
        # Тип
        self.type_label = ctk.CTkLabel(
            self, 
            text=r_type,
            font=ctk.CTkFont(size=13)
        )
        self.type_label.pack(pady=3)
        
        # Цена
        self.price_label = ctk.CTkLabel(
            self, 
            text=format_currency(price) + "/ночь",
            font=ctk.CTkFont(size=12)
        )
        self.price_label.pack(pady=3)
        
        # Статус
        self.status_label = ctk.CTkLabel(
            self, 
            text=status, 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=border_color
        )
        self.status_label.pack(pady=(8, 15))
        
        # Кнопка редактирования
        self.edit_button = ctk.CTkButton(
            self,
            text="Редактировать",
            command=lambda: on_click_callback(room_data),
            width=120,
            height=30,
            font=ctk.CTkFont(size=11)
        )
        self.edit_button.pack(pady=(0, 10))
        
        # Hover эффект
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
    
    def on_hover(self, event):
        """Эффект при наведении"""
        self.configure(fg_color=("#e8e8e8", "#3a3a3a"))
    
    def on_leave(self, event):
        """Эффект при уходе курсора"""
        self.configure(fg_color=("#d8d8d8", "#2b2b2b"))


class RoomsFrame(ctk.CTkFrame):
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Верхняя панель ---
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.top_bar.grid_columnconfigure(1, weight=1)

        self.title = ctk.CTkLabel(
            self.top_bar, 
            text="Управление номерами", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title.grid(row=0, column=0, sticky="w", padx=(0, 20))

        self.add_room_button = ctk.CTkButton(
            self.top_bar, 
            text="+ Добавить номер", 
            command=self.open_add_room_dialog,
            height=35
        )
        self.add_room_button.grid(row=0, column=2, sticky="e")
        
        # --- Панель фильтров и поиска ---
        self.filter_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.filter_bar.grid_columnconfigure(2, weight=1)
        
        # Фильтр по статусу
        ctk.CTkLabel(self.filter_bar, text="Статус:").grid(row=0, column=0, padx=(0, 5))
        self.status_filter = ctk.CTkOptionMenu(
            self.filter_bar,
            values=["Все"] + list(AppConfig.STATUS_COLORS.keys()),
            command=lambda x: self.refresh_rooms_display(),
            width=140
        )
        self.status_filter.grid(row=0, column=1, padx=5)
        
        # Фильтр по типу
        ctk.CTkLabel(self.filter_bar, text="Тип:").grid(row=0, column=3, padx=(20, 5))
        self.type_filter = ctk.CTkOptionMenu(
            self.filter_bar,
            values=["Все"] + AppConfig.ROOM_TYPES,
            command=lambda x: self.refresh_rooms_display(),
            width=180
        )
        self.type_filter.grid(row=0, column=4, padx=5)
        
        # Поиск
        self.search_entry = ctk.CTkEntry(
            self.filter_bar,
            placeholder_text="Поиск по номеру...",
            width=200
        )
        self.search_entry.grid(row=0, column=5, padx=(20, 5))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_rooms_display())
        
        # Кнопка сброса фильтров
        self.reset_button = ctk.CTkButton(
            self.filter_bar,
            text="Сбросить",
            command=self.reset_filters,
            width=100,
            fg_color="gray"
        )
        self.reset_button.grid(row=0, column=6, padx=5)
        
        # Статистика
        self.stats_label = ctk.CTkLabel(
            self.filter_bar,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.stats_label.grid(row=0, column=7, padx=(20, 0), sticky="e")
        
        # --- Контейнер для карточек ---
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        
        # Адаптивная сетка (5 колонок)
        for i in range(5):
            self.scrollable_frame.grid_columnconfigure(i, weight=1, uniform="cols")

        self.refresh_rooms_display()

    def reset_filters(self):
        """Сброс всех фильтров"""
        self.status_filter.set("Все")
        self.type_filter.set("Все")
        self.search_entry.delete(0, 'end')
        self.refresh_rooms_display()

    def refresh_rooms_display(self):
        """Обновление отображения номеров"""
        # Очистка
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Получение всех номеров
        all_rooms = self.db.get_all_rooms()
        
        # Применение фильтров
        filtered_rooms = all_rooms
        
        # Фильтр по статусу
        status = self.status_filter.get()
        if status != "Все":
            filtered_rooms = [r for r in filtered_rooms if r[4] == status]
        
        # Фильтр по типу
        room_type = self.type_filter.get()
        if room_type != "Все":
            filtered_rooms = [r for r in filtered_rooms if r[2] == room_type]
        
        # Поиск по номеру
        search_query = self.search_entry.get().strip().lower()
        if search_query:
            filtered_rooms = [r for r in filtered_rooms if search_query in str(r[1]).lower()]
        
        # Обновление статистики
        total = len(all_rooms)
        shown = len(filtered_rooms)
        self.stats_label.configure(text=f"Показано: {shown} из {total}")
        
        # Отображение карточек
        if not filtered_rooms:
            no_rooms_label = ctk.CTkLabel(
                self.scrollable_frame,
                text="Номера не найдены" if search_query or status != "Все" or room_type != "Все" 
                     else "Добавьте первый номер",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            no_rooms_label.grid(row=0, column=0, columnspan=5, pady=50)
        else:
            row, col = 0, 0
            for room in filtered_rooms:
                card = RoomCard(
                    self.scrollable_frame, 
                    room, 
                    self.open_edit_room_dialog
                )
                card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
                
                col += 1
                if col >= 5:
                    col = 0
                    row += 1

    def open_add_room_dialog(self):
        """Открыть диалог добавления номера"""
        AddRoomDialog(self, self.db, on_close_callback=self.refresh_rooms_display)
    
    def open_edit_room_dialog(self, room_data):
        """Открыть диалог редактирования номера"""
        EditRoomDialog(self, self.db, room_data, on_close_callback=self.refresh_rooms_display)