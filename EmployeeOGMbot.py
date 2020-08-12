import mysql.connector
import telebot
import re
from datetime import datetime
import json
from telebot import apihelper
import Send_message

#apihelper.proxy = {'https':'https://51.158.111.229:8811'}  # рабочий прокси Франция
#apihelper.proxy = {'https':'192.168.0.100:50278'}  #
while True:
    try:
        db = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='12345',
            port='3306',
            database='ogm2'
        )
        cursor = db.cursor(True)
        Query = {}
        bot_3 = telebot.TeleBot('1048673690:AAHPT1BfgqOoQ1bBXT1dcSiClLzwwOq0sPU')
        EQuery = {}

        sql = "SELECT tg_id FROM employees"
        cursor.execute(sql)
        allowed_users = cursor.fetchall()
        allowed_ids = []
        for i in allowed_users:
            allowed_ids.append(str(i[0]))
        @bot_3.message_handler(commands=['menu'])
        def handle_commands(message):
            if message.text == '/menu':
                emp_id = str(message.chat.id)
                if emp_id not in allowed_ids:
                    bot_3.send_message(message.chat.id, 'Вам не разрешено пользоваться этим ботом')
                else:
                    #keyboard = telebot.types.InlineKeyboardMarkup()
                    #key_1 = telebot.types.InlineKeyboardButton('Все заявки (мои)', callback_data='my_queries')
                    #keyboard.add(key_1)
                    #key_3 = telebot.types.InlineKeyboardButton('Мои ТО', callback_data='my_to')
                    #keyboard.add(key_3)
                    #bot_3.send_message(message.chat.id, 'Меню', reply_markup=keyboard)
                    bot_3.send_message(message.chat.id, 'Это версия бота v.2. Здесь нету меню, но зато вы можете '
                                                        'начинать, комментировать и заканчивать заявки прямо в том '
                                                        'сообщении в котором заявка пришла.')

        @bot_3.callback_query_handler(func=lambda call: True)
        def callback_worker(call):
            if call.data == 'start_now':                     # принимаем заявку и идем на ремонт
                db = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    passwd='12345',
                    port='3306',
                    database='ogm2'
                )
                cursor = db.cursor(True)
                emp_id = call.message.chat.id

                sql = "SELECT employee_id FROM employees WHERE (tg_id = %s)"
                val = (emp_id,)
                cursor.execute(sql, val)
                man_id = cursor.fetchone()[0]
                msg = re.findall(r'\d+', call.message.text)  # блок считывания id заявки
                EQuery['query_id'] = msg[0]

                sql = "SELECT query_status FROM queries WHERE query_id = %s"
                val = (EQuery['query_id'],)
                cursor.execute(sql, val)
                m = cursor.fetchone()
                if m[0] == 'Завершена':
                    bot_3.send_message(call.message.chat.id, 'Заявка уже завершена...')
                else:
                    try:
                        sql = "SELECT start_time FROM queries WHERE (query_id = %s)"  # проверка на то , начаты ли работы уже
                        val = (EQuery['query_id'],)
                        cursor.execute(sql, val)
                        st = cursor.fetchone()
                        if st[0] == None:
                            sql = "UPDATE queries SET query_status = %s, start_time = %s WHERE query_id = %s "  # 3аписывает время начала выполнения заявки (start time)
                            val = ('В процессе', datetime.now(), EQuery['query_id'])
                            cursor.execute(sql, val)
                            db.commit()
                        sql = "INSERT INTO worktime (query_id, employee_id, start_time) VALUES (%s, %s, %s)"   # создает новую запись в работы
                        val = (EQuery['query_id'], man_id, datetime.now())
                        cursor.execute(sql, val)
                        db.commit()

                        sql = "SELECT queries.query_id, equipment.eq_name, equipment.invnum, equipment.eq_type, " \
                              "equipment.area, queries.reason, queries.msg FROM equipment JOIN queries ON (queries.query_id = %s) AND (queries.eq_id = equipment.eq_id)"
                        val = (EQuery['query_id'],)
                        cursor.execute(sql, val)
                        query = cursor.fetchone()

                        keyboard = telebot.types.InlineKeyboardMarkup()
                        key_1 = telebot.types.InlineKeyboardButton('Заявка завершена...',
                                                                   callback_data='done_this_query')
                        keyboard.add(key_1)
                        #key_2 = telebot.types.InlineKeyboardButton('Комментарий...',
                        #                                           callback_data='leave_comment')
                        #keyboard.add(key_2)

                        key_3 = telebot.types.InlineKeyboardButton('Приостановить...', callback_data='stop_query')
                        keyboard.add(key_3)
                        bot_3.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                parse_mode="Markdown",
                                                text="*В ПРОЦЕССЕ*" + "\n" + "*id заявки: *" + str(query[0]) + "\n" +
                                                     "*Оборудование: *" + query[1] + "\n" + "*Инв.№: *" + query[2] + "\n" +
                                                     "*Тип станка: *" + query[3] + "\n" + "*Участок: *" + query[
                                                         4] + "\n" "*Причина поломки: *" + query[5] + "\n" + "*Сообщение: *" + str(query[6]) + "\n" + "*В процессе*")
                        bot_3.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                        reply_markup=keyboard)
                    except:
                        bot_3.send_message(call.message.chat.id, 'Что то не работает! Какая то ошибка в блоке start_now')

            elif call.data == 'start_now_work':
                db = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    passwd='12345',
                    port='3306',
                    database='ogm2'
                )
                cursor = db.cursor(True)
                emp_id = call.message.chat.id

                sql = "SELECT employee_id FROM employees WHERE (tg_id = %s)"
                val = (emp_id,)
                cursor.execute(sql, val)
                man_id = cursor.fetchone()[0]
                msg = re.findall(r'\d+', call.message.text)  # блок считывания id заявки
                EQuery['work_id'] = msg[0]

                sql = "SELECT query_status FROM unstated_works WHERE work_id = %s"
                val = (EQuery['work_id'],)
                cursor.execute(sql, val)
                m = cursor.fetchone()
                if m[0] == 'Завершена':
                    bot_3.send_message(call.message.chat.id, 'Работа уже завершена...')
                else:
                    try:
                        sql = "SELECT start_time FROM unstated_works WHERE (work_id = %s)"  # проверка на то , начаты ли работы уже
                        val = (EQuery['work_id'],)
                        cursor.execute(sql, val)
                        st = cursor.fetchone()
                        if st[0] == None:
                            sql = "UPDATE unstated_works SET query_status = %s, start_time = %s WHERE work_id = %s "  # 3аписывает время начала выполнения work (start time)
                            val = ('В процессе', datetime.now(), EQuery['work_id'])
                            cursor.execute(sql, val)
                            db.commit()
                        sql = "INSERT INTO worktime (work_id, employee_id, start_time) VALUES (%s, %s, %s)"  # создает новую запись в работы
                        val = (EQuery['work_id'], man_id, datetime.now())
                        cursor.execute(sql, val)
                        db.commit()

                        sql = "SELECT work_id, what FROM unstated_works WHERE work_id = %s"
                        val = (EQuery['work_id'],)
                        cursor.execute(sql, val)
                        work = cursor.fetchone()

                        keyboard = telebot.types.InlineKeyboardMarkup()
                        key_1 = telebot.types.InlineKeyboardButton('Заявка завершена...',
                                                                   callback_data='done_this_work')
                        keyboard.add(key_1)

                        key_3 = telebot.types.InlineKeyboardButton('Приостановить...', callback_data='stop_work')
                        keyboard.add(key_3)
                        bot_3.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                parse_mode="Markdown",
                                                text="*В ПРОЦЕССЕ*" + "\n" + "*id работы: *" + str(work[0]) + "\n" +
                                                    "*Сообщение: *" + str(work[1]) + "\n" + "*В процессе*")
                        bot_3.edit_message_reply_markup(chat_id=call.message.chat.id,
                                                        message_id=call.message.message_id,
                                                        reply_markup=keyboard)
                    except:
                        bot_3.send_message(call.message.chat.id,
                                           'Что то не работает! Какая то ошибка в блоке start_now')

            elif call.data == 'my_queries':                                  # вывести все заявки сотрудника
                #try:
                    db = mysql.connector.connect(
                        host='localhost',
                        user='root',
                        passwd='12345',
                        port='3306',
                        database='ogm2'
                    )
                    cursor = db.cursor(True)
                    emp_id = call.message.chat.id                        # блок выделения id сотрудника
                    sql = "SELECT employee_id FROM employees WHERE (tg_id = %s)"
                    val = (emp_id,)
                    cursor.execute(sql, val)
                    man_id = cursor.fetchone()[0]

                    sql = "SELECT equipment.eq_name, equipment.invnum, equipment.eq_type, equipment.area, " \
                          "queries.reason, queries.msg, queries.query_id, queries.json_emp FROM " \
                          "equipment JOIN queries ON ((queries.eq_id = equipment.eq_id) AND (" \
                          "queries.query_status != 'Завершена')) "
                    cursor.execute(sql)
                    all_queries = cursor.fetchall()
                    my_queries = []
                    print(all_queries)
                    if len(all_queries) == 0:
                        bot_3.send_message(call.message.chat.id, 'похоже сейчас заявок нет')
                    else:
                        for i in all_queries:               # сортировка по значению json файла
                            json_emps_dict = json.loads(i[7])
                            json_emps_list = json_emps_dict['doers']
                            result_emps_list = [int(item) for item in json_emps_list]
                            for j in result_emps_list:
                                if j == man_id:
                                    my_queries.append(i)

                        bot_3.send_message(call.message.chat.id, 'Мои заявки:')
                        for query in my_queries:
                            keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
                            key_1 = telebot.types.InlineKeyboardButton('Приступить', callback_data='done_this_query')
                            key_2 = telebot.types.InlineKeyboardButton('Комментарий', callback_data='leave_comment')
                            keyboard.add(key_1, key_2)
                            bot_3.send_message(call.message.chat.id, '*Id заявки: *' + str(query[6]) + "\n" + '*Наименование: *' + str(query[0]) + "\n" + "*Инв.№: *" + str(query[1]) + "\n" +
                                               "*Тип: *" + str(query[2]) + "\n" + "*Участок: *" + query[3] + "\n" + "*Причина поломки: *" +
                                               query[4] + "\n" + "*Сообщение: *" + str(query[5]), reply_markup=keyboard, parse_mode="Markdown")
                #except Exception as ex:
                    #print(ex)

            elif call.data == 'stop_query':
                # try:
                db = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    passwd='12345',
                    port='3306',
                    database='ogm2'
                )
                cursor = db.cursor(True)
                msg = re.findall(r'\d+', call.message.text)  # блок считывания id заявки
                EQuery['query_id'] = msg[0]
                sql = "SELECT query_status FROM queries WHERE query_id = %s"
                val = (EQuery['query_id'],)
                cursor.execute(sql, val)
                m = cursor.fetchone()
                if m[0] == 'Завершена':
                    sql = "SELECT queries.query_id, equipment.eq_name, equipment.invnum, equipment.eq_type, " \
                          "equipment.area, queries.reason, queries.msg, queries.comment FROM equipment JOIN queries ON (queries.query_id = %s) AND (queries.eq_id = equipment.eq_id)"
                    val = (EQuery['query_id'],)
                    cursor.execute(sql, val)
                    query = cursor.fetchone()
                    bot_3.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            parse_mode="Markdown",
                                            text="*ВЫПОЛНЕНА*" + "\n" + "*id заявки: *" + str(query[0]) + "\n" +
                                                 "*Оборудование: *" + query[1] + "\n" + "*Инв.№: *" + query[2] + "\n" +
                                                 "*Тип станка: *" + query[3] + "\n" + "*Участок: *" + query[
                                                     4] + "\n" "*Причина поломки: *" + query[
                                                     5] + "\n" + "*Сообщение: *" + str(
                                                query[6]) + "\n" + "*ВЫПОЛНЕНА*")
                else:
                    sql = "UPDATE queries SET query_status = %s WHERE query_id = %s "
                    val = ('Приостановлена', EQuery['query_id'])
                    cursor.execute(sql, val)
                    db.commit()
                    sql = "SELECT * FROM worktime WHERE (query_id = %s) ORDER BY id DESC"  # получаем все работы по заявке
                    val = (EQuery['query_id'],)
                    cursor.execute(sql, val)
                    work_id = cursor.fetchall()

                    for i in work_id:
                        sql = "UPDATE worktime SET stop_time = %s WHERE (id = %s) AND (stop_time IS NULL)"
                        val = (datetime.now(), i[0])
                        cursor.execute(sql, val)
                        db.commit()

                    sql = "SELECT queries.query_id, equipment.eq_name, equipment.invnum, equipment.eq_type, " \
                          "equipment.area, queries.reason, queries.msg FROM equipment JOIN queries ON (queries.query_id = %s) AND (queries.eq_id = equipment.eq_id)"
                    val = (EQuery['query_id'],)
                    cursor.execute(sql, val)
                    query = cursor.fetchone()

                    keyboard = telebot.types.InlineKeyboardMarkup()
                    key_1 = telebot.types.InlineKeyboardButton('Заявка завершена...',
                                                               callback_data='done_this_query')
                    keyboard.add(key_1)
                    key_2 = telebot.types.InlineKeyboardButton('Продолжить...', callback_data='continue')
                    keyboard.add(key_2)
                    bot_3.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            parse_mode="Markdown", reply_markup=keyboard,
                                            text="*ПРИОСТАНОВЛЕНА*" + "\n" + "*id заявки: *" + str(query[0]) + "\n" +
                                                 "*Оборудование: *" + query[1] + "\n" + "*Инв.№: *" + query[2] + "\n" +
                                                 "*Тип станка: *" + query[3] + "\n" + "*Участок: *" + query[
                                                     4] + "\n" "*Причина поломки: *" + query[
                                                     5] + "\n" + "*Сообщение: *" + str(
                                                query[6]) + "\n" + "*ПРИОСТАНОВЛЕНА*")
                    msg_to_delete = call.message.message_id
                    msg = bot_3.send_message(call.message.chat.id, 'Пожалуйста опишите причину приостановки:')
                    bot_3.register_next_step_handler(msg, leave_comment)

            elif call.data == 'done_this_work':
                # try:
                db = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    passwd='12345',
                    port='3306',
                    database='ogm2'
                )
                cursor = db.cursor(True)
                msg = re.findall(r'\d+', call.message.text)  # блок считывания id заявки
                EQuery['work_id'] = msg[0]
                sql = "SELECT query_status FROM unstated_works WHERE work_id = %s"
                val = (EQuery['work_id'],)
                cursor.execute(sql, val)
                m = cursor.fetchone()
                if m[0] == 'Завершена':
                    sql = "SELECT work_id, what FROM unstated_works WHERE work_id = %s"
                    val = (EQuery['work_id'],)
                    cursor.execute(sql, val)
                    work = cursor.fetchone()
                    bot_3.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            parse_mode="Markdown",
                                            text="*ВЫПОЛНЕНА*" + "\n" + "*id работы: *" + str(work[0]) + "\n" +
                                                "*Сообщение: *" + str(work[1]) + "\n" + "*ВЫПОЛНЕНА*")
                else:
                    sql = "UPDATE unstated_works SET query_status = %s WHERE work_id = %s "
                    val = ('Завершена', EQuery['work_id'])
                    cursor.execute(sql, val)
                    db.commit()
                    sql = "UPDATE unstated_works SET stop_time = %s WHERE work_id = %s"
                    val = (datetime.now(), EQuery['work_id'])
                    cursor.execute(sql, val)
                    db.commit()
                    sql = "SELECT * FROM worktime WHERE (work_id = %s) ORDER BY id DESC"  # получаем все работы по заявке
                    val = (EQuery['work_id'],)
                    cursor.execute(sql, val)
                    work_id = cursor.fetchall()

                    for i in work_id:
                        sql = "UPDATE worktime SET stop_time = %s WHERE (id = %s) AND (stop_time IS NULL)"
                        val = (datetime.now(), i[0])
                        cursor.execute(sql, val)
                        db.commit()

                    sql = "SELECT work_id, what FROM unstated_works WHERE work_id = %s"
                    val = (EQuery['work_id'],)
                    cursor.execute(sql, val)
                    work = cursor.fetchone()
                    bot_3.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            parse_mode="Markdown",
                                            text="*ВЫПОЛНЕНА*" + "\n" + "*id заявки: *" + str(work[0]) + "\n" +
                                                "*Сообщение: *" + str(work[1]) + "\n" + "*ВЫПОЛНЕНА*")
                    msg = bot_3.send_message(call.message.chat.id, 'Опишите выполненные работы...')
                    bot_3.register_next_step_handler(msg, leave_comment)

                    #try:
                    sql = "SELECT what FROM unstated_works WHERE work_id = %s"
                    val = (EQuery['work_id'],)
                    cursor.execute(sql, val)
                    message = cursor.fetchone()[0]
                    Send_message.send_message_5(message)
                   # except Exception as ex:
                     #   print(ex)

            elif call.data == 'continue':
                db = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    passwd='12345',
                    port='3306',
                    database='ogm2'
                )
                cursor = db.cursor(True)
                emp_id = call.message.chat.id

                sql = "SELECT employee_id FROM employees WHERE (tg_id = %s)"
                val = (emp_id,)
                cursor.execute(sql, val)
                man_id = cursor.fetchone()[0]
                msg = re.findall(r'\d+', call.message.text)  # блок считывания id заявки
                EQuery['query_id'] = msg[0]

                sql = "SELECT query_status FROM queries WHERE query_id = %s"
                val = (EQuery['query_id'],)
                cursor.execute(sql, val)
                m = cursor.fetchone()
                if m[0] == 'Завершена':
                    bot_3.send_message(call.message.chat.id, 'Заявка уже завершена...')
                else:
                    try:
                        sql = "INSERT INTO worktime (query_id, employee_id, start_time) VALUES (%s, %s, %s)"  # создает новую запись в работы
                        val = (EQuery['query_id'], man_id, datetime.now())
                        cursor.execute(sql, val)
                        db.commit()

                        sql = "SELECT queries.query_id, equipment.eq_name, equipment.invnum, equipment.eq_type, " \
                              "equipment.area, queries.reason, queries.msg FROM equipment JOIN queries ON (queries.query_id = %s) AND (queries.eq_id = equipment.eq_id)"
                        val = (EQuery['query_id'],)
                        cursor.execute(sql, val)
                        query = cursor.fetchone()

                        keyboard = telebot.types.InlineKeyboardMarkup()
                        key_1 = telebot.types.InlineKeyboardButton('Заявка завершена...',
                                                                   callback_data='done_this_query')
                        keyboard.add(key_1)
                        # key_2 = telebot.types.InlineKeyboardButton('Комментарий...',
                        #                                           callback_data='leave_comment')
                        # keyboard.add(key_2)

                        key_3 = telebot.types.InlineKeyboardButton('Приостановить...', callback_data='stop_query')
                        keyboard.add(key_3)
                        bot_3.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                parse_mode="Markdown",
                                                text="*В ПРОЦЕССЕ*" + "\n" + "*id заявки: *" + str(query[0]) + "\n" +
                                                     "*Оборудование: *" + query[1] + "\n" + "*Инв.№: *" + query[
                                                         2] + "\n" +
                                                     "*Тип станка: *" + query[3] + "\n" + "*Участок: *" + query[
                                                         4] + "\n" "*Причина поломки: *" + query[
                                                         5] + "\n" + "*Сообщение: *" + str(
                                                    query[6]) + "\n" + "*В ПРОЦЕССЕ*")
                        bot_3.edit_message_reply_markup(chat_id=call.message.chat.id,
                                                        message_id=call.message.message_id,
                                                        reply_markup=keyboard)
                    except:
                        bot_3.send_message(call.message.chat.id,
                                           'Что то не работает! Какая то ошибка в блоке continue')

            elif call.data == 'done_this_query':
                #try:
                db = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    passwd='12345',
                    port='3306',
                    database='ogm2'
                )
                cursor = db.cursor(True)
                msg = re.findall(r'\d+', call.message.text)  # блок считывания id заявки
                EQuery['query_id'] = msg[0]
                sql = "SELECT query_status FROM queries WHERE query_id = %s"
                val = (EQuery['query_id'],)
                cursor.execute(sql, val)
                m = cursor.fetchone()
                if m[0] == 'Завершена':
                    sql = "SELECT queries.query_id, equipment.eq_name, equipment.invnum, equipment.eq_type, " \
                          "equipment.area, queries.reason, queries.msg, queries.comment FROM equipment JOIN queries ON (queries.query_id = %s) AND (queries.eq_id = equipment.eq_id)"
                    val = (EQuery['query_id'],)
                    cursor.execute(sql, val)
                    query = cursor.fetchone()
                    bot_3.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            parse_mode="Markdown",
                                            text="*ВЫПОЛНЕНА*" + "\n" + "*id заявки: *" + str(query[0]) + "\n" +
                                                 "*Оборудование: *" + query[1] + "\n" + "*Инв.№: *" + query[2] + "\n" +
                                                 "*Тип станка: *" + query[3] + "\n" + "*Участок: *" + query[
                                                     4] + "\n" "*Причина поломки: *" + query[
                                                     5] + "\n" + "*Сообщение: *" + str(
                                                query[6]) + "\n" + "*ВЫПОЛНЕНА*")
                else:
                    sql = "UPDATE queries SET query_status = %s WHERE query_id = %s "
                    val = ('Завершена', EQuery['query_id'])
                    cursor.execute(sql, val)
                    db.commit()
                    sql = "UPDATE queries SET stop_time = %s WHERE query_id = %s"
                    val = (datetime.now(), EQuery['query_id'])
                    cursor.execute(sql, val)
                    db.commit()
                    sql = "SELECT * FROM worktime WHERE (query_id = %s) ORDER BY id DESC" #получаем все работы по заявке
                    val = (EQuery['query_id'],)
                    cursor.execute(sql, val)
                    work_id = cursor.fetchall()
                    sql = "SELECT eq_id FROM queries WHERE (query_id = %s)"   #получаем ид обордования и ставим статус "Работает"
                    val = (EQuery['query_id'],)
                    cursor.execute(sql, val)
                    eq_id = cursor.fetchone()[0]
                    sql = "UPDATE equipment SET eq_status = 'Работает' WHERE (eq_id = %s)"
                    val = (eq_id,)
                    cursor.execute(sql, val)

                    cursor.execute("SELECT * FROM eq_stoptime WHERE (eq_id = %s) AND (start_time IS NULL) ORDER BY id DESC LIMIT 1", [eq_id])
                    result = cursor.fetchone()
                    try:
                        result = list(result)
                        if len(result) > 0:
                            i = result[0]
                            cursor.execute("UPDATE eq_stoptime SET start_time = %s WHERE id = %s", [datetime.now(), i])
                            db.commit()
                    except:
                        pass

                    for i in work_id:
                        sql = "UPDATE worktime SET stop_time = %s WHERE (id = %s) AND (stop_time IS NULL)"
                        val = (datetime.now(), i[0])
                        cursor.execute(sql, val)
                        db.commit()

                    sql="SELECT queries.query_id, equipment.eq_name, equipment.invnum, equipment.eq_type, " \
                            "equipment.area, queries.reason, queries.msg FROM equipment JOIN queries ON (queries.query_id = %s) AND (queries.eq_id = equipment.eq_id)"
                    val = (EQuery['query_id'],)
                    cursor.execute(sql, val)
                    query = cursor.fetchone()
                    bot_3.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            parse_mode="Markdown",
                                            text="*ВЫПОЛНЕНА*" + "\n" + "*id заявки: *" + str(query[0]) + "\n" +
                                                 "*Оборудование: *" + query[1] + "\n" + "*Инв.№: *" + query[2] + "\n" +
                                                 "*Тип станка: *" + query[3] + "\n" + "*Участок: *" + query[
                                                     4] + "\n" "*Причина поломки: *" + query[
                                                     5] + "\n" + "*Сообщение: *" + str(
                                                query[6]) + "\n" + "*ВЫПОЛНЕНА*")
                    msg = bot_3.send_message(call.message.chat.id, 'Опишите выполненные работы...')
                    bot_3.register_next_step_handler(msg, leave_comment)

                    try:
                        sql = "SELECT eq_name, invnum, eq_type, area FROM equipment WHERE (eq_id = %s)"
                        val = (eq_id,)
                        cursor.execute(sql, val)
                        x = list(cursor.fetchone())
                        name = x[0]
                        invnum = x[1]
                        eq_type = x[2]
                        area = x[3]
                        sql = "SELECT msg FROM queries WHERE query_id = %s"
                        val = (EQuery['query_id'],)
                        cursor.execute(sql, val)
                        message = cursor.fetchone()[0]
                        Send_message.send_message_4(name, invnum, eq_type, area, message)
                    except Exception as ex:
                        print(ex)

            elif call.data == 'leave_comment':
                try:
                    db = mysql.connector.connect(
                        host='localhost',
                        user='root',
                        passwd='12345',
                        port='3306',
                        database='ogm2'
                    )
                    cursor = db.cursor(True)
                    emp_id = call.message.chat.id  # блок выделения id сотрудника
                    sql = "SELECT employee_id FROM employees WHERE (tg_id = %s)"
                    val = (emp_id,)
                    cursor.execute(sql, val)
                    man_id = cursor.fetchone()[0]

                    msg = re.findall(r'\d+', call.message.text)  # блок считывания id заявки
                    EQuery[man_id] = msg[0]

                    msg = bot_3.send_message(call.message.chat.id, 'Слушаю комментарий...')
                    bot_3.register_next_step_handler(msg, leave_comment)
                except Exception as ex:
                    print(ex)

            elif call.data == 'my_to':
                db = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    passwd='12345',
                    port='3306',
                    database='ogm2'
                )
                cursor = db.cursor(True)
                emp_id = call.message.chat.id  # блок выделения id сотрудника
                sql = "SELECT employee_id FROM employees WHERE (tg_id = %s)"
                val = (emp_id,)
                cursor.execute(sql, val)
                man_id = cursor.fetchone()[0]

                sql = "SELECT equipment.eq_name, equipment.invnum, equipment.eq_type, equipment.area, " \
                      "maintenance.id, maintenance.start_time, maintenance.end_time, maintenance.employee_id, maintenance.comment, maintenance.status FROM " \
                      "equipment JOIN maintenance ON ((maintenance.eq_id = equipment.eq_id) AND (" \
                      "maintenance.end_time IS NULL)) "
                cursor.execute(sql)
                all_to = cursor.fetchall()
                my_to = []
                for i in all_to:  # сортировка по значению json файла
                    json_emps_dict = json.loads(i[7])
                    json_emps_list = json_emps_dict['doers']
                    result_emps_list = [int(item) for item in json_emps_list]
                    for j in result_emps_list:
                        if j == man_id:
                            my_to.append(i)

                now_to = None
                for i in my_to:
                    if i[9] == 'В процессе':
                        now_to = i
                        break

                if now_to != None:
                    bot_3.send_message(call.message.chat.id, 'Текущее ТО:')
                    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
                    key_1 = telebot.types.InlineKeyboardButton('ТО выполнено!', callback_data='to_done')
                    keyboard.add(key_1)
                    bot_3.send_message(call.message.chat.id, '*Id ТО: *' + str(now_to[4]) + "\n" + '*Наименование: *' + str(
                        now_to[0]) + "\n" + "*Инв.№: *" + str(now_to[1]) + "\n" +
                                       "*Тип: *" + str(now_to[2]) + "\n" + "*Участок: *" + now_to[3], reply_markup=keyboard,
                                       parse_mode="Markdown")
                else:
                    bot_3.send_message(call.message.chat.id, 'Мои ТО:')
                    for query in my_to:
                        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
                        key_1 = telebot.types.InlineKeyboardButton('Приступить к ТО', callback_data='go_to')
                        keyboard.add(key_1)
                        bot_3.send_message(call.message.chat.id, '*Id ТО: *' + str(query[4]) + "\n" + '*Наименование: *' + str(
                            query[0]) + "\n" + "*Инв.№: *" + str(query[1]) + "\n" +
                                           "*Тип: *" + str(query[2]) + "\n" + "*Участок: *" + query[3], reply_markup=keyboard,
                                           parse_mode="Markdown")

            elif call.data == 'go_to':
                db = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    passwd='12345',
                    port='3306',
                    database='ogm2'
                )
                cursor = db.cursor(True)
                msg = re.findall(r'\d+', call.message.text)  # блок считывания id то
                EQuery['to_id'] = msg[0]

                sql = "SELECT equipment.eq_name, equipment.invnum, equipment.eq_type, equipment.area, maintenance.start_time " \
                      "FROM " \
                      "equipment JOIN maintenance ON ((maintenance.id = %s) AND (maintenance.eq_id = equipment.eq_id)) "
                val = (EQuery['to_id'],)
                cursor.execute(sql, val)
                msg = cursor.fetchone()

                sql = "SELECT status FROM maintenance WHERE (id = %s)"
                val = (EQuery['to_id'],)
                cursor.execute(sql, val)
                status = cursor.fetchone()
                if (status[0] == 'В процессе'):
                    keyboard = telebot.types.InlineKeyboardMarkup()
                    key_1 = telebot.types.InlineKeyboardButton('ТО_завершено. Неисправностей не обнаружено.',
                                                               callback_data='to_done')
                    keyboard.add(key_1)
                    key_2 = telebot.types.InlineKeyboardButton('ТО завершено. Есть комментарий...',
                                                               callback_data='comment_to')
                    keyboard.add(key_2)
                    bot_3.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text="*ТО в процессе*" + "\n" + "*id_TO: *" + str(EQuery['to_id']) + "\n" +
                                                 "*Оборудование: *" + msg[0] + "\n" + "*Инв.№: *" + msg[1] + "\n" +
                                                 "*Тип станка: *" + msg[2] + "\n" + "*Участок: *" + msg[
                                                     3] + "\n" "*Дата: *" + str(msg[4])[:10] + "\n" + "*ТО в процессе*",
                                            parse_mode="Markdown")
                    bot_3.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                                    reply_markup=keyboard)
                elif status[0] == 'Завершено':
                    bot_3.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text="*ТО завершено*" + "\n" + "*id_TO: *" + str(EQuery['to_id']) + "\n" +
                                                 "*Оборудование: *" + msg[0] + "\n" + "*Инв.№: *" + msg[1] + "\n" +
                                                 "*Тип станка: *" + msg[2] + "\n" + "*Участок: *" + msg[
                                                     3] + "\n" "*Дата: *" + str(msg[4])[
                                                                            :10],
                                            parse_mode="Markdown")
                    bot_3.send_message(call.message.chat.id, 'Отлично! ТО завершено')
                else:
                    sql = "UPDATE maintenance SET status = %s, start_time = %s WHERE id = %s "
                    val = ('В процессе', datetime.now(), EQuery['to_id'])
                    cursor.execute(sql, val)
                    db.commit()

                    keyboard = telebot.types.InlineKeyboardMarkup()
                    key_1 = telebot.types.InlineKeyboardButton('ТО_завершено. Неисправностей не обнаружено.', callback_data='to_done')
                    keyboard.add(key_1)
                    key_2 = telebot.types.InlineKeyboardButton('ТО завершено. Есть комментарий...', callback_data='comment_to')
                    keyboard.add(key_2)
                    bot_3.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="*ТО в процессе*" + "\n" + "*id_TO: *" + str(EQuery['to_id']) + "\n" +
                           "*Оборудование: *" + msg[0] + "\n" + "*Инв.№: *" + msg[1] + "\n" +
                           "*Тип станка: *" + msg[2] + "\n" + "*Участок: *" + msg[3] + "\n" "*Дата: *" + str(msg[4])[:10] + "\n" + "*ТО в процессе*", parse_mode="Markdown")
                    bot_3.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=keyboard)

            elif call.data == 'to_done':
                db = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    passwd='12345',
                    port='3306',
                    database='ogm2'
                )
                cursor = db.cursor(True)
                msg = re.findall(r'\d+', call.message.text)  # блок считывания id то
                EQuery['to_id'] = msg[0]

                sql = "SELECT equipment.eq_name, equipment.invnum, equipment.eq_type, equipment.area, maintenance.start_time " \
                      "FROM " \
                      "equipment JOIN maintenance ON ((maintenance.id = %s) AND (maintenance.eq_id = equipment.eq_id)) "
                val = (EQuery['to_id'],)
                cursor.execute(sql, val)
                msg = cursor.fetchone()

                sql = "SELECT status FROM maintenance WHERE (id = %s)"
                val = (EQuery['to_id'],)
                cursor.execute(sql, val)
                status = cursor.fetchone()
                if status[0] == 'Завершено':
                    bot_3.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text="*ТО завершено*" + "\n" + "*id_TO: *" + str(EQuery['to_id']) + "\n" +
                                                 "*Оборудование: *" + msg[0] + "\n" + "*Инв.№: *" + msg[1] + "\n" +
                                                 "*Тип станка: *" + msg[2] + "\n" + "*Участок: *" + msg[
                                                     3] + "\n" "*Дата: *" + str(msg[4])[
                                                                            :10],
                                            parse_mode="Markdown")
                    bot_3.send_message(call.message.chat.id, 'Отлично! ТО завершено')
                else:
                    sql = "UPDATE maintenance SET status = %s, end_time = %s WHERE id = %s "
                    val = ('Завершено', datetime.now(), EQuery['to_id'])
                    cursor.execute(sql, val)
                    db.commit()
                    bot_3.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                            text="*ТО завершено*" + "\n" + "*id_TO: *" + str(EQuery['to_id']) + "\n" +
                                                 "*Оборудование: *" + msg[0] + "\n" + "*Инв.№: *" + msg[1] + "\n" +
                                                 "*Тип станка: *" + msg[2] + "\n" + "*Участок: *" + msg[
                                                     3] + "\n" "*Дата: *" + str(msg[4])[:10], parse_mode="Markdown")
                    bot_3.send_message(call.message.chat.id, 'Отлично! ТО завершено')
            elif call.data == 'comment_to':
                db = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    passwd='12345',
                    port='3306',
                    database='ogm2'
                )
                cursor = db.cursor(True)
                msg = re.findall(r'\d+', call.message.text)  # блок считывания id то
                EQuery['to_id'] = msg[0]

                sql = "SELECT equipment.eq_name, equipment.invnum, equipment.eq_type, equipment.area, maintenance.start_time " \
                      "FROM " \
                      "equipment JOIN maintenance ON ((maintenance.id = %s) AND (maintenance.eq_id = equipment.eq_id)) "
                val = (EQuery['to_id'],)
                cursor.execute(sql, val)



                msg = cursor.fetchone()
                db.commit()
                bot_3.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                        text="*ТО завершено*" + "\n" + "*id_TO: *" + str(EQuery['to_id']) + "\n" +
                                             "*Оборудование: *" + msg[0] + "\n" + "*Инв.№: *" + msg[1] + "\n" +
                                             "*Тип станка: *" + msg[2] + "\n" + "*Участок: *" + msg[
                                                 3] + "\n" "*Дата: *" + str(msg[4])[
                                                                        :10],
                                        parse_mode="Markdown")

                msg = bot_3.send_message(call.message.chat.id, 'Слушаю комментарий...')
                bot_3.register_next_step_handler(msg, comment_to)


        def comment_to(message):
            try:
                db = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    passwd='12345',
                    port='3306',
                    database='ogm2'
                )
                cursor = db.cursor(True)
                comment = message.text
                sql = "UPDATE maintenance SET comment = %s WHERE id = %s"
                val = (comment, EQuery['to_id'])
                cursor.execute(sql, val)
                sql = "UPDATE maintenance SET status = %s, end_time = %s WHERE id = %s "
                val = ('Завершено', datetime.now(), EQuery['to_id'])
                cursor.execute(sql, val)
                db.commit()
                bot_3.send_message(message.chat.id, 'Комментарий записан, ТО завершено.')
            except Exception as ex:
                print(ex)
        def leave_comment(message):
            #try:
            db = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='12345',
                port='3306',
                database='ogm2'
            )
            cursor = db.cursor(True)
            emp_id = message.chat.id  # блок выделения id сотрудника
            sql = "SELECT employee_id FROM employees WHERE (tg_id = %s)"
            val = (emp_id,)
            cursor.execute(sql, val)
            man_id = cursor.fetchone()[0]
            #query = user_dict[chat_id]
            comment = message.text
            sql = "INSERT INTO comments (author, text, created_date, query) VALUES (%s, %s, %s, %s)"  # создает новую запись в комменты
            val = (man_id, comment, datetime.now(), EQuery['query_id'])
            cursor.execute(sql, val)
            db.commit()
            #bot_3.send_message(message.chat.id, 'Комментарий добавлен')
            msg = bot_3.send_message(message.chat.id, 'Введите потраченные ТМЦ (если ничего не потрачено - отправьте любой символ)')
            bot_3.register_next_step_handler(msg, supplies)
            #except: print('ошибка в лив коммент')

        def supplies(message):
            try:
                db = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    passwd='12345',
                    port='3306',
                    database='ogm2'
                )
                cursor = db.cursor(True)
                emp_id = message.chat.id  # блок выделения id сотрудника
                sql = "SELECT employee_id FROM employees WHERE (tg_id = %s)"
                val = (emp_id,)
                cursor.execute(sql, val)
                man_id = cursor.fetchone()[0]

                cursor.execute("SELECT eq_id FROM queries WHERE query_id = %s", [EQuery['query_id']])
                eq_id = cursor.fetchone()

                #query = user_dict[chat_id]
                supply = message.text
                sql = "INSERT INTO supplies (query_id, eq_id, supply, emp_id) VALUES (%s, %s, %s, %s)"  # создает новую запись в комменты
                val = (EQuery['query_id'], eq_id[0], supply, man_id)
                cursor.execute(sql, val)
                db.commit()

                bot_3.send_message(message.chat.id, 'Спасибо')

            except:
                print('ошибка в лив саплайс')
                bot_3.send_message(message.chat.id, 'Спасибо')


        while True:
            try:
                bot_3.polling(none_stop=True)
            except Exception as e:
                print(e)
    except: pass
