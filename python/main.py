import telebot
from telebot.types import Message
from telebot import types
from dotenv import load_dotenv
from os import getenv
from other import load, save
from questions import text

load_dotenv()
token = getenv('TOKEN')
bot = telebot.TeleBot(token=token)

markup_1 = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
markup_2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
markup_3 = types.ReplyKeyboardMarkup()
markup_4 = types.ReplyKeyboardRemove()

button_1 = types.KeyboardButton('начать')
button_2 = types.KeyboardButton('продолжить')
markup_1.row(button_1, button_2)


button_2_1 = types.KeyboardButton('да')
button_2_2 = types.KeyboardButton('скорее да')
button_2_3 = types.KeyboardButton('скорее нет')
button_2_4 = types.KeyboardButton('нет')
markup_2.row(button_2_1, button_2_2, button_2_3, button_2_4)


@bot.message_handler(commands=['start'])
def start(message):
    """
    Функция отправки сообщения в ответ на /start

    во время выполнения этой команды происходит регистрация пользователя
    :param message: команда /start
    :return:
    """

    users = load()
    user_id = str(message.chat.id)
    if user_id not in users:
        users[user_id] = {
            'progress': 1,
            'is_started': False,
            'l_v': 0,
            'social': 0,
            'ideologies': 'undefined'
        }
        save(users)

    bot.send_message(chat_id=message.chat.id, text='хотите начать или продолжить уже начатый тест?',
                     reply_markup=markup_1)


@bot.message_handler(commands=['help'])
def help_message(message: Message):
    """
    Функция отправки сообщения в ответ на /help

    :param message: команда /help
    :return:

    """
    bot.send_message(chat_id=message.chat.id,
                     text="""
слова 'начать' или 'продолжить' запускают тестирование, во время которого нельзя использовать все команды кроме /stop

/start - бот представится и поприветствует вас
/help - бот пришлет список доступных действий
/stop (активна только во время теста)- приостанавливает тестирование
                     """)


@bot.message_handler(content_types=['text'],
                     func=lambda message: message.text.lower() == 'начать' or message.text.lower() == 'продолжить')
def test_first_messages(message: Message):
    users = load()
    user_id = str(message.chat.id)

    message_text = message.text.lower()

    if not users[user_id]['is_started'] and message_text == 'продолжить':
        bot.send_message(chat_id=message.chat.id,
                         text='вы можете продолжить только уже начатый тест', reply_markup=markup_1)

    elif message_text == 'продолжить':
        msg = bot.send_message(chat_id=message.chat.id, text=text['questions'][users[user_id]['progress']]['q'],
                               reply_markup=markup_2)
        bot.register_next_step_handler(msg, test_answer)

    elif not users[user_id]['is_started'] and message_text == 'начать':
        bot.send_message(chat_id=message.chat.id, text=text['disclaimer'])
        with open('\dev\questionnaire_bot\images\img.png', 'rb') as image:
            bot.send_photo(chat_id=message.chat.id, photo=image, caption=text['degining'])
        users[user_id]['is_started'] = True
        users[user_id]['progress'] = 1
        save(users)

        bot.send_message(chat_id=message.chat.id, text=f'вопрос №1:', reply_markup=markup_2)
        msg = bot.send_message(chat_id=message.chat.id, text=text['questions'][users[user_id]['progress']]['q'],
                               reply_markup=markup_2)
        bot.register_next_step_handler(msg, test_answer)

    elif message_text == 'начать':
        users[user_id]['is_started'] = True
        users[user_id]['progress'] = 1
        save(users)

        msg = bot.send_message(chat_id=message.chat.id, text=text['questions'][users[user_id]['progress']]['q'],
                               reply_markup=markup_2)
        bot.register_next_step_handler(msg, test_answer)


def test_question(message: Message):
    """
    Функция отправки сообщения с вопросом

    сначала отправляется сообщение с номером вопроса, затем отправляется сам вопрос
    :param message: ответ пользователя на вопрос
    :return:
    """

    users = load()
    user_id = str(message.chat.id)
    progress_num = users[user_id]['progress']
    question_text = text['questions'][progress_num]['q']

    bot.send_message(chat_id=message.chat.id, text=f'вопрос №{progress_num}:', reply_markup=markup_2)
    msg = bot.send_message(chat_id=message.chat.id, text=question_text, reply_markup=markup_2)
    bot.register_next_step_handler(msg, test_answer)


def test_answer(message: Message):
    users = load()
    user_id = str(message.chat.id)
    progress_num = users[user_id]['progress']

    answer = message.text.lower()

    if answer in ['да', 'скорее да', 'скорее нет', 'нет']:
        new_l_v = users[user_id]['l_v'] + text['questions'][progress_num]['answers'][answer][0]
        new_social = users[user_id]['social'] + text['questions'][progress_num]['answers'][answer][1]
        users[user_id]['l_v'] = new_l_v
        users[user_id]['social'] = new_social
        users[user_id]['progress'] += 1

        save(users)
        bot.send_message(chat_id=message.chat.id, text='принято!', reply_markup=markup_2)
        if users[user_id]['progress'] == 21:
            final_message(message)
        else:
            test_question(message)
    elif answer == '/stop':
        bot.send_message(chat_id=message.chat.id, text='тестирование приостановлено', reply_markup=markup_4)
    else:
        msg = bot.send_message(chat_id=message.chat.id, text='я вас не понял', reply_markup=markup_2)
        bot.register_next_step_handler(msg, test_answer)


def final_message(message: Message):
    users = load()
    user_id = str(message.chat.id)
    if users[user_id]['l_v'] > 0 <= users[user_id]['social']:
        ideology = 'traditionalism'

    elif users[user_id]['l_v'] <= 0 < users[user_id]['social']:
        ideology = 'bolshevism'

    elif users[user_id]['l_v'] >= 0 > users[user_id]['social']:
        ideology = 'anarcho capitalism'

    elif users[user_id]['l_v'] <= 0 >= users[user_id]['social']:
        ideology = 'anarcho communism'

    else:
        ideology = 'кто ты?'

    users[user_id] = {
        'progress': 1,
        'is_started': False,
        'l_v': 0,
        'social': 0,
        'ideologies': ideology
                }
    save(users)
    link = text['description'][ideology]['flag']
    img_text = text['description'][ideology]['flag_about']
    with open(link, 'rb') as img:
        bot.send_photo(chat_id=message.chat.id, photo=img, caption=img_text)
    bot.send_message(chat_id=message.chat.id, text=text['description'][ideology]['text'], reply_markup=markup_4)


@bot.message_handler(content_types=['text'])
def echo(message: Message) -> None:
    """Функция ответа на некорректное сообщение от пользователя

    Функция отправляет сообщение с некорректным ответом от пользователя в формате
    'Вы напечатали: *сообщение пользователя*.что?'
    :param message: некорректное сообщение пользователя"""
    bot.send_message(chat_id=message.chat.id, text=f'Вы напечатали: {message.text}. Что?')


bot.polling()
