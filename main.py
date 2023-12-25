import telebot
from telebot.types import Message
from telebot import types
from dotenv import load_dotenv
from os import getenv
import json
from questions import text

load_dotenv()
token = getenv('TOKEN')
bot = telebot.TeleBot(token=token)


@bot.message_handler(commands=['start'])
def start(message):
    """
    функция отправки сообщения в ответ на /start
    """

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_1 = types.KeyboardButton('начать')
    button_2 = types.KeyboardButton('продолжить')
    markup.add(button_1)
    users = load()
    user_id = str(message.chat.id)
    if user_id not in users:
        users[user_id] = {
            "progress": 1,
            "is_started": False,
            'l_v': 0,
            'social': 0
        }
        bot.send_message(chat_id=message.chat.id, text='вы добавлены')
        save(users)
    else:
        bot.send_message(chat_id=message.chat.id, text='вы уже в базе')
    if not users[user_id]["is_started"]:
        bot.send_message(chat_id=message.chat.id, text='начнем?', reply_markup=markup)
    elif users[user_id]["is_started"] and 0 < users[user_id]["progress"] < 20:
        markup.add(button_2)
        bot.send_message(chat_id=message.chat.id, text='хотите начать или продолжить уже начатый тест?', reply_markup=markup)
    else:
        bot.send_message(chat_id=message.chat.id, text='что?')


@bot.message_handler(commands=['help'])
def help(message: Message):
    """
    функция отправки сообщения в ответ на /help
    """
    bot.send_message(chat_id=message.chat.id,
                     text="""
/start - бот представится и поприветствует вас
/help - бот пришлет список доступных действий

                     """)


@bot.message_handler(content_types=['text'],
                     func=lambda message: message.text.lower() == 'начать' or message.text.lower() == 'продолжить')
def test_questions(message: Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = types.KeyboardButton('да')
    button_2 = types.KeyboardButton('скорее да')
    button_3 = types.KeyboardButton('скорее нет')
    button_4 = types.KeyboardButton('нет')
    markup.add(button_1, button_2, button_3, button_4)

    users = load()
    user_id = str(message.chat.id)
    progress_num = users[user_id]['progress']

    if users[user_id]['progress'] == 1:
        bot.send_message(chat_id=message.chat.id, text=text['disclaimer'])

    msg = bot.send_message(chat_id=message.chat.id, text=text['questions'][progress_num]['q'], reply_markup=markup)
    answer = message.text

    if answer in ['да', 'скорее да', 'скорее нет', 'нет']:
        new_l_v = users[user_id]['l_v'] + text['questions'][progress_num]['answers'][answer][0]
        new_social = users[user_id]['social'] + text['questions'][progress_num]['answers'][answer][1]
        users[user_id]['l_v'] = new_l_v
        users[user_id]['social'] = new_social
        users[user_id]['progress'] += 1
        save(users)
    else:
        bot.send_message(chat_id=message.chat.id, text='я вас не понял', reply_markup=markup)

    bot.register_next_step_handler(msg, test_questions)












filename = 'data.json'


def load() -> dict:
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except:
        return {}


def save(data: dict):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


bot.polling()