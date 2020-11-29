from bot.bot import Bot
from bot.filter import Filter
from bot.handler import DefaultHandler, MessageHandler

import config
import database
from event_handler import add_bot, handler_bot, start_info


def start_bots():
    bots = []
    for token in database.get_tokens():
        bot_token = Bot(token=token)
        if bot_token.self_get().json()['ok']:
            bots.append(bot_token)
    for bot in bots:
        bot = handler_bot(bot)
        bot.start_polling()

    
main_bot = Bot(token=config.MAIN_TOKEN)
main_bot.dispatcher.add_handler(MessageHandler(
    callback=add_bot,
    filters=Filter.regexp(r'^/addbot')
))
main_bot.dispatcher.add_handler(DefaultHandler(callback=start_info))
main_bot.start_polling()
start_bots()
main_bot.idle()


