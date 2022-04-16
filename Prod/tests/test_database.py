# IP для подключения к БД
TEST_HOST = '192.168.1.81'

import logging
import pytest
import os
import sys
import inspect

# Импортируем файл обработчика запросов БД из родительского каталога (на 1 уровень вверх)
# Устанавливаем путь на родительский каталог
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from db_handler import DBHandler

# Настраиваем логирование
logger = logging.getLogger(__name__)


class TestBooks:
    def setup(self):
        logger.info("basic setup into class")

    def teardown(self):
        logger.info("basic teardown into class")

    def setup_class(cls):
        logger.info("class setup")

    def teardown_class(cls):
        logger.info("class teardown")

    def setup_method(self, method):
        logger.info("method setup")

    def teardown_method(self, method):
        logger.info("method teardown")

    @pytest.fixture(autouse=True)
    def prepare_handler(self):
        logger.info(f"prepare handler. Test host: {TEST_HOST}")
        self.handler = DBHandler(TEST_HOST)
        yield

    def test_table_clear(self, prepare_handler):
        logger.info("table recreation")
        # Очищаем таблицы
        assert self.handler.recreate_users() is None
        assert self.handler.recreate_log() is None

    def test_create_users(self, prepare_handler):
        logger.info("user creation")
        # Создаем 2-х пользователей (должно быть успешно)
        user_a = self.handler.create_new_user(username="Вася",
                                              rfid_uid=123456,
                                              secret_code='666',
                                              permitted_checkpoints=['A1', 'B2', 'C141'])
        assert user_a

        user_b = self.handler.create_new_user(username="Олег",
                                              rfid_uid=123457,
                                              secret_code='666',
                                              permitted_checkpoints=['A1', 'B2', 'C121'])
        assert user_b

        # Пытаемся создать пользователя с таким же id (должен вернуться False)
        user_c = self.handler.create_new_user(username="Олег",
                                              rfid_uid=123457,
                                              secret_code='666',
                                              permitted_checkpoints=['A1', 'B2', 'C121'])
        assert not user_c

    def test_find_user(self, prepare_handler):
        existed_user = self.handler.find_user_by_rfid(123456)
        assert existed_user
        logger.info(f"existed user: {existed_user}")

        not_existed_user = self.handler.find_user_by_rfid(170422)
        assert not not_existed_user
        logger.info(f"not existed user: {not_existed_user}")

    def test_modify_user(self, prepare_handler):
        logger.info("user modification")
        result_a = self.handler.modify_user_by_id(
            username="Не Вася",
            rfid_uid=654321,
            secret_code='123',
            permitted_checkpoints=['A1', 'B2', 'C141'],
            db_id=1)
        assert result_a is None

        result_b = self.handler.modify_user_by_id(
            username="Не Петя",
            rfid_uid=654321,
            secret_code='123',
            permitted_checkpoints=['A1', 'B2', 'C141'],
            db_id=152)
        assert result_b is None
