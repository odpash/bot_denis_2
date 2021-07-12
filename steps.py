from aiogram import types
from database_editing import registration_user_in_db, add_record_to_db, get_lang
from database_editing import parse_txt_file, read_records_from_db


def settings_step_1_func(callback_query, bot):
    f = parse_txt_file('config_bot_2.txt')
    db_lang, db_hash = read_records_from_db(callback_query.from_user.id)
    user_cmd = callback_query.data
    lang = user_cmd[-1]
    if 'hash' in user_cmd:
        command = 'hash'
        ans = db_hash
    else:
        ans = db_lang
        command = 'lang'
    lang = int(lang)
    answer = f'{f[f"settings_step1_text"][lang]} {f[f"{command}"][lang]}: {ans}'
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f[f'change_btn'][lang], callback_data=f'settings_{command}_step2_{lang}'))
    bot.answer_callback_query(callback_query.id)
    bot.send_message(callback_query.from_user.id, answer, reply_markup=[markup])


def yes_btn_pressed_func(callback_query, bot):
    data = parse_txt_file('config_bot_2.txt')
    user_cmd = callback_query.data
    idx = int(user_cmd[-1])
    bot.answer_callback_query(callback_query.id)
    bot.send_message(callback_query.from_user.id, data[f'write_transaction'][idx])


def pay_btn_pressed_func(callback_query, bot):
    data = parse_txt_file('config_bot_2.txt')
    user_cmd = callback_query.data
    idx = int(user_cmd[-1])
    bot.send_message(callback_query.message.chat.id, data[f'press_yes_when_pay'][idx])
    markup = types.InlineKeyboardMarkup(resize_keyboard=True)
    markup.add(types.InlineKeyboardButton(data[f'yes_btn'][idx], callback_data=f'yes_btn_pressed_{idx}'))
    bot.answer_callback_query(callback_query.id)
    bot.send_message(callback_query.from_user.id, data[f'BNB_info'][idx], reply_markup=[markup])


def step_service(data, message, support_btns, settings_btns, instruction_btns, bot):
    if message.text in support_btns:
        answer, idx = 'support', support_btns.index(message.text)
    elif message.text in settings_btns:
        answer, idx = 'settings', settings_btns.index(message.text)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(data[f'hash'][idx], callback_data=f'settings_hash_step1_{idx}'),
                   types.InlineKeyboardButton(data[f'language'][idx], callback_data=f'settings_lang_step1_{idx}'),
                   )
        bot.send_message(message.chat.id, data[f'{answer}_text'][idx], reply_markup=[markup])
        return
    elif message.text in instruction_btns:
        answer, idx = 'instruction', instruction_btns.index(message.text)
    else:
        return
    bot.send_message(message.chat.id, data[f'{answer}_text'][idx])


def step_start(data, message, bot):  # Step_1 /start
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton(data['lang'][0]), types.KeyboardButton(data['lang'][1]))
    markup.row(types.KeyboardButton(data['lang'][2]), types.KeyboardButton(data['lang'][3]))
    markup.row(types.KeyboardButton(data['lang'][4]))
    bot.send_message(message.chat.id, 'Choose language:', reply_markup=[markup])


def step_btn_pay(data, message, idx, bot):  # Step_2 (After language)
    registration_user_in_db(message.from_user.id, data[f'lang'][idx])
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(types.KeyboardButton(data[f'support'][idx]), types.KeyboardButton(data[f'settings'][idx]),
               types.KeyboardButton(data[f'instruction'][idx]))
    bot.send_message(message.chat.id, data[f'hi'][idx], reply_markup=[markup])
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(data[f'pay'][idx], callback_data=f'pay_btn_pressed_{idx}'))
    bot.send_message(message.chat.id, data[f'message_pay'][idx], reply_markup=[markup])
    return
    # bot.send_message(message.chat.id, data[f'message_pay'][idx], reply_markup=[markup])


def payment_success(data, message, bot):
    add_record_to_db(message.from_user.id, message.text)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    idx = get_lang(message, data)
    markup.row(types.KeyboardButton(data[f'support'][idx]), types.KeyboardButton(data[f'settings'][idx]),
               types.KeyboardButton(data[f'instruction'][idx]))
    bot.send_message(message.chat.id, data[f'payment_success'][idx], reply_markup=[markup])


def error_messages(data, message, bot, last_message):
    if last_message in data['support'] or last_message in data['settings'] or last_message in data['instruction']:
        message.text = last_message
        step_service(data, message, data['support'], data['settings'], data['instruction'],
                     bot)  # Методы из нижней сточки меню

    elif last_message == '/start':
        message.text = last_message
        step_start(data, message, bot)
    elif last_message in data['lang']:
        message.text = last_message
        step_btn_pay(data, message, data['lang'].index(last_message), bot)  # step_2
    else:
        print(last_message.data)
        try:
            if 'pay_btn_pressed' in last_message.data:
                pay_btn_pressed_func(last_message, bot)
                return
            elif 'yes_btn_pressed' in last_message.data:
                pay_btn_pressed_func(last_message, bot)
                return
            elif 'step1' in last_message.data or 'step2' in last_message.data:
                settings_step_1_func(last_message, bot)
        except:
            pass

        idx = get_lang(message, data)
        if idx == 'None':
            bot.send_message(message.chat.id, 'Unknown command. Please, write /start')
        else:
            bot.send_message(message.chat.id, data['error_message'][idx])


def settings_change_language_final_stage(message, f, bot):
    idx = get_lang(message, f)
    answer = f['all_save'][idx]
    bot.send_message(message.from_user.id, answer)


def settings_change_token_final_stage(message, f, bot):
    idx = get_lang(message, f)
    answer = f['all_save'][idx]
    bot.send_message(message.from_user.id, answer)
    step_btn_pay(f, message, idx, bot)
