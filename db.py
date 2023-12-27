import sqlite3

conn = sqlite3.connect('data.db')

create_table_query = '''CREATE TABLE IF NOT EXISTS list (
                            user_id INTEGER NOT NULL,
                            mode TEXT NOT NULL,
                            date TEXT NOT NULL,
                            phone TEXT NOT NULL,
                            model TEXT NOT NULL,
                            username TEXT);'''

conn.execute(create_table_query)

conn.close()


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def add_list(self, user_id, mode, date, phone, model, username):
        with self.connection:
            return self.cursor.execute("INSERT INTO 'list' ('user_id', 'mode', 'date', 'phone', 'model', 'username') VALUES (?, ?, ?, ?, ?, ?)",
                                       (user_id, mode, date, phone, model, username))

    def get_order_info(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT date, model, mode, phone, username FROM list WHERE user_id = ?",
                                         (user_id,)).fetchall()
            return result

    def get_all_orders(self):
        with self.connection:
            result = self.cursor.execute("SELECT user_id, date, model, mode, phone, username FROM list").fetchall()
            return result

    def delete_all_orders(self):
        with self.connection:
            self.cursor.execute("DELETE FROM list")

    def delete_order(self, user_id):
        """
        Удаляет запись пользователя по его ID.

        :param user_id: Идентификатор пользователя, запись которого нужно удалить.
        """
        # SQL-запрос для удаления записи
        query = "DELETE FROM list WHERE user_id = ?"

        # Выполнение запроса
        self.cursor.execute(query, (user_id,))
        self.connection.commit()
