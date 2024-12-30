import psycopg2
import time
from functools import wraps

def timeit(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000
        print(f"\nFunction '{func.__name__}' executed in {elapsed_time:.4f} milliseconds\n")
        return result
    return wrapper

class Model:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname = 'Vitaliy',
            user = 'postgres',
            password = 'Edlk30112003#',
            host = 'localhost',
            port = 5432
        )

    # Дістати всі рядки
    @timeit
    def get_data(self, table_name):
        """Отримує всі дані з таблиці."""
        cursor = self.conn.cursor()
        try:
            cursor.execute(f'SELECT * FROM "{table_name}"')
            result = cursor.fetchall()
            print(f"Fetched {len(result)} rows from {table_name}.")
        except Exception as e:
            print(f"An error occurred while fetching data: {e}")
            result = []
        finally:
            self.conn.rollback()
            cursor.close()
        
        return result

    # Перегляд даних із фільтрацією
    @timeit
    def get_data_in_range(self, table_name, id_field, id_start, id_end, order_field):
        c = self.conn.cursor()
        try:
            query = f'SELECT * FROM "{table_name}" WHERE {id_field} BETWEEN {id_start} AND {id_end} ORDER BY {order_field}'
            c.execute(query)
            result = c.fetchall()
        except Exception as e:
            print(f"An error occurred: {e}")
            result = None
        finally:
            self.conn.rollback()
            c.close()
        return result

    # Пошук за шаблоном LIKE
    @timeit
    def get_data_by_field_like(self, table_name, req_field, search_req, order_field):
        c = self.conn.cursor()
        try:
            query = f"SELECT * FROM {table_name} WHERE {req_field} LIKE '%{search_req}%' ORDER BY {order_field}"
            c.execute(query)
            result = c.fetchall()
        except Exception as e:
            print(f"An error occurred: {e}")
            result = None
        finally:
            self.conn.rollback()
            c.close()
        return result

    # Додавання запису в таблицю `users`
    @timeit
    def add_user(self, user_id, name, phone_number):
        c = self.conn.cursor()
        try:
            query = "INSERT INTO users (user_id, name, phone_number) VALUES (%s, %s, %s)"
            c.execute(query, (user_id, name, phone_number))
            self.conn.commit()
            print("User added successfully.")
        except Exception as e:
            self.conn.rollback()
            print(f"An error occurred: {e}")
        finally:
            self.conn.rollback()
            c.close()

    # Генерація записів для `users`
    @timeit
    def generate_users(self, num_users):
        """Generate random users with only user_id, name, and phone_number."""
        try:
            # Fetch maximum user_id to avoid duplicates
            query = 'SELECT MAX(user_id) FROM users'
            max_user_id = self.fetch_query(query)
            max_user_id = max_user_id[0][0] if max_user_id[0][0] else 0

            # Generate random users
            query = f"""
                WITH generated_users AS (
                    SELECT 
                        (ROW_NUMBER() OVER () + {max_user_id}) AS user_id,
                        'User_' || FLOOR(RANDOM() * 1000) AS name,  -- Random name
                        '380' || FLOOR(RANDOM() * 10000000) AS phone_number  -- Random phone number in format 380xxxxxxxxx
                    FROM generate_series(1, {num_users})
                )
                INSERT INTO users (user_id, name, phone_number)
                SELECT user_id, name, phone_number
                FROM generated_users
            """
            self.execute_query(query)
            print(f"{num_users} users generated successfully.")

        except Exception as e:
            print(f"Error generating users: {str(e)}")

    
    # Оновлення запису для таблиці `users`
    @timeit
    def update_user(self, user_id, name=None, phone_number=None):
        c = self.conn.cursor()
        try:
            query = "UPDATE users SET name = COALESCE(%s, name), phone_number = COALESCE(%s, phone_number) WHERE user_id = %s"
            c.execute(query, (name, phone_number, user_id))
            self.conn.commit()
            print(f"User {user_id} updated successfully.")
        except Exception as e:
            print(f"Error updating user: {e}")
        finally:
            self.conn.rollback()
            c.close()

    @timeit
    def add_service(self, service_id, service_name, price):
        """Додавання нового сервісу до таблиці."""
        c = self.conn.cursor()
        try:
            query = "INSERT INTO services (service_id, sirvice_name, price) VALUES (%s, %s, %s)" % (service_id, '\'' + service_name + '\'', price)
            self.execute_query(query)
        except Exception as e:
            self.conn.rollback()
            print(f"Error adding service: {e}")

    @timeit
    def update_service(self, service_id, field, new_value):
        """Оновлення даних сервісу."""
        try:
            if field == 'sirvice_name':
                new_value = "'" + new_value + "'"
            query = "UPDATE services SET %s = %s WHERE service_id = %s" % (field, new_value, service_id)
            self.execute_query(query)
        except Exception as e:
            print(f"Error updating service: {e}")

    @timeit
    def generate_services(self, num_services):
        """Генерація випадкових сервісів із унікальними назвами через SQL."""
        c = self.conn.cursor()
        try:
            # Отримуємо максимальний service_id для унікальності
            query = "SELECT COALESCE(MAX(service_id), 0) FROM services"
            c.execute(query)
            max_service_id = c.fetchone()[0]

            # Генерація даних через SQL
            query = f"""
                WITH generated_services AS (
                    SELECT 
                        (ROW_NUMBER() OVER ()) + {max_service_id} AS service_id,
                        'Service_' || ((ROW_NUMBER() OVER ()) + {max_service_id}) AS sirvice_name,
                        FLOOR(RANDOM() * (500 - 50 + 1) + 50)::INTEGER AS price
                    FROM generate_series(1, {num_services})
                )
                INSERT INTO services (service_id, sirvice_name, price)
                SELECT service_id, sirvice_name, price
                FROM generated_services;
            """
            c.execute(query)
            self.conn.commit()
            print(f"{num_services} services generated successfully.")
        except Exception as e:
            self.conn.rollback()
            print(f"Error generating services: {e}")
        finally:
            c.close()


    @timeit
    def add_room(self, room_id, room_number, room_type_id, user_id, check_in_date, check_out_date):
        """Додавання нового номера до таблиці rooms."""
        c = self.conn.cursor()
        try:
            # Якщо user_id порожнє, то ставимо його як NULL
            if user_id == "":
                user_id = None

            # Формуємо SQL запит
            query = """
                INSERT INTO rooms (room_id, room_number, room_type_id, user_id, check_in_date, check_out_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            # Виконання запиту з параметрами
            c.execute(query, (room_id, room_number, room_type_id, user_id, check_in_date, check_out_date))
            self.conn.commit()
            print(f"Room {room_id} added successfully.")
        except Exception as e:
            self.conn.rollback()
            print(f"Error adding room: {e}")
        finally:
            c.close()


    @timeit
    def update_room(self, room_id, field, new_value):
        """Оновлення запису в таблиці rooms."""
        query = f"UPDATE rooms SET {field} = {new_value} WHERE room_id = {room_id}"
        try:
            self.execute_query(query)
            print(f"Room {room_id} updated successfully.")
        except Exception as e:
            print(f"Error updating room: {e}")

    @timeit
    def generate_rooms(self, num_rooms):
        """Генерація нових кімнат з випадковими користувачами та датами, з перевіркою максимальних room_id, room_type_id та правильним вибором user_id"""
        try:
            # Отримуємо максимальний room_id з таблиці для уникнення дублювання
            query_max_room_id = "SELECT MAX(room_id) FROM rooms"
            max_room_id = self.fetch_query(query_max_room_id)
            max_room_id = max_room_id[0][0] if max_room_id[0][0] else 0  # Якщо кімнат ще немає, починаємо з 0
            
            # Отримуємо максимальний user_id з таблиці для уникнення дублювання
            query_max_user_id = "SELECT MAX(user_id) FROM users"
            max_user_id = self.fetch_query(query_max_user_id)
            max_user_id = max_user_id[0][0] if max_user_id[0][0] else 0  # Якщо користувачів ще немає, починаємо з 0
            
            # Отримуємо максимальний room_type_id з таблиці room_type для уникнення дублювання
            query_max_room_type_id = "SELECT MAX(room_type_id) FROM room_type"
            max_room_type_id = self.fetch_query(query_max_room_type_id)
            max_room_type_id = max_room_type_id[0][0] if max_room_type_id[0][0] else 0  # Якщо типів кімнат ще немає, починаємо з 0

            # Перевіряємо чи є хоча б один room_type_id в таблиці room_type
            query_check_room_types = "SELECT COUNT(*) FROM room_type"
            room_type_count = self.fetch_query(query_check_room_types)
            if room_type_count[0][0] == 0:
                print("Error: No room types found in the database.")
                return
            
            # Генерація кімнат з випадковими даними
            query = f"""
                WITH generated_rooms AS (
                    SELECT 
                        (ROW_NUMBER() OVER () + {max_room_id}) AS room_id,  -- Починаємо з наступного доступного room_id
                        (FLOOR(RANDOM() * 100) + 1) AS room_number,  -- Випадковий номер кімнати
                        (FLOOR(RANDOM() * {max_room_type_id}) + 1) AS room_type_id,  -- Випадковий існуючий room_type_id
                        (FLOOR(RANDOM() * {max_user_id}) + 1) AS user_id,  -- Випадковий user_id
                        NOW() - (INTERVAL '1 day' * FLOOR(RANDOM() * 100)) + (INTERVAL '1 hour' * FLOOR(RANDOM() * 24)) AS check_in_date,  -- Випадкова дата та час заїзду
                        NOW() + (INTERVAL '1 day' * FLOOR(RANDOM() * 30)) + (INTERVAL '1 hour' * FLOOR(RANDOM() * 24)) AS check_out_date  -- Випадкова дата та час виїзду
                    FROM generate_series(1, {num_rooms})
                )
                INSERT INTO rooms (room_id, room_number, room_type_id, user_id, check_in_date, check_out_date)
                SELECT room_id, room_number, room_type_id, user_id, check_in_date, check_out_date
                FROM generated_rooms
                WHERE room_type_id IS NOT NULL
            """
            
            self.execute_query(query)
            print(f"{num_rooms} rooms generated successfully.")

        except Exception as e:
            print(f"Error generating rooms: {e}")


    @timeit
    def add_room_type(self, room_type_id, type_name, price):
        """Додавання нового типу кімнати до таблиці room_type."""
        query = f"""
            INSERT INTO room_type (room_type_id, type_name, price)
            VALUES ({room_type_id}, '{type_name}', {price})
        """

        try:
            self.execute_query(query)
            print(f"Room type {room_type_id} added successfully.")
        except Exception as e:
            print(f"Error adding room type: {e}")

    @timeit
    def update_room_type(self, room_type_id, field, new_value):
        """Оновлення даних типу кімнати в таблиці room_type."""
        query = f"UPDATE room_type SET {field} = '{new_value}' WHERE room_type_id = {room_type_id}"
        try:
            self.execute_query(query)
            print(f"Room type {room_type_id} updated successfully.")
        except Exception as e:
            print(f"Error updating room type: {e}")


    @timeit
    def generate_room_types(self, num_room_types):
        """Генерація випадкових записів у таблиці room_type."""
        query = f"""
            WITH generated_room_types AS (
                SELECT 
                    (ROW_NUMBER() OVER ()) + COALESCE((SELECT MAX(room_type_id) FROM room_type), 0) AS room_type_id,
                    'Type_' || (ROW_NUMBER() OVER ()) AS type_name,
                    FLOOR(RANDOM() * 1000) + 100 AS price  -- випадкова ціна в діапазоні 100-1099
                FROM generate_series(1, {num_room_types})
            )
            INSERT INTO room_type (room_type_id, type_name, price)
            SELECT room_type_id, type_name, price
            FROM generated_room_types
        """
        try:
            self.execute_query(query)
            print(f"{num_room_types} room types generated successfully.")
        except Exception as e:
            self.conn.rollback()
            print(f"Error generating room types: {e}")

    @timeit
    def add_ordering_service(self, user_id, service_id, date):
        """Додавання нового запису до таблиці ordering_services."""
        try:
            query = f"""
                INSERT INTO ordering_services (user_id, service_id, data)
                VALUES ({user_id}, {service_id}, '{date}')
            """
            self.execute_query(query)
        except Exception as e:
            self.conn.rollback()
            print(f"Error adding ordering service: {e}")

    @timeit
    def update_ordering_service(self, user_id, service_id, field, new_value, date):
        """Оновлення запису в таблиці ordering_services."""
        try:
            query = f"""
                UPDATE ordering_services
                SET {field} = '{new_value}'
                WHERE user_id = {user_id} AND service_id = {service_id} AND data = '{date}'
            """
            self.execute_query(query)
        except Exception as e:
            self.conn.rollback()
            print(f"Error updating ordering service: {e}")

    @timeit
    def generate_ordering_services(self, num_records):
        """Генерація випадкових записів для таблиці ordering_services."""
        try:
            # Отримання максимального user_id і service_id для забезпечення коректних значень.
            max_user_id = self.fetch_query("SELECT MAX(user_id) FROM users")[0][0] or 0
            max_service_id = self.fetch_query("SELECT MAX(service_id) FROM services")[0][0] or 0

            if max_user_id == 0 or max_service_id == 0:
                raise Exception("Users or services table is empty. Unable to generate ordering services.")

            # Генерація SQL запиту для вставки даних.
            query = f"""
                WITH generated_ordering_services AS (
                    SELECT
                        FLOOR(RANDOM() * {max_user_id} + 1)::int AS user_id,
                        FLOOR(RANDOM() * {max_service_id} + 1)::int AS service_id,
                        NOW() - (INTERVAL '1 day' * FLOOR(RANDOM() * 30)) AS data
                    FROM generate_series(1, {num_records})
                )
                INSERT INTO ordering_services (user_id, service_id, data)
                SELECT user_id, service_id, data
                FROM generated_ordering_services
            """
            self.execute_query(query)
            print(f"{num_records} ordering services generated successfully.")
        except Exception as e:
            self.conn.rollback()
            print(f"Error generating ordering services: {e}")


    @timeit
    def delete_data(self, table_name, option, **kwargs):
        """Функція для видалення даних з таблиці за значенням поля або діапазоном ID"""
        try:
            c = self.conn.cursor()

            # Якщо вибрано видалення за значенням поля
            if option == "field":
                field = kwargs.get("field")
                value = kwargs.get("value")
                c.execute(f"DELETE FROM {table_name} WHERE {field} = %s", (value,))
            
            # Якщо вибрано видалення за діапазоном ID
            elif option == "range":
                field_name = kwargs.get("field_name")  # Поле для діапазону
                id_start = kwargs.get("id_start")
                id_end = kwargs.get("id_end")
                c.execute(f'DELETE FROM "{table_name}" WHERE "{field_name}" BETWEEN %s AND %s', (id_start, id_end))
            
            self.conn.commit()
            rows_updated = c.rowcount
            print(f"\n{rows_updated} rows deleted.")
        
        except Exception as e:
            print(f"An error occurred while deleting data: {e}")
            self.conn.rollback()
        
        finally:
            c.close()

    def fetch_query(self, query):
        """Виконує SELECT запит і повертає результат"""
        try:
            c = self.conn.cursor()
            c.execute(query)
            result = c.fetchall()
            c.close()
            return result
        except Exception as e:
            print(f"Error fetching data: {str(e)}")
            return []

    def execute_query(self, query):
        """Виконує SQL-запит на вставку або оновлення даних"""
        try:
            c = self.conn.cursor()
            c.execute(query)
            self.conn.commit()
            c.close()
        except Exception as e:
            print(f"Error executing query: {str(e)}")
            self.conn.rollback()