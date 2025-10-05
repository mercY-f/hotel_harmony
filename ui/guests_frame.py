import customtkinter as ctk
from tkinter import ttk, messagebox
from utils import validate_phone, validate_email, format_phone


class EditGuestDialog(ctk.CTkToplevel):
    """Диалог редактирования гостя"""
    def __init__(self, master, db, guest_data, on_close_callback):
        super().__init__(master)
        self.db = db
        self.guest_data = guest_data
        self.on_close_callback = on_close_callback

        self.title(f"Редактировать гостя #{guest_data[0]}")
        self.geometry("400x500")
        self.transient(master)
        self.grab_set()
        
        # Заголовок
        ctk.CTkLabel(
            self, 
            text=f"Гость #{guest_data[0]}", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(padx=20, pady=(20, 10))

        # ФИО
        self.name_label = ctk.CTkLabel(self, text="ФИО: *")
        self.name_label.pack(padx=20, pady=(10, 5), anchor="w")
        self.name_entry = ctk.CTkEntry(self, width=300)
        self.name_entry.insert(0, guest_data[1])
        self.name_entry.pack(padx=20, pady=5)

        # Телефон
        self.phone_label = ctk.CTkLabel(self, text="Номер телефона:")
        self.phone_label.pack(padx=20, pady=(10, 5), anchor="w")
        self.phone_entry = ctk.CTkEntry(self, width=300)
        self.phone_entry.insert(0, guest_data[2] or "")
        self.phone_entry.pack(padx=20, pady=5)

        # Email
        self.email_label = ctk.CTkLabel(self, text="Email:")
        self.email_label.pack(padx=20, pady=(10, 5), anchor="w")
        self.email_entry = ctk.CTkEntry(self, width=300)
        self.email_entry.insert(0, guest_data[3] or "")
        self.email_entry.pack(padx=20, pady=5)
        
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
        
        self.delete_button = ctk.CTkButton(
            self.button_frame,
            text="Удалить",
            command=self.delete_guest,
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
        full_name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()

        # Валидация ФИО
        if not full_name:
            messagebox.showerror("Ошибка", "ФИО гостя не может быть пустым.", parent=self)
            self.name_entry.focus()
            return

        # Валидация телефона
        if phone and not validate_phone(phone):
            messagebox.showerror(
                "Ошибка", 
                "Некорректный формат телефона.\nИспользуйте: +7XXXXXXXXXX или 8XXXXXXXXXX", 
                parent=self
            )
            self.phone_entry.focus()
            return
        
        # Валидация email
        if email and not validate_email(email):
            messagebox.showerror(
                "Ошибка", 
                "Некорректный формат email.", 
                parent=self
            )
            self.email_entry.focus()
            return

        # Форматируем телефон
        if phone:
            phone = format_phone(phone)
        
        try:
            # Обновление данных
            self.db.cursor.execute(
                "UPDATE guests SET full_name = ?, phone_number = ?, email = ? WHERE id = ?",
                (full_name, phone, email, self.guest_data[0])
            )
            self.db.conn.commit()
            
            messagebox.showinfo("Успех", "Данные гостя обновлены", parent=self)
            self.on_close_callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить изменения: {e}", parent=self)
    
    def delete_guest(self):
        """Удаление гостя"""
        # Проверяем наличие активных броней
        self.db.cursor.execute(
            "SELECT COUNT(*) FROM bookings WHERE guest_id = ? AND status = ?",
            (self.guest_data[0], self.db.BOOKING_STATUS_ACTIVE)
        )
        active_bookings = self.db.cursor.fetchone()[0]
        
        if active_bookings > 0:
            messagebox.showerror(
                "Ошибка",
                f"Нельзя удалить гостя с активными бронированиями!\n"
                f"Активных броней: {active_bookings}",
                parent=self
            )
            return
        
        if messagebox.askyesno(
            "Подтверждение",
            f"Вы уверены, что хотите удалить гостя '{self.guest_data[1]}'?\n"
            "Это действие нельзя отменить!",
            parent=self
        ):
            try:
                self.db.cursor.execute("DELETE FROM guests WHERE id = ?", (self.guest_data[0],))
                self.db.conn.commit()
                
                messagebox.showinfo("Успех", "Гость удален", parent=self)
                self.on_close_callback()
                self.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить гостя: {e}", parent=self)


class AddGuestDialog(ctk.CTkToplevel):
    def __init__(self, master, db, on_close_callback):
        super().__init__(master)
        self.db = db
        self.on_close_callback = on_close_callback

        self.title("Добавить гостя")
        self.geometry("400x450")
        self.transient(master)
        self.grab_set()
        
        # Заголовок
        ctk.CTkLabel(
            self, 
            text="Новый гость", 
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(padx=20, pady=(20, 10))

        # ФИО
        self.name_label = ctk.CTkLabel(self, text="ФИО: *")
        self.name_label.pack(padx=20, pady=(10, 5), anchor="w")
        self.name_entry = ctk.CTkEntry(
            self, 
            placeholder_text="Иванов Иван Иванович", 
            width=300
        )
        self.name_entry.pack(padx=20, pady=5)

        # Телефон
        self.phone_label = ctk.CTkLabel(self, text="Номер телефона:")
        self.phone_label.pack(padx=20, pady=(10, 5), anchor="w")
        self.phone_entry = ctk.CTkEntry(
            self, 
            placeholder_text="+7 (999) 123-45-67", 
            width=300
        )
        self.phone_entry.pack(padx=20, pady=5)

        # Email
        self.email_label = ctk.CTkLabel(self, text="Email:")
        self.email_label.pack(padx=20, pady=(10, 5), anchor="w")
        self.email_entry = ctk.CTkEntry(
            self, 
            placeholder_text="example@mail.com", 
            width=300
        )
        self.email_entry.pack(padx=20, pady=5)
        
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
            command=self.save_guest,
            width=140
        )
        self.save_button.pack(side="right", expand=True, padx=(5, 0))

    def save_guest(self):
        """Сохранение гостя с валидацией"""
        full_name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()

        # Валидация ФИО
        if not full_name:
            messagebox.showerror("Ошибка", "ФИО гостя не может быть пустым.", parent=self)
            self.name_entry.focus()
            return

        # Валидация телефона
        if phone and not validate_phone(phone):
            messagebox.showerror(
                "Ошибка", 
                "Некорректный формат телефона.\nИспользуйте: +7XXXXXXXXXX или 8XXXXXXXXXX", 
                parent=self
            )
            self.phone_entry.focus()
            return
        
        # Валидация email
        if email and not validate_email(email):
            messagebox.showerror(
                "Ошибка", 
                "Некорректный формат email.", 
                parent=self
            )
            self.email_entry.focus()
            return

        # Форматируем телефон
        if phone:
            phone = format_phone(phone)

        # Добавляем гостя
        guest_id = self.db.add_guest(full_name, phone, email)
        if guest_id:
            messagebox.showinfo(
                "Успех", 
                f"Гость '{full_name}' успешно добавлен.", 
                parent=self
            )
            self.on_close_callback()
            self.destroy()
        else:
            messagebox.showwarning(
                "Предупреждение", 
                "Гость с такими данными уже существует.", 
                parent=self
            )


class GuestsFrame(ctk.CTkFrame):
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
            text="Гости", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title.grid(row=0, column=0, sticky="w", padx=(0, 20))
        
        self.add_guest_button = ctk.CTkButton(
            self.top_bar, 
            text="+ Добавить гостя", 
            command=self.open_add_guest_dialog,
            height=35
        )
        self.add_guest_button.grid(row=0, column=2, sticky="e")
        
        # --- Панель поиска ---
        self.search_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.search_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.search_bar.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(self.search_bar, text="Поиск:").grid(row=0, column=0, padx=(0, 5))
        
        self.search_entry = ctk.CTkEntry(
            self.search_bar,
            placeholder_text="Введите ФИО, телефон или email...",
            width=300
        )
        self.search_entry.grid(row=0, column=1, padx=5, sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_guests_table())
        
        self.clear_search_button = ctk.CTkButton(
            self.search_bar,
            text="Очистить",
            command=self.clear_search,
            width=100,
            fg_color="gray"
        )
        self.clear_search_button.grid(row=0, column=2, padx=5)
        
        self.stats_label = ctk.CTkLabel(
            self.search_bar,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.stats_label.grid(row=0, column=3, padx=(20, 0))
        
        # --- Таблица с гостями ---
        # Стилизация Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Guests.Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        rowheight=30,
                        fieldbackground="#2b2b2b",
                        bordercolor="#343638",
                        borderwidth=0)
        style.map('Guests.Treeview', background=[('selected', '#22559b')])
        style.configure("Guests.Treeview.Heading",
                        background="#565b5e",
                        foreground="white",
                        relief="flat",
                        font=('TkDefaultFont', 10, 'bold'))
        style.map("Guests.Treeview.Heading",
                  background=[('active', '#3484F0')])

        # Создание таблицы с прокруткой
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.tree_frame.grid_rowconfigure(0, weight=1)
        self.tree_frame.grid_columnconfigure(0, weight=1)
        
        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("ID", "ФИО", "Телефон", "Email"),
            show="headings",
            style="Guests.Treeview"
        )
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("ФИО", text="ФИО")
        self.tree.heading("Телефон", text="Телефон")
        self.tree.heading("Email", text="Email")
        
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("ФИО", width=300)
        self.tree.column("Телефон", width=200)
        self.tree.column("Email", width=250)
        
        # Скроллбары
        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Контекстное меню (правая кнопка мыши)
        self.tree.bind("<Button-3>", self.show_context_menu)
        # Двойной клик для редактирования
        self.tree.bind("<Double-1>", self.open_edit_guest_dialog)
        
        # --- Панель действий ---
        self.action_bar = ctk.CTkFrame(self, fg_color="transparent")
        self.action_bar.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        self.edit_button = ctk.CTkButton(
            self.action_bar,
            text="Редактировать",
            command=self.open_edit_guest_dialog,
            fg_color="#3498db",
            width=120
        )
        self.edit_button.pack(side="left", padx=5)
        
        self.delete_button = ctk.CTkButton(
            self.action_bar,
            text="Удалить",
            command=self.delete_guest,
            fg_color="#e74c3c",
            width=120
        )
        self.delete_button.pack(side="left", padx=5)
        
        self.refresh_button = ctk.CTkButton(
            self.action_bar,
            text="Обновить",
            command=self.refresh_guests_table,
            width=100
        )
        self.refresh_button.pack(side="right", padx=5)
        
        self.refresh_guests_table()
    
    def clear_search(self):
        """Очистка поиска"""
        self.search_entry.delete(0, 'end')
        self.refresh_guests_table()
    
    def show_context_menu(self, event):
        """Показать контекстное меню (правая кнопка мыши)"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            
            # Создаем всплывающее меню
            menu = ctk.CTkToplevel(self)
            menu.withdraw()
            menu.overrideredirect(True)
            
            ctk.CTkButton(
                menu, 
                text="📝 Редактировать", 
                command=lambda: [self.open_edit_guest_dialog(), menu.destroy()],
                fg_color="#3498db",
                anchor="w"
            ).pack(fill="x", padx=2, pady=2)
            
            ctk.CTkButton(
                menu, 
                text="ℹ️ Информация", 
                command=lambda: [self.show_guest_details(None), menu.destroy()],
                fg_color="gray",
                anchor="w"
            ).pack(fill="x", padx=2, pady=2)
            
            # Разделитель
            ctk.CTkFrame(menu, height=2, fg_color="#555").pack(fill="x", padx=5, pady=3)
            
            ctk.CTkButton(
                menu, 
                text="🗑️ Удалить", 
                command=lambda: [self.delete_guest(), menu.destroy()],
                fg_color="#e74c3c",
                anchor="w"
            ).pack(fill="x", padx=2, pady=2)
            
            menu.deiconify()
            menu.geometry(f"+{event.x_root}+{event.y_root}")
            menu.bind("<FocusOut>", lambda e: menu.destroy())
            menu.focus_set()
    
    def open_edit_guest_dialog(self, event=None):
        """Открыть диалог редактирования гостя"""
        selection = self.tree.selection()
        if not selection:
            if event is None:  # Вызвано кнопкой, а не двойным кликом
                messagebox.showwarning(
                    "Предупреждение",
                    "Выберите гостя для редактирования",
                    parent=self
                )
            return
        
        values = self.tree.item(selection[0])['values']
        
        # Получаем полные данные из БД
        self.db.cursor.execute(
            "SELECT id, full_name, phone_number, email FROM guests WHERE id = ?",
            (values[0],)
        )
        guest_data = self.db.cursor.fetchone()
        
        if guest_data:
            EditGuestDialog(self, self.db, guest_data, on_close_callback=self.refresh_guests_table)
    
    def delete_guest(self):
        """Удалить гостя"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                "Предупреждение",
                "Выберите гостя для удаления",
                parent=self
            )
            return
        
        values = self.tree.item(selection[0])['values']
        guest_id = values[0]
        guest_name = values[1]
        
        # Проверяем наличие активных броней
        self.db.cursor.execute(
            "SELECT COUNT(*) FROM bookings WHERE guest_id = ? AND status = ?",
            (guest_id, self.db.BOOKING_STATUS_ACTIVE)
        )
        active_bookings = self.db.cursor.fetchone()[0]
        
        if active_bookings > 0:
            messagebox.showerror(
                "Ошибка",
                f"Нельзя удалить гостя с активными бронированиями!\n"
                f"Активных броней: {active_bookings}",
                parent=self
            )
            return
        
        if messagebox.askyesno(
            "Подтверждение",
            f"Вы уверены, что хотите удалить гостя '{guest_name}'?\n"
            "Это действие нельзя отменить!",
            parent=self
        ):
            try:
                self.db.cursor.execute("DELETE FROM guests WHERE id = ?", (guest_id,))
                self.db.conn.commit()
                
                messagebox.showinfo("Успех", "Гость удален", parent=self)
                self.refresh_guests_table()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить гостя: {e}", parent=self)
    
    def show_guest_details(self, event):
        """Показать детали гостя"""
        selection = self.tree.selection()
        if not selection:
            return
        
        values = self.tree.item(selection[0])['values']
        
        # Получаем историю броней
        self.db.cursor.execute(
            """SELECT COUNT(*) FROM bookings 
               WHERE guest_id = ? AND status = ?""",
            (values[0], self.db.BOOKING_STATUS_ACTIVE)
        )
        active_bookings = self.db.cursor.fetchone()[0]
        
        self.db.cursor.execute(
            """SELECT COUNT(*) FROM bookings 
               WHERE guest_id = ?""",
            (values[0],)
        )
        total_bookings = self.db.cursor.fetchone()[0]
        
        details = f"""
Гость #{values[0]}
{'='*40}
ФИО: {values[1]}
Телефон: {values[2] or 'Не указан'}
Email: {values[3] or 'Не указан'}

История бронирований:
  • Всего броней: {total_bookings}
  • Активных: {active_bookings}
        """
        
        messagebox.showinfo("Информация о госте", details.strip(), parent=self)
        
    def refresh_guests_table(self):
        """Обновление таблицы гостей"""
        # Очистка таблицы
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Получение данных
        search_query = self.search_entry.get().strip()
        
        if search_query:
            guests = self.db.search_guests(search_query)
        else:
            guests = self.db.get_all_guests()
        
        # ВАЖНО: Преобразование sqlite3.Row в tuple/list
        processed_guests = []
        for guest in guests:
            if hasattr(guest, 'keys'):  # Это sqlite3.Row объект
                processed_guests.append(tuple(guest))
            else:  # Это уже tuple
                processed_guests.append(guest)
        
        # Вставка данных
        for guest in processed_guests:
            # Заменяем None на пустую строку для красоты
            display_values = [
                guest[0],  # ID
                guest[1],  # ФИО
                guest[2] if guest[2] else "",  # Телефон
                guest[3] if guest[3] else ""   # Email
            ]
            self.tree.insert("", "end", values=display_values)
        
        # Обновление статистики
        total_count = len(self.db.get_all_guests())
        shown_count = len(processed_guests)
        
        if search_query:
            self.stats_label.configure(text=f"Найдено: {shown_count} из {total_count}")
        else:
            self.stats_label.configure(text=f"Всего гостей: {total_count}")

    def open_add_guest_dialog(self):
        """Открыть диалог добавления гостя"""
        AddGuestDialog(self, self.db, on_close_callback=self.refresh_guests_table)