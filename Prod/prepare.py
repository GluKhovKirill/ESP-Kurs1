HOST = '172.18.0.2'
from db_handler import DBHandler


handler = DBHandler(HOST)
handler.recreate_log()
handler.recreate_users()

handler.create_new_user(username="Вася",
                        rfid_uid=123456,
                        secret_code='666',
                        permitted_checkpoints=[
                            'A1',
                            'B2',
                            'C141'
                        ])
