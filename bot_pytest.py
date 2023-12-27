import pytest
from unittest.mock import Mock, patch
import main
from main import handle_delete_order, parse_date, start, make_order_mode, make_order_date, make_order_model, make_order_phone
from datetime import datetime

# Мокинг объектов bot и Database
@pytest.fixture(autouse=True)
def mock_bot():
    with patch('main.bot') as mock_bot:
        yield mock_bot

@pytest.fixture(autouse=True)
def mock_db():
    with patch('main.db') as mock_db:
        yield mock_db

# Тест для функции handle_delete_order
def test_handle_delete_order(mock_bot, mock_db):
    message = Mock()
    message.from_user.id = 123
    handle_delete_order(message, 123)
    mock_db.delete_order.assert_called_with(123)
    mock_bot.send_message.assert_called_with(123, "Ваши записи удалены.")

# Тест для функции parse_date
def test_parse_date():
    assert parse_date("01.01.2023") == datetime(2023, 1, 1)

# Тесты для функции start

def test_start_admin(mock_bot):
    message = Mock()
    message.text = "/start"
    message.from_user.id = 818878003  # Админ
    start(message)
    mock_bot.send_message.assert_called_with(818878003, "Привет, менеджер!\nВыбери действие", reply_markup=main.keyboard_admin)

# Дополните тестами для make_order_mode, make_order_date, make_order_model, make_order_phone
# Эти тесты будут аналогичны по структуре