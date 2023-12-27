# импорт модулей
import telebot
from telebot import types
from db import Database
from datetime import datetime
import re

# создание объекта базы данных
db = Database('data.db')

# настройка бота
adminID = 818878003
bot_token = '6454888084:AAGnMl1wWe02LFdokLu3LDnC8GJ4f-BFO38'

# создание экземпляра бота
bot = telebot.TeleBot(bot_token)

# инициализация строковых переменных
mode = ""
date = ""
model = ""

# создание клавиатуры для стартового экрана
keyboard_startup = types.ReplyKeyboardMarkup(resize_keyboard=True)
button1 = types.KeyboardButton("Мои записи")
button2 = types.KeyboardButton("Записаться")
button_delete = types.KeyboardButton("Удалить мою запись")
keyboard_startup.add(button1, button2, button_delete)

# создание клавиатуры администратора
keyboard_admin = types.ReplyKeyboardMarkup(resize_keyboard=True)
button1 = types.KeyboardButton("Мои записи")
button2 = types.KeyboardButton("Записаться")
button3 = types.KeyboardButton("Посмотреть все записи")
button4 = types.KeyboardButton("Удалить все записи")
keyboard_admin.add(button1, button2, button3, button4)

# создание клавиатуры для выбора услуги
keyboard_mode = types.ReplyKeyboardMarkup(resize_keyboard=True)
button1 = types.KeyboardButton("Тех. обслуживание")
button2 = types.KeyboardButton("Ремонт")
button3 = types.KeyboardButton("Диагностика")
button4 = types.KeyboardButton("Отмена")
keyboard_mode.add(button1, button2, button3, button4)

# клавиатура для отмены действия
keyboard_cansel = types.ReplyKeyboardMarkup(resize_keyboard=True)
button1 = types.KeyboardButton("Отмена")
keyboard_cansel.add(button1)


def handle_delete_order(message, id):
    # функция удаления записи
    db.delete_order(id)
    bot.send_message(message.from_user.id, "Ваши записи удалены.")


def parse_date(date_string):
    # функция разбора даты
    return datetime.strptime(date_string, "%d.%m.%Y")


@bot.message_handler(func=lambda message: True)
def start(message, flag=0):
    # функция, обрабатывающая входящие сообщения от пользователей
    if message.text == "/start":
        if message.from_user.id == adminID:

            if flag == 0:
                bot.send_message(message.from_user.id, "Привет, менеджер!\nВыбери действие",
                                 reply_markup=keyboard_admin)
            else:
                bot.send_message(message.from_user.id, "Выбери действие",
                                 reply_markup=keyboard_admin)
        else:
            if flag == 0:
                bot.send_message(message.from_user.id, "Приветствуем Вас в нашем сервисе!\n"
                                                       "Выберите действие", reply_markup=keyboard_startup)
            else:
                bot.send_message(message.from_user.id, "Выберите действие", reply_markup=keyboard_startup)
    elif message.text == "Мои записи":
        order_info = db.get_order_info(message.from_user.id)
        if not order_info:
            bot.send_message(message.from_user.id, "Записи не обнаружены")
        else:
            for info in order_info:
                date_, model_, mode_, phone_, username_ = info
                bot.send_message(message.from_user.id, f"Услуга: {mode_}\n\n"
                                                       f"Модель: {model_}\n\n"
                                                       f"Дата: {date_}\n\n"
                                                       f"Номер телефона: {phone_}")
    elif message.text == "Записаться":
        bot.send_message(message.from_user.id, "Выберите услугу", reply_markup=keyboard_mode)
        bot.register_next_step_handler(message, make_order_mode)

    elif message.text == "Удалить мою запись":
        handle_delete_order(message, message.from_user.id)

    elif message.text == "Посмотреть все записи":
        if message.from_user.id == adminID:
            order_info = db.get_all_orders()
            if not order_info:
                bot.send_message(message.from_user.id, "Записи не обнаружены")
            else:
                informs = []
                for info in order_info:
                    user_, date_, model_, mode_, phone_, username_ = info
                    informs.append([date_, model_, mode_, phone_, username_])
                sorted_informs = sorted(informs, key=lambda x: parse_date(x[0]))

                for info in sorted_informs:
                    bot.send_message(message.from_user.id, f"Услуга: {info[2]}\n\n"
                                                           f"Модель: {info[1]}\n\n"
                                                           f"Дата: {info[0]}\n\n"
                                                           f"Номер телефона: {info[3]}\n\n"
                                                           f"Пользователь: @{info[-1]}")
    elif message.text == "Удалить все записи":
        if message.from_user.id == adminID:
            db.delete_all_orders()
            bot.send_message(message.from_user.id, "Все записи удалены")


"""
Следующие четыре функции (make_order_mode, make_order_date, make_order_model, make_order_phone)
последовательно запрашивают у пользователя информацию о записи, проверяет введенные данные и сохраняют их
"""


def make_order_mode(message):
    global mode
    if message.text == "Отмена" or message.text == "/start":
        message.text = "/start"
        start(message, 1)
        return
    elif message.text == "Тех. обслуживание":
        mode = message.text
    elif message.text == "Ремонт":
        mode = message.text
    elif message.text == "Диагностика":
        mode = message.text
    else:
        bot.send_message(message.from_user.id, "Услуга не найдена")
        message.text = "/start"
        start(message, 1)
        return
    bot.send_message(message.from_user.id, "Укажите дату (формат ДД.ММ.ГГГГ)", reply_markup=keyboard_cansel)
    bot.register_next_step_handler(message, make_order_date)


def make_order_date(message):
    if message.text == "Отмена" or message.text == "/start":
        message.text = "/start"
        start(message, 1)
    else:
        if re.match(r"^\d{2}\.\d{2}\.\d{4}$", message.text):
            parsed_date = datetime.strptime(message.text, "%d.%m.%Y")
            global date
            date = parsed_date.strftime("%d.%m.%Y")

            bot.send_message(message.from_user.id, "Укажите модель квадрацикла")
            bot.register_next_step_handler(message, make_order_model)
        else:
            # Если формат даты неправильный, запрашиваем ввод заново
            bot.send_message(message.from_user.id, "Пожалуйста, введите дату в формате ДД.ММ.ГГГГ.",
                             reply_markup=keyboard_mode)  # Используйте подходящую клавиатуру
            bot.register_next_step_handler(message, make_order_date)


def make_order_model(message):
    global model
    if message.text == "Отмена" or message.text == "/start":
        message.text = "/start"
        start(message, 1)
    else:
        model = message.text
        bot.send_message(message.from_user.id, "Укажите номер телефона (формат +7XXXXXXXXXX или 8XXXXXXXXXX)",
                         reply_markup=keyboard_cansel)
        bot.register_next_step_handler(message, make_order_phone)


def make_order_phone(message):
    global date, mode, model

    phone_regex = r"^\+?7\d{10}$|^8\d{10}$"

    if re.match(phone_regex, message.text):
        phone = message.text
        db.add_list(message.from_user.id, mode, date, phone, model, message.from_user.username)
        bot.send_message(message.from_user.id, "Запись сделана")
        bot.send_message(adminID, "Обнаружена новая запись")

        message.text = "/start"
        start(message, 1)
    elif message.text == "Отмена" or message.text == "/start":
        message.text = "/start"
        start(message, 1)
    else:
        bot.send_message(message.from_user.id, "Пожалуйста, введите номер телефона в правильном формате "
                                               "(+7XXXXXXXXXX или 8XXXXXXXXXX).")
        bot.register_next_step_handler(message, make_order_phone)


# точка входа в программу
if __name__ == "__main__":
    bot.polling(none_stop=True)
