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


@dp.message_handler(commands=['start'])
async def on_message(message: types.Message):
    await bot.send_message(message.from_user.id, f" Привіт, {message.from_user.first_name} {message.from_user.last_name}! \n"
                                                 f" Давай поглянемо на курс: \n"
                                                 f" /create - Створити базу даних \n"
                                                 f" /insert - Внесення в базу даних \n"
                                                 f" /select - Вибрати історію курсів!")
    await sleep(1)


@dp.message_handler(commands=['create'])
async def create_db(message: types.Message):
    try:
        connect = psycopg2.connect(host="localhost", database="Yurii", user="postgres", password="EvevnW44")
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
    except Error as e:
        print(f"Error while connect to DATABASE {e}")
    cursor = await connect.cursor()

@dp.message_handler(commands=['insert'])
async def insert_db(message: types.Message):
    try:
        while True:
            currency = requests.get(URL).json()
            await asyncio.sleep(4)
            connect = psycopg2.connect(host="localhost", database="Yurii", user="postgres", password="EvevnW44")
            cursor = connect.cursor()
            cursor.execute(
                f"INSERT INTO currency (ccy, buy_price, sale_price) VALUES ('{currency[0]['ccy']}','{currency[0]['buy']}','{currency[0]['sale']}');")
            cursor.execute(
                f"INSERT INTO currency (ccy, buy_price, sale_price) VALUES ('{currency[1]['ccy']}','{currency[1]['buy']}','{currency[1]['sale']}');")
            cursor.execute(
                f"INSERT INTO currency (ccy, buy_price, sale_price) VALUES ('{currency[2]['ccy']}','{currency[2]['buy']}','{currency[2]['sale']}');")
            cursor.execute(
                f"INSERT INTO currency (ccy, buy_price, sale_price) VALUES ('{currency[3]['ccy']}','{currency[3]['buy']}','{currency[3]['sale']}');")

            connect.commit()
            cursor.close()
            connect.close()
    except Error as e:
        print(f"Error while connect to DATABASE {e}")
    cursor = await connect.cursor()

@dp.message_handler(commands=['select'])
async def select_db(message: types.Message):
    try:
        connect = psycopg2.connect(host="localhost", database="Yurii", user="postgres", password="EvevnW44")
        cursor = connect.cursor()
        cursor.execute("SELECT ccy, buy_price, sale_price, time FROM currency;")
        cursor.fetchone()
        result = cursor.fetchone()
        await bot.send_message(message.from_user.id,
                               f"Дані от такі:  Ccy: '{result[0]}', buy_price: {result[1]}, sale_price: {result[2]}, time: {result[3]}")
        connect.commit()
        cursor.close()
        connect.close()
    except Error as e:
        print(f"Error while connect to DATABASE {e}")
    cursor = await connect.cursor()

@dp.message_handler(commands=['delete'],)
async def delete_db(message: types.Message):
    try:
        await bot.send_message(message.from_user.id,
                               f" Для того щоб видалити вкажи номер id, наприклад (id=1,2 ....)")
        connect = psycopg2.connect(host="localhost", database="Yurii", user="postgres", password="EvevnW44")
        cursor = connect.cursor()
        cursor.execute(f"DELETE FROM currency WHERE id=2;")
        connect.commit()
        cursor.close()
        connect.close()
    except Error as e:
        print(f"Error while connect to DATABASE {e}")
    cursor = await connect.cursor()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
