import customtkinter as ctk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, date

class AddBookingDialog(ctk.CTkToplevel):
    def __init__(self, master, db, on_close_callback):
        super().__init__(master)
        self.db = db
        self.on_close_callback = on_close_callback

        self.title("Новое бронирование")
        self.geometry("450x650")
        self.transient(master)
        self.grab_set()

        # Скроллируемый контейнер
        self.scrollable = ctk.CTkScrollableFrame(self)
        self.scrollable.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Выбор комнаты ---
        self.room_label = ctk.CTkLabel(
            self.scrollable, 
            text="Выберите свободный номер:", 
            font=ctk.CTkFont(weight="bold")
        )
        self.room_label.pack(padx=20, pady=(10, 5))
        
        free_rooms = [
            f"№{r[1]} - {r[2]} ({r[3]} руб/ночь)" 
            for r in self.db.get_all_rooms() 
            if r[4] == self.db.ROOM_STATUS_FREE
        ]
        
        if not free_rooms:
            ctk.CTkLabel(
                self.scrollable, 
                text="Нет свободных номеров!", 
                text_color="red"
            ).pack(padx=20, pady=5)
            self.room_menu = None
        else:
            self.room_map = {
                f"№{r[1]} - {r[2]} ({r[3]} руб/ночь)": (r[0], r[3]) 
                for r in self.db.get_all_rooms() 
                if r[4] == self.db.ROOM_STATUS_FREE
            }
            self.room_menu = ctk.CTkOptionMenu(
                self.scrollable, 
                values=free_rooms,
                command=self.on_room_selected
            )
            self.room_menu.pack(padx=20, pady=5, fill="x")
        
        # --- Информация о госте ---
        ctk.CTkLabel(
            self.scrollable, 
            text="Информация о госте", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(padx=20, pady=(20, 10))
        
        # Поиск существующего гостя
        self.search_frame = ctk.CTkFrame(self.scrollable, fg_color="transparent")
        self.search_frame.pack(padx=20, pady=5, fill="x")
        
        self.search_entry = ctk.CTkEntry(
            self.search_frame, 
            placeholder_text="Поиск гостя по имени/телефону"
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.search_button = ctk.CTkButton(
            self.search_frame, 
            text="Найти", 
            width=80,
            command=self.search_guest
        )
        self.search_button.pack(side="right")
        
        # Поля для нового гостя
        self.guest_name_entry = ctk.CTkEntry(
            self.scrollable, 
            placeholder_text="ФИО *"
        )
        self.guest_name_entry.pack(padx=20, pady=5, fill="x")
        
        self.guest_phone_entry = ctk.CTkEntry(
            self.scrollable, 
            placeholder_text="Телефон"
        )
        self.guest_phone_entry.pack(padx=20, pady=5, fill="x")
        
        self.guest_email_entry = ctk.CTkEntry(
            self.scrollable, 
            placeholder_text="Email"
        )
        self.guest_email_entry.pack(padx=20, pady=5, fill="x")
        
        # --- Даты ---
        ctk.CTkLabel(
            self.scrollable, 
            text="Период бронирования", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(padx=20, pady=(20, 10))
        
        self.checkin_label = ctk.CTkLabel(self.scrollable, text="Дата заезда:")
        self.checkin_label.pack(padx=20, pady=(5, 2))
        self.checkin_entry = DateEntry(
            self.scrollable, 
            date_pattern='yyyy-mm-dd', 
            width=30,
            mindate=date.today()
        )
        self.checkin_entry.pack(padx=20, pady=5)
        self.checkin_entry.bind("<<DateEntrySelected>>", self.calculate_price)

        self.checkout_label = ctk.CTkLabel(self.scrollable, text="Дата выезда:")
        self.checkout_label.pack(padx=20, pady=(10, 2))
        self.checkout_entry = DateEntry(
            self.scrollable, 
            date_pattern='yyyy-mm-dd', 
            width=30,
            mindate=date.today()
        )
        self.checkout_entry.pack(padx=20, pady=5)
        self.checkout_entry.bind("<<DateEntrySelected>>", self.calculate_price)

        # --- Расчет стоимости ---
        self.price_frame = ctk.CTkFrame(self.scrollable, fg_color=("#d0d0d0", "#3a3a3a"))
        self.price_frame.pack(padx=20, pady=20, fill="x")
        
        self.nights_label = ctk.CTkLabel(
            self.price_frame, 
            text="Количество ночей: 0"
        )
        self.nights_label.pack(pady=(10, 5))
        
        self.total_label = ctk.CTkLabel(
            self.price_frame, 
            text="Итого: 0 руб", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.total_label.pack(pady=(5, 10))

        # Кнопки
        self.button_frame = ctk.CTkFrame(self.scrollable, fg_color="transparent")
        self.button_frame.pack(padx=20, pady=10, fill="x")
        
        self.cancel_button = ctk.CTkButton(
            self.button_frame, 
            text="Отмена", 
            command=self.destroy,
            fg_color="gray"
        )
        self.cancel_button.pack(side="left", expand=True, padx=(0, 5))
        
        self.save_button = ctk.CTkButton(
            self.button_frame, 
            text="Создать бронь", 
            command=self.save_booking
        )
        self.save_button.pack(side="right", expand=True, padx=(5, 0))
        
        self.selected_guest_id = None
    
    def search_guest(self):
        """Поиск гостя в базе"""
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Предупреждение", "Введите имя или телефон гостя", parent=self)
            return
        
        guests = self.db.search_guests(query)
        
        if not guests:
            messagebox.showinfo("Результат", "Гости не найдены", parent=self)
            return
        
        # Создаем диалог выбора гостя
        SelectGuestDialog(self, guests, self.fill_guest_data)
    
    def fill_guest_data(self, guest_data):
        """Заполнение полей данными выбранного гостя"""
        # Преобразуем sqlite3.Row в tuple если нужно
        if hasattr(guest_data, 'keys'):
            guest_data = tuple(guest_data)
        
        self.selected_guest_id = guest_data[0]
        self.guest_name_entry.delete(0, 'end')
        self.guest_name_entry.insert(0, guest_data[1])
        self.guest_phone_entry.delete(0, 'end')
        self.guest_phone_entry.insert(0, guest_data[2] or "")
        self.guest_email_entry.delete(0, 'end')
        self.guest_email_entry.insert(0, guest_data[3] or "")
    
    def on_room_selected(self, choice):
        """Обработка выбора номера"""
        self.calculate_price()
    
    def calculate_price(self, event=None):
        """Расчет итоговой стоимости"""
        if not self.room_menu:
            return
        
        try:
            room_display = self.room_menu.get()
            if not room_display or room_display not in self.room_map:
                return
            
            room_id, price_per_night = self.room_map[room_display]
            
            check_in = self.checkin_entry.get_date()
            check_out = self.checkout_entry.get_date()
            
            if check_out <= check_in:
                self.nights_label.configure(text="Количество ночей: 0")
                self.total_label.configure(text="Итого: 0 руб")
                return
            
            num_nights = (check_out - check_in).days
            total = price_per_night * num_nights
            
            self.nights_label.configure(text=f"Количество ночей: {num_nights}")
            self.total_label.configure(text=f"Итого: {total:,.2f} руб")
        except Exception as e:
            print(f"Ошибка расчета: {e}")
    
    def save_booking(self):
        """Сохранение бронирования"""
        if not self.room_menu:
            messagebox.showerror("Ошибка", "Нет доступных номеров", parent=self)
            return
        
        room_display = self.room_menu.get()
        if not room_display:
            messagebox.showerror("Ошибка", "Выберите номер", parent=self)
            return
        
        room_id, price_per_night = self.room_map[room_display]
        
        guest_name = self.guest_name_entry.get().strip()
        if not guest_name:
            messagebox.showerror("Ошибка", "Укажите ФИО гостя", parent=self)
            return
        
        check_in_date = self.checkin_entry.get_date()
        check_out_date = self.checkout_entry.get_date()

        if check_in_date >= check_out_date:
            messagebox.showerror(
                "Ошибка", 
                "Дата выезда должна быть позже даты заезда", 
                parent=self
            )
            return
        
        # Расчет стоимости
        num_nights = (check_out_date - check_in_date).days
        total_price = price_per_night * num_nights

        # Создаем или используем существующего гостя
        if self.selected_guest_id:
            guest_id = self.selected_guest_id
        else:
            guest_phone = self.guest_phone_entry.get().strip()
            guest_email = self.guest_email_entry.get().strip()
            guest_id = self.db.add_guest(guest_name, guest_phone, guest_email)
            
            if not guest_id:
                messagebox.showerror(
                    "Ошибка", 
                    "Не удалось добавить гостя", 
                    parent=self
                )
                return
        
        # Создаем бронирование
        booking_id = self.db.create_booking(
            room_id, 
            guest_id, 
            check_in_date.strftime('%Y-%m-%d'), 
            check_out_date.strftime('%Y-%m-%d'), 
            total_price
        )
        
        if booking_id:
            messagebox.showinfo(
                "Успех", 
                f"Бронь #{booking_id} для '{guest_name}' создана.\n"
                f"Период: {num_nights} ноч.\n"
                f"Стоимость: {total_price:,.2f} руб.", 
                parent=self
            )
            self.on_close_callback()
            self.destroy()
        else:
            messagebox.showerror(
                "Ошибка", 
                "Не удалось создать бронь. Возможно, номер уже занят на эти даты.", 
                parent=self
            )


class SelectGuestDialog(ctk.CTkToplevel):
    """Диалог выбора гостя из списка"""
    def __init__(self, master, guests, callback):
        super().__init__(master)
        self.callback = callback
        
        self.title("Выберите гостя")
        self.geometry("500x400")
        self.transient(master)
        self.grab_set()
        
        ctk.CTkLabel(
            self, 
            text="Найденные гости:", 
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(padx=20, pady=10)
        
        # Список гостей
        self.listbox_frame = ctk.CTkScrollableFrame(self)
        self.listbox_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        for guest in guests:
            guest_text = f"{guest[1]}\n{guest[2] or 'Нет телефона'} | {guest[3] or 'Нет email'}"
            btn = ctk.CTkButton(
                self.listbox_frame,
                text=guest_text,
                command=lambda g=guest: self.select_guest(g),
                anchor="w",
                height=60
            )
            btn.pack(fill="x", pady=5)
        
        ctk.CTkButton(
            self, 
            text="Отмена", 
            command=self.destroy,
            fg_color="gray"
        ).pack(pady=10)
    
    def select_guest(self, guest_data):
        """Обработка выбора гостя"""
        self.callback(guest_data)
        self.destroy()


class BookingsFrame(ctk.CTkFrame):
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # --- Верхняя панель ---
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.top_bar.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.top_bar.grid_columnconfigure(1, weight=1)
        
        self.title = ctk.CTkLabel(
            self.top_bar, 
            text="Бронирования", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        # Фильтр по статусу
        self.filter_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        self.filter_frame.grid(row=0, column=1, sticky="ew")
        
        ctk.CTkLabel(self.filter_frame, text="Статус:").pack(side="left", padx=(0, 5))
        self.status_filter = ctk.CTkOptionMenu(
            self.filter_frame,
            values=["Все", "Активно", "Завершено", "Отменено"],
            command=self.refresh_bookings_table,
            width=120
        )
        self.status_filter.pack(side="left")
        
        self.add_booking_button = ctk.CTkButton(
            self.top_bar, 
            text="+ Новое бронирование", 
            command=self.open_add_booking_dialog
        )
        self.add_booking_button.grid(row=0, column=2, sticky="e")
        
        # --- Таблица ---
        # Стилизация
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Bookings.Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        rowheight=30,
                        fieldbackground="#2b2b2b",
                        bordercolor="#343638",
                        borderwidth=0)
        style.map('Bookings.Treeview', background=[('selected', '#22559b')])
        style.configure("Bookings.Treeview.Heading",
                        background="#565b5e",
                        foreground="white",
                        relief="flat",
                        font=('TkDefaultFont', 10, 'bold'))
        style.map("Bookings.Treeview.Heading",
                  background=[('active', '#3484F0')])
        
        # Создание таблицы с прокруткой
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("ID", "Номер", "Гость", "Заезд", "Выезд", "Сумма", "Статус"),
            show="headings",
            style="Bookings.Treeview"
        )
        
        # Настройка колонок
        self.tree.heading("ID", text="ID")
        self.tree.heading("Номер", text="Номер")
        self.tree.heading("Гость", text="Гость")
        self.tree.heading("Заезд", text="Дата заезда")
        self.tree.heading("Выезд", text="Дата выезда")
        self.tree.heading("Сумма", text="Сумма")
        self.tree.heading("Статус", text="Статус")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Номер", width=80, anchor="center")
        self.tree.column("Гость", width=200)
        self.tree.column("Заезд", width=120, anchor="center")
        self.tree.column("Выезд", width=120, anchor="center")
        self.tree.column("Сумма", width=120, anchor="e")
        self.tree.column("Статус", width=100, anchor="center")
        
        # Скроллбары
        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Контекстное меню
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.show_booking_details)
        
        # --- Панель действий ---
        self.action_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.action_bar.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        self.complete_button = ctk.CTkButton(
            self.action_bar,
            text="Завершить бронь",
            command=self.complete_booking,
            fg_color="#2ecc71"
        )
        self.complete_button.pack(side="left", padx=5)
        
        self.cancel_button = ctk.CTkButton(
            self.action_bar,
            text="Отменить бронь",
            command=self.cancel_booking,
            fg_color="#e74c3c"
        )
        self.cancel_button.pack(side="left", padx=5)
        
        self.refresh_button = ctk.CTkButton(
            self.action_bar,
            text="Обновить",
            command=self.refresh_bookings_table,
            width=100
        )
        self.refresh_button.pack(side="right", padx=5)
        
        self.refresh_bookings_table()
        
    def refresh_bookings_table(self, *args):
        """Обновление таблицы бронирований"""
        # Очистка
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Получение данных
        bookings = self.db.get_all_bookings()
        
        # Фильтрация по статусу
        filter_status = self.status_filter.get()
        if filter_status != "Все":
            bookings = [b for b in bookings if b[6] == filter_status]
        
        # Вставка данных с форматированием
        for booking in bookings:
            values = list(booking)
            # Форматирование суммы
            values[5] = f"{values[5]:,.2f} руб"
            
            # Цветовая маркировка по статусу
            tags = ()
            if booking[6] == "Активно":
                tags = ('active',)
            elif booking[6] == "Завершено":
                tags = ('completed',)
            elif booking[6] == "Отменено":
                tags = ('cancelled',)
            
            self.tree.insert("", "end", values=values, tags=tags)
        
        # Настройка тегов
        self.tree.tag_configure('active', background='#27ae60', foreground='white')
        self.tree.tag_configure('completed', background='#34495e', foreground='lightgray')
        self.tree.tag_configure('cancelled', background='#c0392b', foreground='white')

    def show_context_menu(self, event):
        """Показать контекстное меню"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            menu = ctk.CTkToplevel(self)
            menu.withdraw()
            menu.overrideredirect(True)
            
            ctk.CTkButton(
                menu, 
                text="Просмотр деталей", 
                command=lambda: [self.show_booking_details(None), menu.destroy()]
            ).pack(fill="x", padx=2, pady=2)
            
            ctk.CTkButton(
                menu, 
                text="Завершить", 
                command=lambda: [self.complete_booking(), menu.destroy()],
                fg_color="#2ecc71"
            ).pack(fill="x", padx=2, pady=2)
            
            ctk.CTkButton(
                menu, 
                text="Отменить", 
                command=lambda: [self.cancel_booking(), menu.destroy()],
                fg_color="#e74c3c"
            ).pack(fill="x", padx=2, pady=2)
            
            menu.deiconify()
            menu.geometry(f"+{event.x_root}+{event.y_root}")
            menu.bind("<FocusOut>", lambda e: menu.destroy())
            menu.focus_set()

    def show_booking_details(self, event):
        """Показать детали бронирования"""
        selection = self.tree.selection()
        if not selection:
            return
        
        values = self.tree.item(selection[0])['values']
        
        details = f"""
Бронирование #{values[0]}
{'='*40}
Номер: {values[1]}
Гость: {values[2]}
Дата заезда: {values[3]}
Дата выезда: {values[4]}
Стоимость: {values[5]}
Статус: {values[6]}
        """
        
        messagebox.showinfo("Детали бронирования", details.strip(), parent=self)

    def complete_booking(self):
        """Завершить бронирование"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                "Предупреждение", 
                "Выберите бронирование", 
                parent=self
            )
            return
        
        booking_id = self.tree.item(selection[0])['values'][0]
        booking_status = self.tree.item(selection[0])['values'][6]
        
        if booking_status != "Активно":
            messagebox.showwarning(
                "Предупреждение", 
                "Можно завершить только активное бронирование", 
                parent=self
            )
            return
        
        if messagebox.askyesno(
            "Подтверждение", 
            f"Завершить бронь #{booking_id}?\nНомер будет переведен в статус 'На уборке'",
            parent=self
        ):
            if self.db.complete_booking(booking_id):
                messagebox.showinfo("Успех", "Бронь завершена", parent=self)
                self.refresh_bookings_table()
            else:
                messagebox.showerror("Ошибка", "Не удалось завершить бронь", parent=self)

    def cancel_booking(self):
        """Отменить бронирование"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                "Предупреждение", 
                "Выберите бронирование", 
                parent=self
            )
            return
        
        booking_id = self.tree.item(selection[0])['values'][0]
        booking_status = self.tree.item(selection[0])['values'][6]
        
        if booking_status != "Активно":
            messagebox.showwarning(
                "Предупреждение", 
                "Можно отменить только активное бронирование", 
                parent=self
            )
            return
        
        if messagebox.askyesno(
            "Подтверждение", 
            f"Отменить бронь #{booking_id}?\nНомер будет освобожден.",
            parent=self
        ):
            if self.db.cancel_booking(booking_id):
                messagebox.showinfo("Успех", "Бронь отменена", parent=self)
                self.refresh_bookings_table()
            else:
                messagebox.showerror("Ошибка", "Не удалось отменить бронь", parent=self)

    def open_add_booking_dialog(self):
        """Открыть диалог создания бронирования"""
        AddBookingDialog(self, self.db, on_close_callback=self.refresh_bookings_table)