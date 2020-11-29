from bot.bot import Bot
from bot.handler import MessageHandler, BotButtonCommandHandler
import database
import event_handler
import config 

def run():
    main_bot = start_main_bot()
    start_bots()
    main_bot.idle()

def start_main_bot():
    main_bot = Bot(token=config.MAIN_TOKEN)
    main_bot.dispatcher.add_handler(MessageHandler(callback=event_handler.main_message_processing))
    main_bot.start_polling()
    return main_bot

def start_bots():
    # TOKENS = [
    #     "001.1767670269.2936977744:751623426",
    #     "001.1641510012.1982111967:751592865"
    # ]
    TOKENS = database.get_tokens()
    bots = []
    for token in TOKENS:
        bot_token = Bot(token=token)
        if bot_token.self_get().json()['ok']==True:
            bots.append(bot_token)
    for bot in bots:
        bot.dispatcher.add_handler(MessageHandler(callback=event_handler.message_processing))
        bot.dispatcher.add_handler(BotButtonCommandHandler(callback=event_handler.button_processing))
        bot.start_polling()

if __name__ == '__main__': 
	run()