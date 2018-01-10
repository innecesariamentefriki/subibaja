#!/usr/bin/python
# -*- coding: utf-8 -*-
from cleverwrap import CleverWrap
cw = CleverWrap("")

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# almacenamiento con sqlite
import datos as dts

import time
import logging

# Enable logging
logging.basicConfig(filename='chatbot.log',
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)




def start(bot, update):
    update.message.reply_text("""\
Indico con precisión los mejores momentos para comprar y vender criptomonedas.
Si sigues mis consejos podrás comprar barato y vender caro.\
""")
    time.sleep(6)
    update.message.reply_text("O esa es la intención al menos.")
    time.sleep(2)
    update.message.reply_text("""\
Sólo tienes que esperar a que te dé mis consejos. En caso de que tengas alguna duda puedes consultar la /ayuda.\
""")
    logger.info(update)

    # si entra un usuario nuevo, se le añade automáticamente al feed de chivatazos
    newuser = update['message']['chat']['first_name']
    newid = update['message']['chat']['id']

    ddbb = dts.datos('subibaja.db')
    if not ddbb.findUser(newuser):
        ddbb.addUser(newuser, newid)
        logger.info("Añadiendo user %s" % str(newuser))
    logger.info(ddbb.showUsers())


def ayuda(bot, update):
    update.message.reply_text("""\
- Las oportunidades de compraventa se notifican cada cinco minutos
y se determinan en base a un algoritmo rematadamente simple,
implementado con poco cariño, sin ningún tipo de depuración y reconocidamente erróneo.
- Puede haber varias recomendaciones a la vez o ninguna.
- Recuerda, no hacer nada es hacer algo.
- Yo te muestro el camino; tú pones las piernas.
\
""")


def nada(bot, update):
    respuesta = cw.say(update.message.text)
    update.message.reply_text(respuesta)

    first_name = str(update['message']['chat']['first_name'])
    dicho = str(update.message.text.encode('utf-8'))
    logger.info("%s: %s" % (first_name, dicho))
    logger.info("bot: %s" % str(respuesta.encode('utf-8')))


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)




def main():
    TOKEN = ''
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("ayuda", ayuda))
    dp.add_handler(MessageHandler(Filters.text, nada))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
