import psycopg2
import datetime


class DBHandler:
    def __init__(self, host: str, db_name='ESP Controller', user='airflow', password='airflow') -> None:
        # Сформируем строку информации для подключения к СУБД
        self.conn_string = f"dbname='{db_name}' user='{user}' host='{host}' password='{password}'"

    def recreate_users(self) -> None:
        """
        Пересоздание таблицы users (dev only)
        :return:
        """

        # Подключимся к нужной таблице СУБД 
        # согласно инструкциям строки conn_string
        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()

        # Удалим старую базу
        cur.execute("DROP TABLE IF EXISTS controller.users;")

        # Создадим новую БД
        cur.execute("""
            CREATE TABLE IF NOT EXISTS controller.users
            (
                id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 ) UNIQUE,
                username text NOT NULL UNIQUE,
                "rfidUID" integer NOT NULL UNIQUE,
                code text NOT NULL,
                "permittedCheckpoints" text NOT NULL,
                PRIMARY KEY (id)
            );
            
            ALTER TABLE controller.users
                OWNER to airflow;
        """)

        conn.commit()
        conn.close()

    def recreate_log(self) -> None:
        """
        Пересоздание таблицы log (dev only)
        :return:
        """

        # Подключимся к нужной таблице СУБД
        # согласно инструкциям строки conn_string
        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()

        # Удалим старую базу
        cur.execute("DROP TABLE IF EXISTS controller.log;")

        # Создадим новую БД
        cur.execute("""
            CREATE TABLE IF NOT EXISTS controller.log
            (
                id integer NOT NULL GENERATED ALWAYS AS IDENTITY ( INCREMENT 1 START 1 ),
                "rfidUID" integer NOT NULL,
                date text NOT NULL,
                "checkpointCode" text NOT NULL,
                "isSuccessful" boolean NOT NULL,
                PRIMARY KEY (id)
            );

            ALTER TABLE controller.log
                OWNER to airflow;
                """)

        conn.commit()
        conn.close()

    def create_new_user(self, username: str, rfid_uid: int, secret_code: str, permitted_checkpoints: [str]) -> bool:
        checkpoints = ";".join(permitted_checkpoints)

        req = f"""
                INSERT INTO controller.users 
                    (username, "rfidUID", code, "permittedCheckpoints")
                VALUES 
                    ('{username}', {rfid_uid}, '{secret_code}', '{checkpoints}');
        """

        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()

        try:
            cur.execute(req)

            conn.commit()
        except psycopg2.errors.UniqueViolation:
            return False
        finally:
            conn.close()

        return True

    def modify_user_by_id(self, username: str, rfid_uid: int, secret_code: str, permitted_checkpoints: [str],
                          db_id: int) -> None:
        checkpoints = ";".join(permitted_checkpoints)
        req = f"""
                        UPDATE controller.users 
                        SET
                            username='{username}', "rfidUID"={rfid_uid}, code='{secret_code}', "permittedCheckpoints"='{checkpoints}'
                        WHERE
                            id={db_id};
                """

        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()

        cur.execute(req)
        conn.commit()

        conn.close()

    def find_user_by_rfid(self, rfid_uid: int) -> []:
        req = f"""
            SELECT 
                id, username, code, "permittedCheckpoints" 
            FROM 
                controller.users 
            WHERE
                "rfidUID" = {rfid_uid};
        """

        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()

        cur.execute(req)
        data = cur.fetchone()
        conn.close()
        if data:
            return list(data)
        return []

    def create_log_record(self, rfid_uid: int, checkpoint_code: str, is_successful: bool) -> None:
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        req = f"""
                INSERT INTO controller.log 
                    ("rfidUID", date, "checkpointCode", "isSuccessful")
                VALUES 
                    ({rfid_uid}, '{date}', '{checkpoint_code}', {is_successful});
        """

        conn = psycopg2.connect(self.conn_string)
        cur = conn.cursor()

        cur.execute(req)
        conn.commit()

        conn.close()
        pass

    pass


if __name__ == "__main__":
    test_host = '192.168.1.81'
    handler = DBHandler(test_host)

    # Пересоздадим (очистим) таблицы
    handler.recreate_users()
    handler.recreate_log()

    # 1. Создадим пользователей
    is_created = handler.create_new_user("Вася",
                                         123456,
                                         '666',
                                         ['A1', 'B2', 'C141'])

    print("(1)\tНовый пользователь был:", "создан." if is_created else "не создан.")
    is_created = handler.create_new_user("Олег",
                                         123457,
                                         '666',
                                         ['A1', 'B2', 'C141'])

    print("(1)\tНовый пользователь был:", "создан." if is_created else "не создан.")

    # 2. Проверим, что нельзя создать пользователя с такой же картой
    is_created = handler.create_new_user("Петя",
                                         123456,
                                         '0000',
                                         ['A1'])

    print("(2)\tНовый пользователь был:", "создан." if is_created else "не создан.")

    # 3. Попробуем получить информацию о существующем пользователе из СУБД 
    # по коду RFID-метки
    print("(3)\tСуществующий юзер:", handler.find_user_by_rfid(123456))

    # 4. Попробуем получить информацию о несуществующем пользователе из СУБД 
    # по коду RFID-метки
    print("(4)\tНесуществующий юзер:", handler.find_user_by_rfid(125))

    # 5. Обновим данные пользователя с ID 1
    handler.modify_user_by_id("Не Вася",
                              654321,
                              '123',
                              ['A1', 'B2', 'C141'],
                              1
                              )

    # 6. Зарегистрируем попытки прохода через Считыватели
    handler.create_log_record(123456,
                              'C1',
                              True)

    handler.create_log_record(10568,
                              'main',
                              False)
