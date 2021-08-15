import config
import telebot
import requests
from telebot import types

bot = telebot.TeleBot(config.token)

# декодовка json, функцією json()
response = requests.get(config.url).json()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    itembtn1 = types.KeyboardButton('USD')
    itembtn2 = types.KeyboardButton('EUR')
    itembtn3 = types.KeyboardButton('RUR')
    itembtn4 = types.KeyboardButton('BTC')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    msg = bot.send_message(message.chat.id,
                      "Дізнатися курс Валют", reply_markup=markup)
    bot.register_next_step_handler(msg, process_coin_step)

def process_coin_step(message):
    try:
        markup = types.ReplyKeyboardRemove(selective=False)

        for coin in response:
            if (message.text == coin ['ccy']):
                bot.send_message(message.chat.id, printCoin(coin['buy'], coin['sale']),
                                 reply_markup=markup, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, 'Йопссс!')

def printCoin(buy, sale):
    '''Вивід курсу для користувача'''
    return " *Курс покупки:*" + str(buy) + "\n   *Курс продажі:*" + str(sale)

bot.enable_save_next_step_handlers(delay=2)


bot.load_next_step_handlers()

if __name__ == '__main__':
    bot.polling(none_stop=True)