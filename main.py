import customtkinter as ctk
from ui.main_app_window import MainAppWindow
from database import Database

if __name__ == "__main__":
    # Устанавливаем тему и цвет по умолчанию
    ctk.set_appearance_mode("System")  # Варианты: "System", "Dark", "Light"
    ctk.set_default_color_theme("blue") # Варианты: "blue", "green", "dark-blue"
    
    db = Database()
    
    app = MainAppWindow(db)
    app.mainloop()
    
    db.close()