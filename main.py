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
    
    composed_message = []
    
    if len(tools.command_argument(message)) >= 2:
        argument = ' '.join(tools.command_argument(message)[1:])
        for query_result in db.find_movie_by_title(argument):
            matched_cinema_id = re.search(tools.CINEMA_ID_PATTERN, query_result)
            if matched_cinema_id:
                cinema_id = matched_cinema_id.group(1)
                cinema_name = theaters.theater_finder(int(cinema_id), "Description")
                composed_message.append(f"{cinema_name} (<code>{cinema_id}</code>)\n")
        unique_theaters = []
        for found_theater in composed_message:
            if found_theater not in unique_theaters:
                unique_theaters.append(found_theater)
        if unique_theaters:
            bot.reply_to(message, f"'<code>{argument.title()}</code>' è disponibile nei seguenti cinema da te configurati:\n\n{''.join(set(unique_theaters))}", parse_mode='HTML')  # noqa: E501
        else:
            bot.reply_to(message, f"'<code>{argument.title()}</code>' non trovato.", parse_mode='HTML')  # noqa: E501
            
@bot.message_handler(commands=['dbc'])
def db_cleanup(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    chat_member = bot.get_chat_member(chat_id, user_id)
    is_admin = chat_member.status in ["administrator", "creator"]
    
    if is_admin:
        db.database_cleanup()
    else:
        bot.reply_to(message, "Comando disponibile solo per amministratori del gruppo.", parse_mode='HTML')  # noqa: E501


bot.remove_webhook()
bot.set_my_commands([
    telebot.types.BotCommand("tl", "Trova i cinema presenti in webtic, per ogni provincia. (/tl MI)"),  # noqa: E501
    telebot.types.BotCommand("fm", "Trova i film disponibili nei cinema configurati. (/tl Harry Potter)"),  # noqa: E501
    telebot.types.BotCommand("dbc", "Pulizia del database (amministratori)")  # noqa: E501
])

def schedule_db_cleanup():

    schedule.every(1).weeks.do(db.database_cleanup)

    while True:
        schedule.run_pending()
        time.sleep(1)
        
threading.Thread(target=schedule_db_cleanup, daemon=True).start()

bot.polling()