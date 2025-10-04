import customtkinter as ctk

class StatCard(ctk.CTkFrame):
    def __init__(self, master, title, value_text):
        super().__init__(master, corner_radius=10)
        self.configure(fg_color=("#e0e0e0", "#2b2b2b"))

        self.title_label = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=16))
        self.title_label.pack(pady=(10, 5), padx=10)

        self.value_label = ctk.CTkLabel(self, text=value_text, font=ctk.CTkFont(size=36, weight="bold"))
        self.value_label.pack(pady=(5, 20), padx=10)

    def set_value(self, new_value):
        self.value_label.configure(text=str(new_value))

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, db):
        super().__init__(master, fg_color="transparent")
        self.db = db

        self.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.title = ctk.CTkLabel(self, text="Обзор", font=ctk.CTkFont(size=24, weight="bold"))
        self.title.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="w")
        
        # Создание карточек
        self.free_card = StatCard(self, "Свободно номеров", "0")
        self.free_card.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.occupied_card = StatCard(self, "Занято номеров", "0")
        self.occupied_card.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        self.checkin_card = StatCard(self, "Заездов сегодня", "0")
        self.checkin_card.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        self.checkout_card = StatCard(self, "Выездов сегодня", "0")
        self.checkout_card.grid(row=1, column=3, padx=10, pady=10, sticky="nsew")
        
        self.update_stats()

    def update_stats(self):
        stats = self.db.get_dashboard_stats()
        self.free_card.set_value(stats["free"])
        self.occupied_card.set_value(stats["occupied"])
        self.checkin_card.set_value(stats["check_ins"])
        self.checkout_card.set_value(stats["check_outs"])