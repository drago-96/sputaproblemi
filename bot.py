from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters

import datetime

import config
from compile import *


def get_and_compile(session):
    res = get_random_problem(session)
    problema = res.testo
    titolo = res.get_titolo()

    write_problem(problema, titolo)
    err = do_compile()

    return res, err


def sputa(bot, update, **kwargs):
    print(update.message.chat.id)
    session = Session()
    problem, errors = get_and_compile(session)
    kwargs['chat_data']['problema'] = problem
    kwargs['chat_data']['DBsess'] = session

    if errors:
        update.message.reply_text(problem.testo)
        return 2

    update.message.reply_photo(photo=open('build/problema.jpg','rb'))
    return 1

def upload(bot, update, **kwargs):
    p = kwargs['chat_data']['problema']
    sess = kwargs['chat_data']['DBsess']
    oggi = datetime.date.today()
    p.dato = oggi
    sess.add(p)
    sess.commit()
    sess.close()

    upload_IG()

    update.message.reply_text("Problema caricato!")
    return ConversationHandler.END

def rifiuta(bot, update, **kwargs):
    kwargs['chat_data']['DBsess'].close()
    return ConversationHandler.END

def modifica(bot, update, **kwargs):
    update.message.reply_text(kwargs['chat_data']['problema'].testo)
    update.message.reply_text("Mandami la versione corretta!")
    return 2

def scrivi(bot, update, **kwargs):
    text = update.message.text
    p = kwargs['chat_data']['problema']
    sess = kwargs['chat_data']['DBsess']

    write_problem(text, p.get_titolo())
    err = do_compile()
    if err:
        update.message.reply_text("Compilazione fallita! Riprova")
        return 2

    p.testo = text
    sess.add(p)
    sess.commit()

    update.message.reply_photo(photo=open('build/problema.jpg','rb'))
    return 1

def cancel(bot, update, **kwargs):
    kwargs['chat_data']['DBsess'].close()
    return ConversationHandler.END


def hello(bot, update):
    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))


updater = Updater(config.token)

updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('sputa', sputa))

conv_handler = ConversationHandler(
    entry_points = [CommandHandler('problema', sputa, pass_chat_data=True)],
    states = {
        1: [CommandHandler('si', upload, pass_chat_data=True),
            CommandHandler('no', rifiuta, pass_chat_data=True),
            CommandHandler('modifica', modifica, pass_chat_data=True)],
        2: [MessageHandler(Filters.text, scrivi, pass_chat_data=True)]
    },
    fallbacks = [CommandHandler('cancel', cancel)]
)

updater.dispatcher.add_handler(conv_handler)

updater.start_polling()
updater.idle()
