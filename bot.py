import random
import requests
import telebot
import config
import dbworker

from BassBoost import boost, clean

bot = telebot.TeleBot(config.__token)
keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard1.row('5', '10', '15', '20', '25', '30')

keyboard2 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard2.row('0.5', '0.6', '0.7', '0.8', '0.9', '1', '1.1')


def is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


# По команде /reset будем сбрасывать состояния, возвращаясь к началу диалога
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Что ж, начнём по-новой ;)")
    dbworker.set_state(message.chat.id, config.States.S_START.value)


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Добро пожаловать!')
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAJ79V_Q2_6_mGRx6pMQaTmX3PyPRTOpAAI1AAN24i4Fls4_vHbHpAABHgQ')
    bot.send_message(message.chat.id, 'Выбери режим буста', reply_markup=keyboard1)
    dbworker.set_state(message.chat.id, config.States.S_ENTER_BOOST_MODE.value)



@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_ENTER_BOOST_MODE.value)
def entering_boost_mode(message):
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Что-то не так, попробуй ещё раз!")
        return
    if int(message.text) < 5 or int(message.text) > 41:
        bot.send_message(message.chat.id, "Не корректные данные для буста")
        return
    else:
        bot.send_message(message.chat.id, "Уровень буста = {0}".format(message.text))
        config.__BOOST_MODE = int(message.text)
        bot.send_message(message.chat.id, 'Выбери спид мод', reply_markup=keyboard2)
        dbworker.set_state(message.chat.id, config.States.S_SEND_SPEED_MODE.value)


@bot.message_handler(
    func=lambda message: dbworker.get_current_state(message.chat.id) == config.States.S_SEND_SPEED_MODE.value)
def entering_speed_mode(message):
    if not is_float(message.text):
        bot.send_message(message.chat.id, "Что-то не так, попробуй ещё раз!")
        return
    if float(message.text) <= 0.5 or float(message.text) > 1.5:
        bot.send_message(message.chat.id, "Некорректрые данные для спид мода")
        return
    else:
        bot.send_message(message.chat.id, "Уровень спид мода = {0}".format(message.text))
        bot.send_message(message.chat.id, "Добавьте трек для буста")
        config.__SPEED_MODE = float(message.text)
        dbworker.set_state(message.chat.id, config.States.S_TRACK_PROCESSING_MODE.value)



@bot.message_handler(content_types=['audio'], func=lambda message: dbworker.get_current_state(message.chat.id)
                                                                   == config.States.S_TRACK_PROCESSING_MODE.value )
def get_text_messages(message):
    if message.audio:
        file_id_info = bot.get_file(message.audio.file_id)
        file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(config.__token, file_id_info.file_path))
        try:
            name_track = message.audio.performer + ' - ' + message.audio.title + '.mp3'
        except:
            #name_track = message.json.audio.file_name
            name_track = message.json['audio']['file_name']
        with open(name_track, 'wb') as f:
            f.write(file.content)
        if message.audio.file_size // 1024 // 1024 < 10:
            bot.send_message(message.from_user.id, "Ждите, происходит обработка")
            final = boost(name_track, config.__BOOST_MODE, config.__SPEED_MODE)
            if(type(final) != 0):
                bot.send_audio(message.from_user.id, final)
            else:
                bot.send_message(message.from_user.id, "Бас должен быть больше 0")

            bot.send_message(message.from_user.id, "Готово!")
            bot.send_message(message.from_user.id, "Если вы хотете сбросить настройки буста, введите команду /reset")
            clean()
        else:
            bot.send_message(message.from_user.id,
                             "Много, давай что бы было меньше 10 Мб, не охота полдня бустить")
    elif message.text.lower() == "Привет":
        bot.send_message(message.from_user.id, "Привет-привет-привет")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Синтаксис работы: bst 10 1.5, "
                                               "\nгде bst - ключевое слово для работы "
                                               "\n10 - количество децибел, на которое будет увеличен бас"
                                               "\n1.5 - скорость, можно не писать, если не хочешь менять скорость трека, работает от 0.5 до 2")
    else:
        phrases = ["Здрасте", "Добрый вечер", "Здарова", "Привет"]
        mes = random.choice(phrases) + ". Если нужна помощь - пиши /help"
        bot.send_message(message.from_user.id, mes)
        mes = ""


if __name__ == '__main__':
    bot.polling()
