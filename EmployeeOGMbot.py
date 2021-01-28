import mysql.connector
import telebot
import re
from datetime import datetime
import json
db = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='12345',
    port='3306',
    database='ogm2'
)
cursor = db.cursor(True)
Query = {}
bot_3 = telebot.TeleBot('#')
EQuery = {}

@bot_3.message_handler(commands=['menu'])
def handle_commands(message):
    if message.text == '/menu':
        keyboard = telebot.types.InlineKeyboardMarkup()
        key_1 = telebot.types.InlineKeyboardButton('Все заявки (мои)', callback_data='my_queries')
        keyboard.add(key_1)
        key_2 = telebot.types.InlineKeyboardButton('Текущая заявка', callback_data='now_query')
        keyboard.add(key_2)
        key_3 = telebot.types.InlineKeyboardButton('Мои ТО', callback_data='my_to')
        keyboard.add(key_3)
        bot_3.send_message(message.chat.id, 'Меню', reply_markup=keyboard)

@bot_3.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'start_now':                     # принимаем заявку и идем на ремонт
        emp_id = call.message.chat.id

        sql = "SELECT employee_id FROM employees WHERE (tg_id = %s) and (master != True)"
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
            return
        try:
            sql = "SELECT query_id, query_status, json_emp FROM queries WHERE (query_status = 'В процессе') AND (multiple = '0')"  # блок приостановки тех заявок где исполнитель один
            cursor.execute(sql)
            all_queries = cursor.fetchall()
            my_queries = []
            for i in all_queries:  # сортировка по значению json файла
                json_emps_dict = json.loads(i[2])
                json_emps_list = json_emps_dict['doers']
                result_emp = int(json_emps_list[0])
                if result_emp == man_id:
                    my_queries.append(i)
            for i in my_queries:
                sql = "UPDATE queries SET query_status = 'Приостановлена' WHERE query_id = %s"
                val = (i[0],)
                cursor.execute(sql, val)
                db.commit()
        except:
            print('ошибка в кнопке старт нау')

        try:
            sql = "UPDATE worktime SET stop_time = %s WHERE (stop_time IS NULL) and (employee_id = %s)"   # останавливает работы которые в процессе
            val = (datetime.now(), man_id)
            cursor.execute(sql, val)
            db.commit()
        except:
            print('ошибка в кнопке старт нау')

        sql = "SELECT start_time FROM queries WHERE (query_id = %s)"  # проверка на то , начаты ли работы уже
        val = (EQuery['query_id'],)
        cursor.execute(sql, val)
        st = cursor.fetchone()
        print(st)
        if st[0] == None:
            sql = "UPDATE queries SET query_status = %s, start_time = %s WHERE query_id = %s "  # 3аписывает время начала выполнения заявки (start time)
            val = ('В процессе', datetime.now(), EQuery['query_id'])
            cursor.execute(sql, val)
            db.commit()
        sql = "INSERT INTO worktime (query_id, employee_id, start_time) VALUES (%s, %s, %s)"   # создает новую запись в работы
        val = (EQuery['query_id'], man_id, datetime.now())
        cursor.execute(sql, val)
        db.commit()

        bot_3.send_message(call.message.chat.id, 'Поехали!')
        bot_3.edit_message_text(call.message.text, call.message.chat.id, call.message.message_id)

    elif call.data == 'go_this_query':
        emp_id = call.message.chat.id
        try:
            sql = "SELECT employee_id FROM employees WHERE (tg_id = %s) and (master != True)"
            val = (emp_id,)
            cursor.execute(sql, val)
            man_id = cursor.fetchone()[0]

            msg = re.findall(r'\d+', call.message.text)  # блок считывания id заявки
            EQuery['query_id'] = msg[0]

            sql = "SELECT query_id, query_status, json_emp FROM queries WHERE (query_status = 'В процессе') AND (multiple = '0')"  # блок приостановки тех заявок где исполнитель один
            cursor.execute(sql)
            all_queries = cursor.fetchall()
            my_queries = []
            for i in all_queries:  # сортировка по значению json файла
                json_emps_dict = json.loads(i[2])
                json_emps_list = json_emps_dict['doers']
                result_emp = int(json_emps_list[0])
                if result_emp == man_id:
                    my_queries.append(i)
            for i in my_queries:
                sql = "UPDATE queries SET query_status = 'Приостановлена' WHERE query_id = %s"
                val = (i[0],)
                cursor.execute(sql, val)
                db.commit()

            sql = "SELECT start_time FROM queries WHERE (query_id = %s)"   #проверка на то , начаты ли работы уже
            val = (EQuery['query_id'],)
            cursor.execute(sql, val)
            st = cursor.fetchone()
            print(st)
            if st[0] == None:
                sql = "UPDATE queries SET query_status = %s, start_time = %s WHERE query_id = %s "  # 3аписывает время начала выполнения заявки (start time)
                val = ('В процессе', datetime.now(), EQuery['query_id'])
                cursor.execute(sql, val)
                db.commit()

            sql = "UPDATE worktime SET stop_time = %s WHERE (stop_time IS NULL) and (employee_id = %s)"  # останавливает работы которые в процессе
            val = (datetime.now(), man_id)
            cursor.execute(sql, val)
            db.commit()

            sql = "INSERT INTO worktime (query_id, employee_id, start_time) VALUES (%s, %s, %s)"  # создает новую запись в работы
            val = (EQuery['query_id'], man_id, datetime.now())
            cursor.execute(sql, val)
            db.commit()

            sql = "UPDATE queries SET query_status = %s WHERE query_id = %s"  # блок начала выполнения заявки (статус в процессе)
            val = ('В процессе', EQuery['query_id'])
            cursor.execute(sql, val)
            db.commit()

            bot_3.send_message(call.message.chat.id, 'Поехали!')
            bot_3.edit_message_text(call.message.text, call.message.chat.id, call.message.message_id)
        except:
            print('ошибка в го зис куери')

    elif call.data == 'start_later':                    # откладываем заявку чтобы открыть ее позже
        try:
            msg = re.findall(r'\d+', call.message.text)  # блок считывания id заявки
            EQuery['query_id'] = msg[0]

            sql = "SELECT query_status FROM queries WHERE query_id = %s"
            val = (EQuery['query_id'],)
            cursor.execute(sql, val)
            m = cursor.fetchone()
            if m[0] == 'Завершена':
                bot_3.send_message(call.message.chat.id, 'Заявка уже завершена...')
                return

            sql = "UPDATE queries SET query_status = %s WHERE query_id = %s "
            val = ('Отложена', EQuery['query_id'])
            cursor.execute(sql, val)
            db.commit()

            bot_3.send_message(call.message.chat.id, 'Сделаю позже...')
            bot_3.edit_message_text(call.message.text, call.message.chat.id, call.message.message_id)
        except:
            print('ошибка в старт лэйтер')

    elif call.data == 'my_queries':                                  # вывести все заявки сотрудника
        try:
            emp_id = call.message.chat.id                        # блок выделения id сотрудника
            sql = "SELECT employee_id FROM employees WHERE (tg_id = %s) and (master != True)"
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
                key_1 = telebot.types.InlineKeyboardButton('Приступить', callback_data='go_this_query')
                key_2 = telebot.types.InlineKeyboardButton('Комментарий', callback_data='leave_comment')
                keyboard.add(key_1, key_2)
                bot_3.send_message(call.message.chat.id, '*Id заявки: *' + str(query[6]) + "\n" + '*Наименование: *' + str(query[0]) + "\n" + "*Инв.№: *" + str(query[1]) + "\n" +
                                   "*Тип: *" + str(query[2]) + "\n" + "*Участок: *" + query[3] + "\n" + "*Причина поломки: *" +
                                   query[4] + "\n" + "*Сообщение: *" + str(query[5]), reply_markup=keyboard, parse_mode="Markdown")
        except Exception as ex:
            print(ex)

    elif call.data == 'now_query':                                  # вывести текущую заявку
        try:
            emp_id = call.message.chat.id                           # блок выделения id сотрудника
            sql = "SELECT employee_id FROM employees WHERE (tg_id = %s) and (master != True)"
            val = (emp_id,)
            cursor.execute(sql, val)
            man_id = cursor.fetchone()[0]
            # sql = "SELECT query_id, query_status, json_emp FROM queries WHERE (query_status = 'В процессе')"  # блок приостановки тех заявок где исполнитель один
            sql = "SELECT equipment.eq_name, equipment.invnum, equipment.eq_type, equipment.area, " \
                  "queries.reason, queries.msg, queries.query_id, queries.json_emp FROM " \
                  "equipment JOIN queries ON ((queries.eq_id = equipment.eq_id) AND (queries.query_status = %s)) "
            val = ("В процессе",)

            cursor.execute(sql, val)
            all_queries = cursor.fetchall()
            my_queries = []
            for i in all_queries:  # сортировка по значению json файла
                json_emps_dict = json.loads(i[-1])
                json_emps_list = json_emps_dict['doers']
                result_emps_list = [int(item) for item in json_emps_list]
                for j in result_emps_list:
                    if j == man_id:
                        my_queries.append(i)
            if len(my_queries) == 0:
                bot_3.send_message(call.message.chat.id, 'Кажется сейчас вы отдыхаете...')
            for query in my_queries:
                keyboard = telebot.types.InlineKeyboardMarkup()
                key_1 = telebot.types.InlineKeyboardButton('Приостановить выполнение заявки', callback_data='stop_this_query')
                keyboard.add(key_1)
                key_2 = telebot.types.InlineKeyboardButton('Заявка выполнена', callback_data='done_this_query')
                keyboard.add(key_2)
                bot_3.send_message(call.message.chat.id, '*id заявки: *' + str(query[-2]) + "\n" + '*Наименование: *' + query[0] + "\n" +
                               '*Инв.№: *' + query[1] + "\n" +
                               "*Тип: *" + query[2] + "\n" + "*Участок: *" + query[3] + "\n" + "*Причина поломки: *" +
                               query[4] + "\n" + "*Сообщение: *" + str(query[5]), reply_markup=keyboard, parse_mode="Markdown")
        except Exception as ex:
            print(ex)
            bot_3.send_message(call.message.chat.id, 'Кажется сейчас вы отдыхаете...')

    elif call.data == 'done_this_query':
        try:
            msg = re.findall(r'\d+', call.message.text)  # блок считывания id заявки
            EQuery['query_id'] = msg[0]
            sql = "UPDATE queries SET query_status = %s WHERE query_id = %s "
            val = ('Завершена', EQuery['query_id'])
            cursor.execute(sql, val)
            db.commit()

            sql = "UPDATE queries SET stop_time = %s WHERE query_id = %s"
            val = (datetime.now(), EQuery['query_id'])
            cursor.execute(sql, val)
            db.commit()

            sql = "SELECT * FROM worktime WHERE (query_id = %s) ORDER BY id DESC"
            val = (EQuery['query_id'],)
            cursor.execute(sql, val)
            work_id = cursor.fetchall()

            for i in work_id:
                sql = "UPDATE worktime SET stop_time = %s WHERE (id = %s)"
                val = (datetime.now(), i[0])
                cursor.execute(sql, val)
                db.commit()

            bot_3.send_message(call.message.chat.id, 'Отлично!')
            bot_3.edit_message_text(call.message.text, call.message.chat.id, call.message.message_id)
        except Exception as ex:
            print(ex)

    elif call.data == 'stop_this_query':
        try:
            msg = re.findall(r'\d+', call.message.text)  # блок считывания id заявки
            EQuery['query_id'] = msg[0]
            sql = "UPDATE queries SET query_status = %s WHERE query_id = %s "
            val = ('Приостановлена', EQuery['query_id'])
            cursor.execute(sql, val)
            db.commit()

            emp_id = call.message.chat.id  # блок выделения id сотрудника
            sql = "SELECT employee_id FROM employees WHERE (tg_id = %s) and (master != True)"
            val = (emp_id,)
            cursor.execute(sql, val)
            man_id = cursor.fetchone()[0]

            sql = "SELECT * FROM worktime WHERE (query_id = %s) ORDER BY id DESC"
            val = (EQuery['query_id'],)
            cursor.execute(sql, val)
            work_id = cursor.fetchall()

            for i in work_id:
                if i[2] == man_id:
                    sql = "UPDATE worktime SET stop_time = %s WHERE (id = %s)"
                    val = (datetime.now(), i[0])
                    cursor.execute(sql, val)
                    db.commit()

            bot_3.send_message(call.message.chat.id, 'Заявка приостановлена')
            bot_3.edit_message_text(call.message.text, call.message.chat.id, call.message.message_id)
        except:
            print('ошибка в соп зис кваери')

    elif call.data == 'leave_comment':
        try:
            emp_id = call.message.chat.id  # блок выделения id сотрудника
            sql = "SELECT employee_id FROM employees WHERE (tg_id = %s) and (master != True)"
            val = (emp_id,)
            cursor.execute(sql, val)
            man_id = cursor.fetchone()[0]

            msg = re.findall(r'\d+', call.message.text)  # блок считывания id заявки
            EQuery[man_id] = msg[0]

            msg = bot_3.send_message(call.message.chat.id, 'Слушаю...')
            bot_3.register_next_step_handler(msg, leave_comment)
        except:
            pass

    elif call.data == 'my_to':
        emp_id = call.message.chat.id  # блок выделения id сотрудника
        sql = "SELECT employee_id FROM employees WHERE (tg_id = %s) and (master != True)"
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
        msg = re.findall(r'\d+', call.message.text)  # блок считывания id то
        EQuery['to_id'] = msg[0]
        sql = "UPDATE maintenance SET status = %s, start_time = %s WHERE id = %s "
        val = ('В процессе', datetime.now(), EQuery['to_id'])
        cursor.execute(sql, val)
        db.commit()
        bot_3.send_message(call.message.chat.id, 'Поехали!')

    elif call.data == 'to_done':
        msg = re.findall(r'\d+', call.message.text)  # блок считывания id то
        EQuery['to_id'] = msg[0]
        sql = "UPDATE maintenance SET status = %s, end_time = %s WHERE id = %s "
        val = ('Завершено', datetime.now(), EQuery['to_id'])
        cursor.execute(sql, val)
        db.commit()
        bot_3.send_message(call.message.chat.id, 'Отлично!')

def leave_comment(message):
    try:
        emp_id = message.chat.id  # блок выделения id сотрудника
        sql = "SELECT employee_id FROM employees WHERE (tg_id = %s) and (master != True)"
        val = (emp_id,)
        cursor.execute(sql, val)
        man_id = cursor.fetchone()[0]

        #query = user_dict[chat_id]
        comment = message.text
        sql = "INSERT INTO comments (author, text, created_date, query) VALUES (%s, %s, %s, %s)"  # создает новую запись в комменты
        val = (man_id, comment, datetime.now(), EQuery[man_id])
        cursor.execute(sql, val)
        db.commit()

        bot_3.send_message(message.chat.id, 'Комментарий добавлен')
    except: print('ошибка в лив коммент')


while True:
    try:
        bot_3.polling(none_stop=True)
    except Exception as e:
        print(e)
