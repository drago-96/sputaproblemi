from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters

import datetime

import config
from compile import *

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def get_and_compile(session, tipo, path):
    res = get_random_problem(session, diff=tipo)
    problema = res.testo
    titolo = res.get_titolo()

    write_problem(problema, titolo)
    err = do_compile(path)
    if err:
        logging.warning("Compilazione fallita!\n{}".format(problema))

    return res, err


def sputa(bot, update, **kwargs):
    session = Session()
    try:
        tipo = int(kwargs['args'][0])
    except:
        tipo = (datetime.date.today().weekday()+1)%7
    logging.info("Richiesta ricevuta da {}; difficoltà: {}".format(update.message.chat.id, tipo))

    timestamp = datetime.datetime.now().time().replace(microsecond=0).isoformat()
    path = timestamp+".jpg"
    problem, errors = get_and_compile(session, tipo, path)
    kwargs['chat_data']['problema'] = problem
    kwargs['chat_data']['DBsess'] = session
    kwargs['chat_data']['path'] = path

    if errors:
        update.message.reply_text(problem.testo)
        return 2

    update.message.reply_photo(photo=open('build/'+path,'rb'))
    return 1

def my_upload(bot, job):
    upload_IG(job.name)
    bot.send_message(chat_id=job.context, text='Problema {} caricato!'.format(job.name))


def upload(bot, update, job_queue, **kwargs):
    p = kwargs['chat_data']['problema']
    path = kwargs['chat_data']['path']
    sess = kwargs['chat_data']['DBsess']
    oggi = datetime.date.today()
    p.dato = oggi
    sess.add(p)
    sess.commit()
    sess.close()

    job_queue.run_once(my_upload, datetime.time(0,14,0), context=update.message.chat_id, name=path)

    update.message.reply_text("Problema programmato con nome {}".format(path))
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
    path = kwargs['chat_data']['path']

    write_problem(text, p.get_titolo())
    err = do_compile(path)
    if err:
        update.message.reply_text("Compilazione fallita! Riprova")
        return 2

    p.testo = text
    sess.add(p)
    sess.commit()

    update.message.reply_photo(photo=open('build/'+path,'rb'))
    return 1

def cancel(bot, update, **kwargs):
    kwargs['chat_data']['DBsess'].close()
    return ConversationHandler.END

def elimina(bot, update, **kwargs):
    try:
        nome = kwargs['args'][0]
    except:
        update.message.reply_text("Devi darmi l'id del problema!")
        return
    job_queue = kwargs['job_queue']
    cnt = 0
    for job in job_queue.get_jobs_by_name(nome):
        job.schedule_removal()
        cnt += 1
    update.message.reply_text("Ho cancellato {} problema".format(cnt))



updater = Updater(config.token)


updater.dispatcher.add_handler(CommandHandler('sputa', sputa))

conv_handler = ConversationHandler(
    entry_points = [CommandHandler('problema', sputa, pass_chat_data=True, pass_args=True)],
    states = {
        1: [CommandHandler('si', upload, pass_chat_data=True, pass_job_queue=True),
            CommandHandler('no', rifiuta, pass_chat_data=True),
            CommandHandler('modifica', modifica, pass_chat_data=True)],
        2: [MessageHandler(Filters.text, scrivi, pass_chat_data=True)]
    },
    fallbacks = [CommandHandler('cancel', cancel, pass_chat_data=True)]
)

updater.dispatcher.add_handler(CommandHandler('elimina', elimina, pass_job_queue=True, pass_args=True))

updater.dispatcher.add_handler(conv_handler)

updater.start_polling()
updater.idle()
