import telebot
import db
import tools
import schedule
import time
import threading
import re
import theaters

bot = telebot.TeleBot(tools.configurator('telegram', 'token'))

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
                         f'Nessuna provincia "{tools.command_argument(message)[1]}" trovata',  parse_mode='HTML')  # noqa: E501
        else:
            composed_message = ""
            for cinema in list_of_cinemas:
                cinema_name, cinema_id = cinema
                composed_message += f"\n{cinema_name.title()} (<code>{cinema_id}</code>)"  # noqa: E501
            bot.reply_to(message, composed_message, parse_mode='HTML')
    elif len(tools.command_argument(message)) > 1:
        bot.reply_to(message, 'Questo comando accetta un solo argomento.')
    else:
        bot.reply_to(message, 'Specifica il codice provincia.')
        
@bot.message_handler(commands=['fm'])
def find_movie(message):
    
    composed_message = ''
    
    if len(tools.command_argument(message)) >= 3:
        argument = ' '.join(tools.command_argument(message)[1:])
        print('argument:', argument)
        for query_result in db.find_movie_by_title(argument):
            matched_cinema_id = re.search(tools.CINEMA_ID_PATTERN, query_result)
            print('matched cinema id:', matched_cinema_id)
            if matched_cinema_id:
                cinema_id = matched_cinema_id.group(1)
                cinema_name = theaters.theater_finder(int(cinema_id), "Description")
                composed_message += f"{cinema_name} (<code>{cinema_id}</code>)\n"  # noqa: E501
        bot.reply_to(message, composed_message, parse_mode='HTML')
    else:
        print('fuckoff')


bot.remove_webhook()
bot.set_my_commands([
    telebot.types.BotCommand("tl", "Lista i cinema presenti in webtic (e i loro ID), per provincia. (/tl MI)"),  # noqa: E501
    telebot.types.BotCommand("fm", "Trova i film prenotabili da i cinema configurati. /tl Harry Potter")  # noqa: E501
])

def schedule_db_cleanup():

    schedule.every(1).weeks.do(db.database_cleanup)

    while True:
        schedule.run_pending()
        time.sleep(1)
        
threading.Thread(target=schedule_db_cleanup, daemon=True).start()

bot.polling()