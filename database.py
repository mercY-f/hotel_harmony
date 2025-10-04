import sqlite3
from datetime import date
from typing import Optional, List, Tuple, Dict
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Кастомное исключение для ошибок БД"""
    pass


class Database:
    # Константы для статусов
    ROOM_STATUS_FREE = "Свободен"
    ROOM_STATUS_OCCUPIED = "Занят"
    ROOM_STATUS_CLEANING = "На уборке"
    ROOM_STATUS_REPAIR = "Ремонт"
    
    BOOKING_STATUS_ACTIVE = "Активно"
    BOOKING_STATUS_COMPLETED = "Завершено"
    BOOKING_STATUS_CANCELLED = "Отменено"
    
    def __init__(self, db_file="hotel.db"):
        try:
            self.conn = sqlite3.connect(db_file, check_same_thread=False)
            # Убираем row_factory чтобы возвращались обычные tuples
            # self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            self._create_tables()
            logger.info(f"Подключение к БД '{db_file}' успешно")
        except sqlite3.Error as e:
            logger.error(f"Ошибка подключения к БД: {e}")
            raise DatabaseError(f"Не удалось подключиться к базе данных: {e}")

    def _create_tables(self):
        """Создание таблиц с индексами для оптимизации"""
        try:
            # Таблица номеров
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS rooms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    number TEXT NOT NULL UNIQUE,
                    type TEXT NOT NULL,
                    price_per_night REAL NOT NULL CHECK(price_per_night > 0),
                    status TEXT NOT NULL DEFAULT 'Свободен',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Таблица гостей
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS guests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL,
                    phone_number TEXT,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(full_name, phone_number)
                );
            """)
            
            # Таблица бронирований
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_id INTEGER NOT NULL,
                    guest_id INTEGER NOT NULL,
                    check_in_date TEXT NOT NULL,
                    check_out_date TEXT NOT NULL,
                    total_price REAL NOT NULL CHECK(total_price >= 0),
                    status TEXT NOT NULL DEFAULT 'Активно',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE,
                    FOREIGN KEY (guest_id) REFERENCES guests (id) ON DELETE CASCADE,
                    CHECK(check_out_date > check_in_date)
                );
            """)
            
            # Индексы для ускорения запросов
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_rooms_status 
                ON rooms(status);
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_bookings_dates 
                ON bookings(check_in_date, check_out_date);
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_bookings_status 
                ON bookings(status);
            """)
            
            self.conn.commit()
            logger.info("Таблицы и индексы успешно созданы/проверены")
        except sqlite3.Error as e:
            logger.error(f"Ошибка создания таблиц: {e}")
            raise DatabaseError(f"Не удалось создать таблицы: {e}")

    # --- Room Methods ---
    def add_room(self, number: str, r_type: str, price: float) -> bool:
        """Добавление нового номера"""
        try:
            if not number or not r_type or price <= 0:
                logger.warning("Попытка добавить номер с некорректными данными")
                return False
            
            self.cursor.execute(
                "INSERT INTO rooms (number, type, price_per_night, status) VALUES (?, ?, ?, ?)",
                (number.strip(), r_type.strip(), price, self.ROOM_STATUS_FREE)
            )
            self.conn.commit()
            logger.info(f"Номер '{number}' успешно добавлен")
            return True
        except sqlite3.IntegrityError:
            logger.warning(f"Номер '{number}' уже существует")
            return False
        except sqlite3.Error as e:
            logger.error(f"Ошибка добавления номера: {e}")
            self.conn.rollback()
            return False

    def get_all_rooms(self) -> List[Tuple]:
        """Получение всех номеров"""
        try:
            self.cursor.execute("SELECT * FROM rooms ORDER BY CAST(number AS INTEGER)")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения номеров: {e}")
            return []

    def get_room_by_id(self, room_id: int) -> Optional[Tuple]:
        """Получение номера по ID"""
        try:
            self.cursor.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения номера #{room_id}: {e}")
            return None

    def update_room_status(self, room_id: int, status: str) -> bool:
        """Обновление статуса номера"""
        try:
            self.cursor.execute(
                "UPDATE rooms SET status = ? WHERE id = ?", 
                (status, room_id)
            )
            self.conn.commit()
            logger.info(f"Статус номера #{room_id} изменен на '{status}'")
            return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка обновления статуса: {e}")
            self.conn.rollback()
            return False

    def delete_room(self, room_id: int) -> bool:
        """Удаление номера (если нет активных броней)"""
        try:
            # Проверка активных броней
            self.cursor.execute(
                "SELECT COUNT(*) FROM bookings WHERE room_id = ? AND status = ?",
                (room_id, self.BOOKING_STATUS_ACTIVE)
            )
            if self.cursor.fetchone()[0] > 0:
                logger.warning(f"Нельзя удалить номер #{room_id} - есть активные брони")
                return False
            
            self.cursor.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
            self.conn.commit()
            logger.info(f"Номер #{room_id} удален")
            return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка удаления номера: {e}")
            self.conn.rollback()
            return False

    # --- Guest Methods ---
    def add_guest(self, full_name: str, phone: str = "", email: str = "") -> Optional[int]:
        """Добавление гостя"""
        try:
            if not full_name or not full_name.strip():
                logger.warning("Попытка добавить гостя без имени")
                return None
            
            self.cursor.execute(
                "INSERT INTO guests (full_name, phone_number, email) VALUES (?, ?, ?)",
                (full_name.strip(), phone.strip(), email.strip())
            )
            self.conn.commit()
            guest_id = self.cursor.lastrowid
            logger.info(f"Гость '{full_name}' добавлен с ID {guest_id}")
            return guest_id
        except sqlite3.IntegrityError:
            logger.warning(f"Гость '{full_name}' с таким телефоном уже существует")
            # Возвращаем ID существующего гостя
            self.cursor.execute(
                "SELECT id FROM guests WHERE full_name = ? AND phone_number = ?",
                (full_name.strip(), phone.strip())
            )
            result = self.cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            logger.error(f"Ошибка добавления гостя: {e}")
            self.conn.rollback()
            return None

    def get_all_guests(self) -> List[Tuple]:
        """Получение всех гостей"""
        try:
            self.cursor.execute(
                "SELECT id, full_name, phone_number, email FROM guests ORDER BY full_name"
            )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения гостей: {e}")
            return []

    def search_guests(self, query: str) -> List[Tuple]:
        """Поиск гостей по имени, телефону или email"""
        try:
            search_pattern = f"%{query}%"
            self.cursor.execute(
                """SELECT id, full_name, phone_number, email 
                   FROM guests 
                   WHERE full_name LIKE ? OR phone_number LIKE ? OR email LIKE ?
                   ORDER BY full_name""",
                (search_pattern, search_pattern, search_pattern)
            )
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Ошибка поиска гостей: {e}")
            return []

    # --- Booking Methods ---
    def create_booking(self, room_id: int, guest_id: int, check_in: str, 
                      check_out: str, total_price: float) -> Optional[int]:
        """Создание бронирования"""
        try:
            # Проверка доступности номера
            if not self._is_room_available(room_id, check_in, check_out):
                logger.warning(f"Номер #{room_id} недоступен на указанные даты")
                return None
            
            self.cursor.execute(
                """INSERT INTO bookings 
                   (room_id, guest_id, check_in_date, check_out_date, total_price, status) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (room_id, guest_id, check_in, check_out, total_price, self.BOOKING_STATUS_ACTIVE)
            )
            booking_id = self.cursor.lastrowid
            self.update_room_status(room_id, self.ROOM_STATUS_OCCUPIED)
            self.conn.commit()
            logger.info(f"Бронь #{booking_id} создана")
            return booking_id
        except sqlite3.Error as e:
            logger.error(f"Ошибка создания брони: {e}")
            self.conn.rollback()
            return None

    def _is_room_available(self, room_id: int, check_in: str, check_out: str) -> bool:
        """Проверка доступности номера на указанные даты"""
        try:
            self.cursor.execute(
                """SELECT COUNT(*) FROM bookings 
                   WHERE room_id = ? 
                   AND status = ?
                   AND NOT (check_out_date <= ? OR check_in_date >= ?)""",
                (room_id, self.BOOKING_STATUS_ACTIVE, check_in, check_out)
            )
            return self.cursor.fetchone()[0] == 0
        except sqlite3.Error as e:
            logger.error(f"Ошибка проверки доступности: {e}")
            return False

    def get_all_bookings(self) -> List[Tuple]:
        """Получение всех бронирований"""
        try:
            query = """
                SELECT
                    b.id,
                    r.number,
                    g.full_name,
                    b.check_in_date,
                    b.check_out_date,
                    b.total_price,
                    b.status
                FROM bookings b
                JOIN rooms r ON b.room_id = r.id
                JOIN guests g ON b.guest_id = g.id
                ORDER BY b.check_in_date DESC
            """
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения броней: {e}")
            return []

    def cancel_booking(self, booking_id: int) -> bool:
        """Отмена бронирования"""
        try:
            # Получаем информацию о брони
            self.cursor.execute(
                "SELECT room_id FROM bookings WHERE id = ?", 
                (booking_id,)
            )
            result = self.cursor.fetchone()
            if not result:
                return False
            
            room_id = result[0]
            
            # Обновляем статус брони
            self.cursor.execute(
                "UPDATE bookings SET status = ? WHERE id = ?",
                (self.BOOKING_STATUS_CANCELLED, booking_id)
            )
            
            # Освобождаем номер
            self.update_room_status(room_id, self.ROOM_STATUS_FREE)
            
            self.conn.commit()
            logger.info(f"Бронь #{booking_id} отменена")
            return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка отмены брони: {e}")
            self.conn.rollback()
            return False

    def complete_booking(self, booking_id: int) -> bool:
        """Завершение бронирования (выезд)"""
        try:
            self.cursor.execute(
                "SELECT room_id FROM bookings WHERE id = ?", 
                (booking_id,)
            )
            result = self.cursor.fetchone()
            if not result:
                return False
            
            room_id = result[0]
            
            self.cursor.execute(
                "UPDATE bookings SET status = ? WHERE id = ?",
                (self.BOOKING_STATUS_COMPLETED, booking_id)
            )
            self.update_room_status(room_id, self.ROOM_STATUS_CLEANING)
            
            self.conn.commit()
            logger.info(f"Бронь #{booking_id} завершена")
            return True
        except sqlite3.Error as e:
            logger.error(f"Ошибка завершения брони: {e}")
            self.conn.rollback()
            return False

    def get_dashboard_stats(self) -> Dict[str, int]:
        """Получение статистики для дашборда"""
        try:
            today = date.today().strftime("%Y-%m-%d")
            
            self.cursor.execute(
                "SELECT COUNT(*) FROM rooms WHERE status = ?", 
                (self.ROOM_STATUS_FREE,)
            )
            free_rooms = self.cursor.fetchone()[0]
            
            self.cursor.execute(
                "SELECT COUNT(*) FROM rooms WHERE status = ?", 
                (self.ROOM_STATUS_OCCUPIED,)
            )
            occupied_rooms = self.cursor.fetchone()[0]
            
            self.cursor.execute(
                "SELECT COUNT(*) FROM bookings WHERE check_in_date = ? AND status = ?", 
                (today, self.BOOKING_STATUS_ACTIVE)
            )
            check_ins_today = self.cursor.fetchone()[0]
            
            self.cursor.execute(
                "SELECT COUNT(*) FROM bookings WHERE check_out_date = ? AND status = ?", 
                (today, self.BOOKING_STATUS_ACTIVE)
            )
            check_outs_today = self.cursor.fetchone()[0]
            
            return {
                "free": free_rooms,
                "occupied": occupied_rooms,
                "check_ins": check_ins_today,
                "check_outs": check_outs_today
            }
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {"free": 0, "occupied": 0, "check_ins": 0, "check_outs": 0}

    def get_revenue_stats(self, start_date: str = None, end_date: str = None) -> float:
        """Получение статистики по доходам за период"""
        try:
            if start_date and end_date:
                self.cursor.execute(
                    """SELECT SUM(total_price) FROM bookings 
                       WHERE status IN (?, ?) 
                       AND check_in_date BETWEEN ? AND ?""",
                    (self.BOOKING_STATUS_ACTIVE, self.BOOKING_STATUS_COMPLETED, 
                     start_date, end_date)
                )
            else:
                self.cursor.execute(
                    """SELECT SUM(total_price) FROM bookings 
                       WHERE status IN (?, ?)""",
                    (self.BOOKING_STATUS_ACTIVE, self.BOOKING_STATUS_COMPLETED)
                )
            
            result = self.cursor.fetchone()[0]
            return result if result else 0.0
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения статистики доходов: {e}")
            return 0.0

    def close(self):
        """Закрытие соединения с БД"""
        try:
            self.conn.close()
            logger.info("Соединение с БД закрыто")
        except sqlite3.Error as e:
            logger.error(f"Ошибка закрытия БД: {e}")