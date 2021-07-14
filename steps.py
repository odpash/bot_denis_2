from aiogram import types
from database_editing import registration_user_in_db, add_record_to_db, get_lang
from database_editing import parse_txt_file, read_records_from_db


def settings_step_1_func(callback_query, bot, m_id):
    f = parse_txt_file('config_bot_2.txt')
    db_lang, db_hash, _, _  = read_records_from_db(callback_query.from_user.id)
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
    return bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=m_id, text=answer, reply_markup=[markup]).message_id


def yes_btn_pressed_func(callback_query, bot, m_id):
    data = parse_txt_file('config_bot_2.txt')
    user_cmd = callback_query.data
    idx = int(user_cmd[-1])
    bot.answer_callback_query(callback_query.id)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(data[f'support'][idx], callback_data=f"support_cb{data[f'support'][idx]}"),
               types.InlineKeyboardButton(data[f'settings'][idx], callback_data=f"settings_cb{data[f'settings'][idx]}"),
               types.InlineKeyboardButton(data[f'instruction'][idx],
                                          callback_data=f"instruction_cb{data[f'instruction'][idx]}"))
    try:
        return bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=m_id, text=data[f'write_transaction'][idx], reply_markup=[markup]).message_id
    except:
        return bot.send_message(chat_id=callback_query.from_user.id, text=data[f'write_transaction'][idx], reply_markup=[markup]).message_id

def pay_btn_pressed_func(callback_query, bot, m_id):
    data = parse_txt_file('config_bot_2.txt')
    user_cmd = callback_query.data
    idx = int(user_cmd[-1])
    markup = types.InlineKeyboardMarkup(resize_keyboard=True)
    markup.add(types.InlineKeyboardButton(data[f'yes_btn'][idx], callback_data=f'yes_btn_pressed_{idx}'))
    bot.answer_callback_query(callback_query.id)
    try:
        return bot.edit_message_text(chat_id=callback_query.from_user.id, message_id=m_id, text=data[f'BNB_info'][idx], reply_markup=[markup]).message_id
    except:
        return bot.send_message(chat_id=callback_query.from_user.id, text=data[f'BNB_info'][idx], reply_markup=[markup]).message_id


def step_service(data, message, support_btns, settings_btns, instruction_btns, bot, m_id, chat_id):
    print(message)
    if message in support_btns:
        answer, idx = 'support', support_btns.index(message)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(data[f'pay'][idx], callback_data=f'pay_btn_pressed_{idx}'))
        markup.row(
            types.InlineKeyboardButton(data[f'settings'][idx], callback_data=f"settings_cb{data[f'settings'][idx]}"),
            types.InlineKeyboardButton(data[f'instruction'][idx],
                                       callback_data=f"instruction_cb{data[f'instruction'][idx]}"))
    elif message in settings_btns:
        answer, idx = 'settings', settings_btns.index(message)
        markup = types.InlineKeyboardMarkup()

        markup.add(types.InlineKeyboardButton(data[f'hash'][idx], callback_data=f'settings_hash_step1_{idx}'),
                   types.InlineKeyboardButton(data[f'language'][idx], callback_data=f'settings_lang_step1_{idx}'),
                   )
        markup.add(types.InlineKeyboardButton(data[f'pay'][idx], callback_data=f'pay_btn_pressed_{idx}'))
        try:
            return bot.edit_message_text(chat_id=chat_id, message_id=m_id, text=data[f'{answer}_text'][idx], reply_markup=[markup]).message_id
        except:
            return bot.send_message(chat_id=chat_id, text=data[f'{answer}_text'][idx], reply_markup=[markup]).message_id
    elif message in instruction_btns:
        answer, idx = 'instruction', instruction_btns.index(message)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(data[f'pay'][idx], callback_data=f'pay_btn_pressed_{idx}'))
        markup.row(
            types.InlineKeyboardButton(data[f'support'][idx], callback_data=f"support_cb{data[f'support'][idx]}"),
            types.InlineKeyboardButton(data[f'settings'][idx], callback_data=f"settings_cb{data[f'settings'][idx]}"))
    else:
        return
    try:
        return bot.edit_message_text(chat_id=chat_id, message_id=m_id, text=data[f'{answer}_text'][idx], reply_markup=[markup]).message_id
    except:
        return bot.send_message(chat_id=chat_id, text=data[f'{answer}_text'][idx], reply_markup=[markup]).message_id


def step_start(data, message, bot, m_id):  # Step_1 /start
    markup = markup = types.InlineKeyboardMarkup(resize_keyboard=True)
    markup.row(types.InlineKeyboardButton(data['lang'][0], callback_data='lang_' + data['lang'][0]),
               types.InlineKeyboardButton(data['lang'][1], callback_data='lang_' + data['lang'][1]))
    markup.row(types.InlineKeyboardButton(data['lang'][2], callback_data='lang_' + data['lang'][2]),
               types.InlineKeyboardButton(data['lang'][3], callback_data='lang_' + data['lang'][3]))
    markup.row(types.InlineKeyboardButton(data['lang'][4], callback_data='lang_' + data['lang'][4]))
    if m_id == 0:
        m_id = bot.send_message(message.chat.id, 'Choose language:', reply_markup=[markup]).message_id
    else:
        try:
            m_id = bot.edit_message_text(chat_id=message.chat.id, message_id=m_id, text='Choose language:', reply_markup=[markup]).message_id
        except:
            m_id = bot.send_message(chat_id=message.chat.id, text='Choose language:', reply_markup=[markup]).message_id
    return m_id


def step_btn_pay(data, message, idx, bot, m_id):  # Step_2 (After language)
    registration_user_in_db(message.from_user.id, data[f'lang'][idx])
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(data[f'pay'][idx], callback_data=f'pay_btn_pressed_{idx}'))
    markup.row(types.InlineKeyboardButton(data[f'support'][idx], callback_data=f"support_cb{data[f'support'][idx]}"), types.InlineKeyboardButton(data[f'settings'][idx], callback_data=f"settings_cb{data[f'settings'][idx]}"),
               types.InlineKeyboardButton(data[f'instruction'][idx], callback_data=f"instruction_cb{data[f'instruction'][idx]}"))
    try:
        m_id = bot.edit_message_text(chat_id=message.chat.id, message_id=m_id, text=data[f'message_pay'][idx], reply_markup=[markup]).message_id
    except:
        m_id = bot.send_message(chat_id=message.chat.id, text=data[f'message_pay'][idx], reply_markup=[markup]).message_id
    return m_id
    # bot.send_message(message.chat.id, data[f'message_pay'][idx], reply_markup=[markup])


def payment_success(data, message, bot):
    lang, hash_info, trans, wallet = read_records_from_db(message.from_user.id)
    add_record_to_db(message.from_user.id, trans, wallet)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    idx = get_lang(message, data)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(data[f'pay'][idx], callback_data=f'pay_btn_pressed_{idx}'))
    markup.row(types.InlineKeyboardButton(data[f'support'][idx], callback_data=f"support_cb{data[f'support'][idx]}"), types.InlineKeyboardButton(data[f'settings'][idx], callback_data=f"settings_cb{data[f'settings'][idx]}"),
               types.InlineKeyboardButton(data[f'instruction'][idx], callback_data=f"instruction_cb{data[f'instruction'][idx]}"))
    return bot.send_message(message.chat.id,data[f'payment_success'][idx], reply_markup=[markup]).message_id


def error_messages(data, message, bot, last_message):
    try:
        if last_message in data['support'] or last_message in data['settings'] or last_message in data['instruction']:
            message.text = last_message
            step_service(data, message, data['support'], data['settings'], data['instruction'],
                         bot)  # Методы из нижней сточки меню
        else:
            idx = get_lang(message, data)
            if idx == 'None':
                bot.send_message(message.chat.id, 'Unknown command. Please, write /start')
            else:
                bot.send_message(message.chat.id, data['error_message'][idx])
    except:
        idx = get_lang(message, data)
        bot.send_message(message.chat.id, data['error_trans'][get_lang(message, data)])
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton(data[f'support'][idx], callback_data=f"support_cb{data[f'support'][idx]}"),
            types.InlineKeyboardButton(data[f'settings'][idx], callback_data=f"settings_cb{data[f'settings'][idx]}"),
            types.InlineKeyboardButton(data[f'instruction'][idx],
                                       callback_data=f"instruction_cb{data[f'instruction'][idx]}"))
        bot.send_message(message.chat.id, data['write_transaction'][get_lang(message, data)], reply_markup=[markup])


def settings_change_language_final_stage(message, f, bot):
    idx = get_lang(message, f)
    answer = f['all_save'][idx]
    bot.send_message(message.from_user.id, answer)


def settings_change_token_final_stage(message, f, bot, m_id):
    idx = get_lang(message, f)
    answer = f['all_save'][idx]
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(f[f'support'][idx], callback_data=f"support_cb{f[f'support'][idx]}"),
        types.InlineKeyboardButton(f[f'settings'][idx], callback_data=f"settings_cb{f[f'settings'][idx]}"),
        types.InlineKeyboardButton(f[f'instruction'][idx],
                                   callback_data=f"instruction_cb{f[f'instruction'][idx]}"))
    return bot.send_message(chat_id=message.from_user.id, text=answer + '\n' + f['pump_funal_info'][idx], reply_markup=[markup]).message_id
