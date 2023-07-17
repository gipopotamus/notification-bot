from telegram.ext import Updater
from config import BOT_TOKEN
from handlers import set_reminder_handler, button_handler


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(set_reminder_handler)
    dp.add_handler(button_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
