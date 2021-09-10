import asyncio
import psycopg2
import requests
from psycopg2 import Error
from aiogram import Bot, Dispatcher, executor, types
from asyncio import sleep

loop = asyncio.get_event_loop()
URL = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'
bot = Bot('1904287315:AAEgT2qs7fEMHPY8_3Jw0pr1C6hQ0Ok3VHo')
dp = Dispatcher(bot, loop=loop)
currency = requests.get(URL).json()

async def connect_db():
    connect = None
    try:
        connect = psycopg2.connect(host="localhost", database="postgres", user="postgres", password="mpmp")
        return connect
    except Error as e:
        print(f"Error while connect to DATABASE {e}")
    cursor = connect.cursor()

@dp.message_handler(commands=['start'])
async def on_message(message: types.Message):
    await bot.send_message(message.from_user.id, f" Привіт, {message.from_user.first_name} {message.from_user.last_name}! \n"
                                                 f" Давай поглянемо на курс: \n"
                                                 f" /create - Створити базу даних \n"
                                                 f" /insert - Внесення в базу даних \n"
                                                 f" /select - Вибрати історію курсів!\n"
                                                 f" /delete - Видалення історії курсів")
    await sleep(1)

@dp.message_handler(commands=['create'])
async def create_db(message: types.Message):
    try:
        connect = await connect_db()
        cursor = connect.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS currency(
                id SERIAL,
                ccy VARCHAR,
                buy_price FLOAT,
                sale_price FLOAT,
                time TIMESTAMP (0) DEFAULT CURRENT_TIMESTAMP
                )""")
        connect.commit()
        cursor.close()
        connect.close()
        await bot.send_message(message.from_user.id, f'База даних створена!')
    except Error as e:
        print(f"Error while connect to DATABASE {e}")
        cursor = await connect.cursor()

@dp.message_handler(commands=['insert'])
async def insert_db(message: types.Message):
    try:
        while True:
            connect = await connect_db()
            cursor = connect.cursor()
            massiv = ''
            for values in currency:
                massiv += f"('{values['ccy']}', '{values['buy']}', '{values['sale']}'),"
            mass = massiv.replace(',',';')
            insert = mass.replace(';',',',11)
            cursor.execute(
                f"INSERT INTO currency (ccy, buy_price, sale_price) VALUES {insert}")
            await asyncio.sleep(5)
            connect.commit()
            cursor.close()
            connect.close()
            await bot.send_message(message.from_user.id,
                                   f" База даних наповнюється......) ")
    except Error as e:
        print(f"Error while connect to DATABASE {e}")
        cursor = await connect.cursor()

@dp.message_handler(commands=['select'])
async def select_db(message: types.Message):
    try:
        connect = await connect_db()
        cursor = connect.cursor()
        cursor.execute("SELECT ccy, buy_price, sale_price, time FROM currency ORDER BY id DESC LIMIT 4;")
        result = cursor.fetchall()
        text_massage = ''
        for i in result:
            massage =   f" Валюта: {i[0]}\n"\
                        f" Курс покупки: {i[1]}\n"\
                        f" Курс продажі: {i[2]}\n"\
                        f" Зафіксований час: {i[3]}\n"
            text_massage = text_massage + massage
        await bot.send_message(message.from_user.id, text_massage)
        connect.commit()
        cursor.close()
        connect.close()
    except Error as e:
        print(f"Error while connect to DATABASE {e}")
        cursor = await connect.cursor()

@dp.message_handler(commands=['delete'],)
async def delete_db(message: types.Message):
        await bot.send_message(message.from_user.id,
                               f" Для того щоб очитити дані таблиці, більші ніж за 2 години введи (/delete_old) ")
        await sleep(1)

@dp.message_handler(commands=['delete_old'],)
async def delete_db(message: types.Message):
    try:
        connect = await connect_db()
        cursor = connect.cursor()
        cursor.execute(f"DELETE FROM currency WHERE id NOT IN (SELECT id FROM currency ORDER BY id DESC LIMIT 4);")
        connect.commit()
        cursor.close()
        connect.close()
        await bot.send_message(message.from_user.id,
                               f" В базі даних залишилися тільки найновіші курси) ")
    except Error as e:
        print(f"Error while connect to DATABASE {e}")
        cursor = await connect.cursor()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
