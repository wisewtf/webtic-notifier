import telebot
import db
import tools
import schedule
import time
import threading
import theaters
import webtic
import anteo
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

tools.logger("Started bot")

bot = telebot.TeleBot(tools.configurator('telegram', 'token'))

THEATERS_PICKLE_FILENAME = 'theater_date.pickle'
THEATERS_PICKLE_PATH = Path(THEATERS_PICKLE_FILENAME)

if not THEATERS_PICKLE_PATH.is_file():
    tools.logger('Creo cetriolo')
    tools.pickle_initializer(THEATERS_PICKLE_FILENAME)
    theaters.theater_updater()
else:
    pass

saved_date = tools.unpickler(THEATERS_PICKLE_FILENAME)
two_weeks_old_date = datetime.now() - timedelta(weeks=2)

if saved_date <= two_weeks_old_date:
    tools.logger('Aggiorno lista dei cinema')
    theaters.theater_updater()
    tools.pickle_initializer(THEATERS_PICKLE_FILENAME)
else:
    pass

@bot.message_handler(commands=['tl'])
def theater_list(message):
    if len(tools.command_argument(message)) == 2:
        list_of_cinemas = []
        for cinema in db.find_theater_by_province(tools.command_argument(message)[1]):
            if len(tools.command_argument(message)[1]) > 2:
                list_of_cinemas = []
            else:
                list_of_cinemas.append((cinema['Description'], cinema['LocalId']))
        if not list_of_cinemas:
            bot.reply_to(message, 
                         f'Nessuna provincia "{tools.command_argument(message)[1]}" trovata',  parse_mode='HTML')
        else:
            composed_message = ""
            for cinema in list_of_cinemas:
                cinema_name, cinema_id = cinema
                composed_message += f"\n{cinema_name.title()} (<code>{cinema_id}</code>)"
            bot.reply_to(message, composed_message, parse_mode='HTML')
    elif len(tools.command_argument(message)) > 1:
        bot.reply_to(message, 'Questo comando accetta un solo argomento.')
    else:
        bot.reply_to(message, 'Specifica il codice provincia.')
            
@bot.message_handler(commands=['dbc'])
def db_cleanup(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    chat_member = bot.get_chat_member(chat_id, user_id)
    is_admin = chat_member.status in ["administrator", "creator"]
    
    if is_admin:
        db.database_cleanup()
    else:
        bot.reply_to(message, "Comando disponibile solo per amministratori del gruppo.", parse_mode='HTML')
        
# @bot.message_handler(commands=['track'])
# def track_event(message):
#     if len(tools.command_argument(message)) == 2:
#         if db.track_movie(int(tools.command_argument(message)[1])) != 0:
#             bot.reply_to(message, f"Terrò traccia del film con ID: <code>{tools.command_argument(message)[1]}</code>", parse_mode='HTML')
#         else:
#             bot.reply_to(message, "Film già tracciato o ID invalido.")
            
# @bot.message_handler(commands=['untrack'])
# def untrack_event(message):
#     if len(tools.command_argument(message)) == 2:
#         if db.untrack_movie(int(tools.command_argument(message)[1])) != 0:
#             bot.reply_to(message, f"Rimosso tracciamento da film con ID: <code>{tools.command_argument(message)[1]}</code>", parse_mode='HTML')
#         else:
#             bot.reply_to(message, "Film non tracciato o ID invalido.")
            
@bot.message_handler(commands=['info'])
def movie_info(message):
    if len(tools.command_argument(message)) >= 2:
        argument = ' '.join(tools.command_argument(message)[1:])
        tools.logger(f"Cerco info su: {argument}")
        tools.find_movie_info(urllib.parse.quote(argument), argument)


bot.remove_webhook()
bot.set_my_commands([
    telebot.types.BotCommand("tl", "Trova i cinema presenti in webtic, per ogni provincia. (/tl MI)"),
    telebot.types.BotCommand("dbc", "Pulizia del database."),
    # telebot.types.BotCommand("track", "Tieni traccia degli aggiornamenti di un film. (/track ID)"),
    telebot.types.BotCommand("untrack", "Rimuovi tracciamento da un film. (/untrack ID)"),
    telebot.types.BotCommand("info", "Trova informazioni su un film (/info TITOLO)")
])

def schedules():

    schedule.every(1).weeks.do(db.database_cleanup)
    schedule.every(15).minutes.do(webtic.findnew)
    schedule.every(15).minutes.do(lambda: anteo.findnew(tools.generate_today()))
    schedule.every(30).minutes.do(lambda: anteo.findnew(tools.generate_next_month_date()))
    schedule.every(30).minutes.do(lambda: anteo.findnew(tools.generate_two_month_ahead_date()))
    while True:
        schedule.run_pending()
        time.sleep(1)
        
threading.Thread(target=schedules, daemon=True).start()

bot.infinity_polling()