from aiogram import types
import telebot
from database_editing import change_user_param_in_db, read_records_from_db, registration_user_in_db, add_record_to_db
from database_editing import parse_txt_file, get_lang
from steps import step_service, step_start, step_btn_pay, payment_success, error_messages
from steps import settings_change_language_final_stage, settings_change_token_final_stage
from steps import pay_btn_pressed_func, yes_btn_pressed_func, settings_step_1_func

token = '1712170001:AAE3r4S9o5R7jtI092xaJSMai_TcY3fb4OY'
bot = telebot.TeleBot(token)
last_message = ''
fl = False


@bot.callback_query_handler(func=lambda c: 'yes_btn_pressed' in c.data)  # Первый шаг настроек (вывод параметров)
def yes_btn_pressed(callback_query: types.CallbackQuery):
    global last_message
    last_message = callback_query
    yes_btn_pressed_func(last_message, bot)


@bot.callback_query_handler(func=lambda c: 'pay_btn_pressed_' in c.data)  # Первый шаг настроек (вывод параметров)
def pay_btn_pressed(callback_query: types.CallbackQuery):
    global last_message
    last_message = callback_query
    pay_btn_pressed_func(last_message, bot)


@bot.callback_query_handler(func=lambda c: 'step1' in c.data)  # Первый шаг настроек (вывод параметров)
def settings_step1_param_and_button(callback_query: types.CallbackQuery):
    global last_message
    last_message = callback_query
    settings_step_1_func(last_message, bot)


@bot.callback_query_handler(func=lambda c: 'step2' in c.data)  # Второй шаг настроек (Это кнопка изменить)
def settings_step2_param_and_button(callback_query: types.CallbackQuery):
    global fl, last_message
    user_cmd = callback_query.data
    fl = True
    f = parse_txt_file('config_bot_2.txt')
    if 'hash' in user_cmd:
        bot.send_message(callback_query.from_user.id, f['change_hash_text'][int(user_cmd[-1])])
    else:
        step_start(f, callback_query.message, bot)
    last_message = callback_query


@bot.message_handler()
def initialize(message):
    global fl, last_message
    print(message.text, message.from_user.id)
    try:
        callback_data = last_message.data
    except Exception:
        callback_data = ''
    f = parse_txt_file('config_bot_2.txt')  # Подгрузка конфиг файла
    if message.text in f['support'] or message.text in f['settings'] or message.text in f['instruction']:  # Сервис
        step_service(f, message, f['support'], f['settings'], f['instruction'], bot)  # Методы из нижней сточки меню
        last_message = message.text
    elif message.text == '/start':  # 1) Пользователь написал /start
        step_start(f, message, bot)  # Описание: бот просил выбрать язык.
        last_message = message.text
    elif message.text in f['lang']:
        last_message = message.text
        if fl:  # Если мы изменяем параметр language у пользователя
            settings_change_language_final_stage(message, f, bot)  # Изменяет параметр в бд
            fl = False  # Оповещает про изменение параметра в бд
        step_btn_pay(f, message, f['lang'].index(message.text), bot)  # step_2

    elif 'yes_btn_pressed' in callback_data:  # Проверка транзакции
        if message.text == '12345':
            payment_success(f, message, bot)
        else:
            bot.send_message(message.chat.id, f['error_trans'][get_lang(message, f)])
            bot.send_message(message.chat.id, f['write_transaction'][get_lang(message, f)])
    else:
        if fl:  # Если меняем параметр токен у пользователя
            change_user_param_in_db(str(message.from_user.id), message.text, 'hash')
            fl = False
            settings_change_token_final_stage(message, f, bot)
        else:  # Обработка ошибок
            error_messages(f, message, bot, last_message)


bot.polling()
