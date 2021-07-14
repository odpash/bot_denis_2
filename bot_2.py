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
fl_end = False
m_id = 0


@bot.callback_query_handler(func=lambda c: 'lang' in c.data)  # Первый шаг настроек (вывод параметров)
def lang_stage(callback_query: types.CallbackQuery):
    global m_id
    global last_message
    last_message = callback_query.data.replace('lang_', '')
    callback_query.data = callback_query.data.replace('lang_', '')
    f = parse_txt_file('config_bot_2.txt')
    if callback_query.data != f['lang'][0]:
        idx = get_lang(callback_query.message, f)
        try:
            m_id = bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=m_id, text=f['only_eng'][idx]).message_id
        except:
            m_id = bot.send_message(callback_query.message.chat.id, f['only_eng'][idx]).message_id
        m_id = step_start(f, callback_query.message, bot, m_id)
        return
    m_id = step_btn_pay(f, callback_query.message, f['lang'].index(last_message), bot, m_id)  # step_2







@bot.callback_query_handler(func=lambda c: 'yes_btn_pressed' in c.data)  # Первый шаг настроек (вывод параметров)
def yes_btn_pressed(callback_query: types.CallbackQuery):
    global last_message, m_id
    last_message = callback_query
    m_id = yes_btn_pressed_func(last_message, bot, m_id)


@bot.callback_query_handler(func=lambda c: 'pay_btn_pressed_' in c.data)  # Первый шаг настроек (вывод параметров)
def pay_btn_pressed(callback_query: types.CallbackQuery):
    print('yeees')
    global last_message, m_id
    last_message = callback_query
    m_id = pay_btn_pressed_func(last_message, bot, m_id)


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

@bot.callback_query_handler(func=lambda c: 'instruction_cb' in c.data or 'settings_cb' in c.data or 'support_cb')  # Первый шаг настроек (вывод параметров)
def service_stage(callback_query: types.CallbackQuery):
    global m_id
    f = parse_txt_file('config_bot_2.txt')  # Подгрузка конфиг файла
    callback_query.data = callback_query.data.replace('instruction_cb', '').replace('settings_cb', '').replace('support_cb', '')
    m_id = step_service(f, callback_query.data, f['support'], f['settings'], f['instruction'], bot, m_id, callback_query.message.chat.id)  # Методы из нижней сточки меню


@bot.message_handler()
def initialize(message):
    global fl_end, m_id
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
        m_id = step_start(f, message, bot, m_id)  # Описание: бот просил выбрать язык.
        last_message = message.text
    elif message.text in f['pay']:
        step_btn_pay(f, message, f['pay'].index(message.text), bot)  # step_2
    elif message.text in f['lang']:
        last_message = message.text
        if fl:  # Если мы изменяем параметр language у пользователя
            settings_change_language_final_stage(message, f, bot)  # Изменяет параметр в бд
            fl = False  # Оповещает про изменение параметра в бд
        if message.text != f['lang'][0]:
            idx = get_lang(message, f)
            bot.send_message(message.chat.id, f['only_eng'][idx])
            step_start(f, message, bot)
        else:
            step_btn_pay(f, message, f['lang'].index(message.text), bot)  # step_2

    elif fl_end:
        fl_end = False
        change_user_param_in_db(message.from_user.id, message.text, 'last_wallet')
        lang, hash_info, trans, wallet = read_records_from_db(message.from_user.id)
        if trans == '12345' and wallet == '54321':
            payment_success(f, message, bot)
        else:
            bot.send_message(message.chat.id, f['error_trans'][get_lang(message, f)])
            markup = types.InlineKeyboardMarkup()
            idx = get_lang(message, f)
            markup.row(
                types.InlineKeyboardButton(f[f'support'][idx], callback_data=f"support_cb{f[f'support'][idx]}"),
                types.InlineKeyboardButton(f[f'settings'][idx],
                                           callback_data=f"settings_cb{f[f'settings'][idx]}"),
                types.InlineKeyboardButton(f[f'instruction'][idx],
                                           callback_data=f"instruction_cb{f[f'instruction'][idx]}"))
            bot.send_message(message.chat.id, f['write_transaction'][get_lang(message, f)], reply_markup=[markup])
    elif 'yes_btn_pressed' in callback_data:  # Проверка транзакции
        fl_end = True
        change_user_param_in_db(message.from_user.id, message.text, 'last_trans')
        idx = get_lang(message, f)
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton(f[f'support'][idx], callback_data=f"support_cb{f[f'support'][idx]}"),
            types.InlineKeyboardButton(f[f'settings'][idx], callback_data=f"settings_cb{f[f'settings'][idx]}"),
            types.InlineKeyboardButton(f[f'instruction'][idx],
                                       callback_data=f"instruction_cb{f[f'instruction'][idx]}"))
        bot.send_message(message.from_user.id, f["wallet_info"][idx], reply_markup=[markup])
        #payment_success(f, message, bot)
        return

    else:
        if fl:  # Если меняем параметр токен у пользователя
            change_user_param_in_db(str(message.from_user.id), message.text, 'hash')
            fl = False
            settings_change_token_final_stage(message, f, bot)
        else:  # Обработка ошибок
            error_messages(f, message, bot, last_message)


bot.polling()
