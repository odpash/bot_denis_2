import sqlite3
import json


def change_user_param_in_db(telegram_id, param, param_name):
    sqlite_connection = sqlite3.connect('telegram_bot_2.db')
    cursor = sqlite_connection.cursor()
    sql_update_query = f"""Update table_users set {param_name} = '{param}' where telegram_id = '{telegram_id}'"""
    cursor.execute(sql_update_query)
    sqlite_connection.commit()
    cursor.close()
    sqlite_connection.close()


def read_records_from_db(telegram_id):
    sqlite_connection = sqlite3.connect('telegram_bot_2.db')
    cursor = sqlite_connection.cursor()
    sqlite_select_query = """SELECT * from table_users"""
    cursor.execute(sqlite_select_query)
    records = cursor.fetchall()
    lang, hash_info = '', ''
    for row in records:
        if str(telegram_id) == row[0]:
            lang, hash_info = row[1], row[2]
    cursor.close()
    sqlite_connection.close()
    return lang, hash_info


def registration_user_in_db(telegram_id, language):
    a, b = read_records_from_db(telegram_id)
    if a == '' and b == '':
        sqlite_connection = sqlite3.connect('telegram_bot_2.db')
        cursor = sqlite_connection.cursor()
        sqlite_insert_query = f"""INSERT INTO table_users (telegram_id, user_language, hash) VALUES ('{telegram_id}', '{language}', 'None');"""
        count = cursor.execute(sqlite_insert_query)
        sqlite_connection.commit()
        cursor.close()
        sqlite_connection.close()
    else:
        change_user_param_in_db(telegram_id, language, 'user_language')


def add_record_to_db(telegram_id, transaction_id):
    sqlite_connection = sqlite3.connect('telegram_bot_2.db')
    cursor = sqlite_connection.cursor()
    sqlite_insert_query = f"""INSERT OR REPLACE INTO table_transactions (telegram_id, transaction_id) VALUES ('{telegram_id}', '{transaction_id}');"""
    count = cursor.execute(sqlite_insert_query)
    sqlite_connection.commit()
    cursor.close()
    sqlite_connection.close()


def parse_txt_file(filename):
    return json.loads(open(filename, mode='r', encoding='UTF-8').read())


def get_lang(message, data):
    db_lang, _ = read_records_from_db(message.from_user.id)
    if db_lang == '':
        return 'None'
    idx = -1
    for i in data['lang']:
        idx += 1
        if i == db_lang:
            break
    return idx
