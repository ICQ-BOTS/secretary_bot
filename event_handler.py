from bot.bot import Bot
from bot.handler import MessageHandler, BotButtonCommandHandler
from bot.filter import Filter
import database
import re
import json
import messages


def init_user(func):
    def wrapper(*args, **kwargs):
        user_info = database.check_user(kwargs['event'].data["from"]["userId"])
        if user_info["not_exist"]:
            database.add_user(
                kwargs['event'].data["from"]["userId"],
                kwargs['event'].data["from"]["firstName"],
                kwargs['event'].data["from"].get('lastName', '')
            )
            user_info = database.check_user(
                kwargs['event'].data["from"]["userId"])
        func(*args, **kwargs)
    return wrapper


def except_cm(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except:
            message = messages.error_comand_both
            kwargs['bot'].send_text(
                chat_id=kwargs['event'].data["chat"]["chatId"], text=message)
    return wrapper


@init_user
def add_bot(bot, event):
    if len(event.data["text"]) > 8:
        text = event.data["text"][8:]
        add_new_bot(bot, event.data, text)
    else:
        message = "Ты забыл прислать данные бота :)"
        bot.send_text(chat_id=event.data["chat"]["chatId"], text=message)
        bot.send_text(chat_id=event.data["chat"]
                      ["chatId"], text=messages.main_message)


@init_user
def start_info(bot, event):
    if event.type.value == 'newMessage':
        bot.send_text(chat_id=event.data["chat"]
                      ["chatId"], text=messages.main_message)


@init_user
def message_cm(bot, event):
    if len(event.data["text"]) > 9:
        text = event.data["text"][20:]
        key = event.data["text"][9:19]
        update_message(bot, event.data, text, key)
    else:
        message = messages.error_comand_message
        bot.send_text(chat_id=event.data["chat"]["chatId"], text=message)


@init_user
def type_cm(bot, event):
    if len(event.data["text"]) > 6:
        key = event.data["text"][6:]
        update_type(bot, event.data, key)
    else:
        message = messages.error_comand_type
        bot.send_text(chat_id=event.data["chat"]["chatId"], text=message)


@init_user
def setchat_cm(bot, event):
    if len(event.data["text"]) > 9:
        text = event.data["text"][20:]
        key = event.data["text"][9:19]
        update_сhat(bot, event.data, text, key)
    else:
        message = messages.error_comand_type
        bot.send_text(chat_id=event.data["chat"]["chatId"], text=message)


@except_cm
@init_user
def ask_cm(bot, event):
    try:
        chat_type = database.get_public(bot.token)[0][4]
    except:
        chat_type = messages.first_message_dev
    if chat_type == "public" or chat_type == "both":
        if len(event.data["text"]) > 5:
            text = event.data["text"][5:]
            add_new_post(bot, event.data, text, "public")
        else:
            message = messages.error_comand_public
            bot.send_text(
                chat_id=event.data["chat"]["chatId"], text=message)
    else:
        message = messages.error_comand
        bot.send_text(
            chat_id=event.data["chat"]["chatId"], text=message)


@except_cm
@init_user
def anon_cm(bot, event):
    try:
        chat_type = database.get_public(bot.token)[0][4]
    except:
        chat_type = messages.first_message_dev
    if chat_type == "anon" or chat_type == "both":
        if len(event.data["text"]) > 6:
            text = event.data["text"][6:]
            add_new_post(bot, event.data, text, "anon")
        else:
            bot.send_text(
                chat_id=event.data["chat"]["chatId"],
                text=messages.error_comand_anon
            )
    else:
        bot.send_text(
            chat_id=event.data["chat"]["chatId"],
            text=messages.error_comand
        )


@init_user
def start_cm(bot, event):
    main_message(bot, event.data)


@init_user
def defauldt_cm(bot, event):
    if event.data["chat"]["type"] == "private":
        bot.send_text(
            chat_id=event.data["chat"]["chatId"],
            text=messages.error_comand_both
        )
    else:
        chat = bot.get_chat_info(event.data["chat"]["chatId"]).json()
        try:
            chat = chat["inviteLink"].split("/")[-1]
        except:
            message = "Бот не имеет прав администратора для данного чата"
            bot.send_text(chat_id=event.data["chat"]["chatId"], text=message)
            return
        try:
            chat_id = database.get_public(bot.token)[0][3]
        except:
            message = messages.first_message_dev
            bot.send_text(chat_id=event.data["chat"]["chatId"], text=message)
            return
        if chat == chat_id:
            if re.match(r'/answer', event.data["text"]):
                text = event.data["text"][8:]
                answer(bot, event.data, text)
            else:
                message = messages.error_comand_answer
                bot.send_text(
                    chat_id=event.data["chat"]["chatId"], text=message)


def but_anon(bot, event):
    database.update_type("anon", bot.token)
    message = "Тип бота успешно изменен на только анонимный"
    bot.send_text(chat_id=event.data["message"]
                  ["chat"]["chatId"], text=message)


def but_public(bot, event):
    database.update_type("public", bot.token)
    message = "Тип бота успешно изменен на только публичный"
    bot.send_text(chat_id=event.data["message"]
                  ["chat"]["chatId"], text=message)


def but_both(bot, event):
    database.update_type("both", bot.token)
    message = "Тип бота успешно изменен на анонимный и публичный"
    bot.send_text(chat_id=event.data["message"]
                  ["chat"]["chatId"], text=message)


def handler_bot(bot):
    bot.dispatcher.add_handler(MessageHandler(
        callback=message_cm,
        filters=Filter.regexp(r'^/message')
    ))
    bot.dispatcher.add_handler(MessageHandler(
        callback=type_cm,
        filters=Filter.regexp(r'^/type')
    ))
    bot.dispatcher.add_handler(MessageHandler(
        callback=setchat_cm,
        filters=Filter.regexp(r'^/setchat')
    ))
    bot.dispatcher.add_handler(MessageHandler(
        callback=ask_cm,
        filters=Filter.regexp(r'^/ask')
    ))
    bot.dispatcher.add_handler(MessageHandler(
        callback=anon_cm,
        filters=Filter.regexp(r'^/anon')
    ))
    bot.dispatcher.add_handler(MessageHandler(
        callback=start_cm,
        filters=Filter.regexp(r'^/start')
    ))
    bot.dispatcher.add_handler(MessageHandler(
        callback=defauldt_cm
    ))
    bot.dispatcher.add_handler(
        BotButtonCommandHandler(
            callback=but_anon,
            filters=Filter.callback_data_regexp(r'anon')
        )
    )
    bot.dispatcher.add_handler(
        BotButtonCommandHandler(
            callback=but_public,
            filters=Filter.callback_data_regexp(r'public')
        )
    )
    bot.dispatcher.add_handler(
        BotButtonCommandHandler(
            callback=but_both,
            filters=Filter.callback_data_regexp(r'both')
        )
    )
    return bot


def add_new_bot(bot, data, text):
    text_arr = text.split("\n")
    for text in text_arr:
        if re.match(r'token:', text):
            new_token = text[7:]
            # new_token
            public_info = database.check_public(new_token)
            if public_info["not_exist"]:
                seq_key = database.add_bot(new_token)
                text1 = messages.bot_ready
                bot.send_text(chat_id=data["chat"]["chatId"], text=text1)
                text2 = "Твой ключ безопасности для твоего бота " + \
                    str(seq_key) + "\nЗапомни его!"
                bot.send_text(chat_id=data["chat"]["chatId"], text=text2)
                new_bot = Bot(token=new_token)
                if new_bot.self_get().json()['ok'] == True:
                    new_bot = handler_bot(new_bot)
                    new_bot.start_polling()
            else:
                text = "Данный бот уже добавлен!"
                bot.send_text(chat_id=data["chat"]["chatId"], text=text)


def answer(bot, data, text):
    text_arr = text.split(" ")
    question_number = str(text_arr[0])
    question = database.get_post(question_number)
    try:
        question_token = question[2]
    except:
        message = "Данного вопроса не существует, проверьте введенный номер"
        bot.send_text(chat_id=data["chat"]["chatId"], text=message)
        return
    if question_token == bot.token:
        answer = ""
        for i in range(1, len(text_arr)):
            answer = answer + text_arr[i] + " "
        message = "Ответ на вопрос " + question_number + " успешно отправлен"
        bot.send_text(chat_id=data["chat"]["chatId"], text=message)
        bot.send_text(chat_id=question[3], text=answer)
    else:
        message = "Данный вопрос не принадлежит вашему боту, проверьте введенный номер"
        bot.send_text(chat_id=data["chat"]["chatId"], text=message)


def main_message(bot, data):
    try:
        message = database.get_public(bot.token)[0][-1]
    except:
        message = messages.first_message_dev
    if message == "none":
        message = messages.first_message_dev
    bot.send_text(chat_id=data["chat"]["chatId"], text=message)


def add_new_post(bot, data, text, post_type):
    if post_type == "public":
        text = text + "\n\nАвтор: @["+str(data["chat"]["chatId"])+"]"
    new_id = database.add_post(
        text, post_type, data["chat"]["chatId"], bot.token)
    text = text + "\n\nНомер вопроса для ответа: " + str(new_id)
    try:
        chat_id = database.get_public(bot.token)[0][3]
    except:
        message = messages.first_message_dev
        bot.send_text(chat_id=data["chat"]["chatId"], text=message)
        return
    bot.send_text(chat_id=chat_id, text=text)
    message = messages.ask_success
    bot.send_text(chat_id=data["chat"]["chatId"], text=message)


def update_message(bot, data, message, key):
    secret_key = database.check_public(bot.token)["seq_key"]
    if key == secret_key:
        database.update_message(bot.token, message)
        message = "Первое сообщение для этого бота было успешно изменено на:\n\n" + message
    else:
        message = "Ключ безопасности не совпадает"
    bot.send_text(chat_id=data["chat"]["chatId"], text=message)


def update_сhat(bot, data, chat, key):
    secret_key = database.check_public(bot.token)["seq_key"]
    if key == secret_key:
        if "https://icq.im/" in chat:
            chat = chat.split("/")[-1]
            database.update_сhat(bot.token, chat)
            message = "Чат модерации для этого бота было успешно изменен на:\n\n" + chat
        else:
            database.update_сhat(bot.token, chat)
            message = "Некоректная ссылка на чат:\n\n" + chat
    else:
        message = "Ключ безопасности не совпадает"
    bot.send_text(chat_id=data["chat"]["chatId"], text=message)


def update_chat(bot, data, message, key):
    secret_key = database.check_public(bot.token)["seq_key"]
    if key == secret_key:
        database.update_message(bot.token, message)
        message = "Первое сообщение для этого бота было успешно изменено на:\n\n" + message
    else:
        message = "Ключ безопасности не совпадает"
    bot.send_text(chat_id=data["chat"]["chatId"], text=message)


def update_type(bot, data, key):
    secret_key = database.check_public(bot.token)["seq_key"]
    if key == secret_key:
        message = "Выберите тип доступных сообщений для вашего бота секретаря"
        inline_keyboard_markup = json.dumps([
            [{"text": "Только Анонимные", "callbackData": "anon"}],
            [{"text": "Только Публичные", "callbackData": "public"}],
            [{"text": "Анонимные и Публичные", "callbackData": "both"}]
        ])
        bot.send_text(chat_id=data["chat"]["chatId"], text=message,
                      inline_keyboard_markup=inline_keyboard_markup)
    else:
        message = "Ключ безопасности не совпадает"
        bot.send_text(chat_id=data["chat"]["chatId"], text=message)
