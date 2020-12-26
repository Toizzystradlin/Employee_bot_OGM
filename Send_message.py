import mysql.connector
import json


def send_message_1(query_id, name, inv, place, cause, msg):  # функция для отправки уведомления о новой заявке мастеру
    import telebot
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='12345',
        port='3306',
        database='ogm2'
    )
    cursor3 = db.cursor(buffered=True)
    sql = "SELECT tg_id FROM employees WHERE (master = True)"
    cursor3.execute(sql)
    masters_id = cursor3.fetchall()
    print(masters_id)

    bot_2 = telebot.TeleBot('1044824865:AAGACPaLwqHdOMn5HZamAmSljkoDvSwOiBw')

    keyboard = telebot.types.InlineKeyboardMarkup()
    key_choose = telebot.types.InlineKeyboardButton('Назначить ...', callback_data='choose')
    keyboard.add(key_choose)
    key_postpone = telebot.types.InlineKeyboardButton('Отложить', callback_data='postpone')
    keyboard.add(key_postpone)


    #392674056
    for i in masters_id:
        try:
            bot_2.send_message(i[0], "*НОВАЯ ЗАЯВКА*" + "\n" + "*id_заявки: *" + str(
            query_id) + "\n" + "*Наименование: *" + name + "\n" +
                       "*Инв.№: *" + inv + "\n" + "*Участок: *" + place + "\n" + "*Причина поломки: *" +
                       cause + "\n" + "*Сообщение: *" + msg, reply_markup=keyboard, parse_mode="Markdown")
        except:
            pass


def send_message_2(id_employee, query_id):  # функция для отправки уведомления сотруднику
    import telebot
    bot_3 = telebot.TeleBot('1048673690:AAHPT1BfgqOoQ1bBXT1dcSiClLzwwOq0sPU')
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='12345',
        port='3306',
        database='ogm2'
    )
    cursor3 = db.cursor(buffered=True)
    sql = "SELECT equipment.eq_name, equipment.invnum, equipment.eq_type, equipment.area, " \
          "queries.reason, queries.msg FROM " \
          "equipment JOIN queries ON ((queries.query_id = %s) AND (queries.eq_id = equipment.eq_id)) "
    val = (query_id,)
    cursor3.execute(sql, val)
    msg = cursor3.fetchone()
    print(msg)

    keyboard = telebot.types.InlineKeyboardMarkup()
    key_start_now = telebot.types.InlineKeyboardButton('Начинаю выполнение', callback_data='start_now')
    keyboard.add(key_start_now)
    key_start_later = telebot.types.InlineKeyboardButton('Отложить', callback_data='start_later')
    keyboard.add(key_start_later)

    bot_3.send_message(id_employee, "У вас новая заявка" + "\n" + "*id_заявки: *" + str(query_id) + "\n" +
                       "*Оборудование: *" + msg[0] + "\n" + "*Инв.№: *" + msg[1] + "\n" +
                       "*Тип станка: *" + msg[2] + "\n" + "*Участок: *" + msg[3] + "\n" +
                       "*Причина поломки: *" + msg[4] + "\n" + "*Сообщение: *" + str(msg[5]), reply_markup=keyboard,
                       parse_mode="Markdown")

    cursor3.close()


def send_message_3(query_id):
    import telebot
    bot_3 = telebot.TeleBot('1044824865:AAGACPaLwqHdOMn5HZamAmSljkoDvSwOiBw')
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='12345',
        port='3306',
        database='ogm2'
    )
    cursor3 = db.cursor(buffered=True)
    sql = "SELECT equipment.eq_name, equipment.invnum, equipment.eq_type, equipment.area, " \
          "queries.reason, queries.msg FROM " \
          "equipment JOIN queries ON ((queries.query_id = %s) AND (queries.eq_id = equipment.eq_id)) "
    val = (query_id,)
    cursor3.execute(sql, val)
    msg = cursor3.fetchone()

    bot_3.send_message(392674056, "*id_заявки: *" + str(query_id) + "\n" +
                       "*Оборудование: *" + msg[0] + "\n" + "*Инв.№: *" + msg[1] + "\n" +
                       "*Тип станка: *" + msg[2] + "\n" + "*Участок: *" + msg[3] + "\n" +
                       "*Причина поломки: *" + msg[4] + "\n" + "*Сообщение: *" + str(msg[5]), parse_mode="Markdown")
    cursor3.close()


def send_message_4(query_id, name, eq_type, inv, area, msg, doers):
    import telebot
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='12345',
        port='3306',
        database='ogm2'
    )
    cursor4 = db.cursor(buffered=True)
    #sql = "SELECT tg_id FROM employees WHERE (master = True)"
    sql = "SELECT tg_id FROM employees WHERE (rank = 'инженер')"
    cursor4.execute(sql)
    masters_id = cursor4.fetchall()

    bot_2 = telebot.TeleBot('1044824865:AAGACPaLwqHdOMn5HZamAmSljkoDvSwOiBw')
    for i in masters_id:
        bot_2.send_message(i[0], "*ЗАЯВКА ВЫПОЛНЕНА*" + "\n" + "*Id заявки: *" + str(query_id) + "\n" + "*Наименование: *" + str(name) + "\n" +
                           "*Инв.№: *" + str(inv) + "\n" + "*Тип оборудования: *" + str(
            eq_type) + "\n" + "*Участок: *" + str(area) + "\n" + "*Сообщение: *" + str(msg) + "\n" + "*Выполнил: *" + doers + "\n" +
                           "*ЗАЯВКА ВЫПОЛНЕНА*", parse_mode="Markdown")
    cursor4.close()

def send_message_5(text, doers):
    import telebot
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='12345',
        port='3306',
        database='ogm2'
    )
    cursor4 = db.cursor(buffered=True)
    #sql = "SELECT tg_id FROM employees WHERE (master = True)"
    sql = "SELECT tg_id FROM employees WHERE (rank = 'инженер')"
    cursor4.execute(sql)
    masters_id = cursor4.fetchall()

    bot_2 = telebot.TeleBot('1044824865:AAGACPaLwqHdOMn5HZamAmSljkoDvSwOiBw')
    for i in masters_id:
        bot_2.send_message(i[0], "*ЗАЯВКА ВЫПОЛНЕНА*" + "\n" + "*Сообщение: *" + str(text) + "\n" + "*Выполнил: *" + doers + "\n" +
                           "*ЗАЯВКА ВЫПОЛНЕНА*", parse_mode="Markdown")
    cursor4.close()

def send_message_6(name, eq_type, inv, area):
    import telebot
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='12345',
        port='3306',
        database='ogm2'
    )
    cursor4 = db.cursor(buffered=True)
    #sql = "SELECT tg_id FROM employees WHERE (master = 1)"
    sql = "SELECT tg_id FROM employees WHERE (rank = 'инженер')"
    cursor4.execute(sql)
    masters_id = cursor4.fetchall()

    bot_2 = telebot.TeleBot('1044824865:AAGACPaLwqHdOMn5HZamAmSljkoDvSwOiBw')
    for i in masters_id:
        bot_2.send_message(i[0], "*ТО ЗАВЕРШЕНО*" + "\n" + "*Наименование: *" + str(name) + "\n" +
                           "*Инв.№: *" + str(inv) + "\n" + "*Тип оборудования: *" + str(
            eq_type) + "\n" + "*Участок: *" + str(area) + "\n" +
                           "*ТО ЗАВЕРШЕНО*", parse_mode="Markdown")
    cursor4.close()

def notification_to_creator(query_id):
    import telebot
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='12345',
        port='3306',
        database='ogm2'
    )
    cursor4 = db.cursor(buffered=True)

    bot_q = telebot.TeleBot('1048146486:AAGwY0ClpWvUtjlBy-D6foxhIntZUFb7-5s', threaded=False)
    cursor4.execute("SELECT queries.query_id, queries.msg, queries.creator_tg_id, equipment.invnum, equipment.eq_name, equipment.eq_type, equipment.area "
                   "FROM queries JOIN equipment WHERE queries.query_id = %s AND queries.eq_id = equipment.eq_id", [query_id])
    data = cursor4.fetchone()
    cursor4.execute("SELECT creator_notificated FROM queries WHERE query_id = %s", [query_id])
    creator_notificated = cursor4.fetchone()[0]
    if creator_notificated == None:
        bot_q.send_message(data[2], "*ЗАЯВКА ЗАВЕРШЕНА*"  + "\n" + "*Наименование: *" + data[4] + "\n" + "*Инв.№: *" + data[3] + "\n" + "*Тип станка: *" + data[5] +
                            "\n" + "*Участок: *" + data[6] + "\n" + "*Поломка: *" + data[1], parse_mode="Markdown")
        cursor4.execute("UPDATE queries SET creator_notificated = 1 WHERE query_id = %s", [data[0]])