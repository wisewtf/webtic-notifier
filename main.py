import telebot
import db
import tools
import schedule
import time
import threading

bot = telebot.TeleBot(tools.configurator('telegram', 'token'))

@bot.message_handler(commands=['tl'])
def theater_list(message):
    message_parts = message.text.split()
    if len(message_parts) > 1:
        provinceid = message_parts[1]
        list_of_cinemas = []
        for cinema in db.find_theater_by_province(provinceid):
            list_of_cinemas.append((cinema['Description'], cinema['LocalId']))
        if not list_of_cinemas:
            bot.reply_to(message, f'Nessuna provincia {provinceid.upper()} trovata')  # noqa: E501
        else:
            composed_message = ""
            for cinema in list_of_cinemas:
                cinema_name, cinema_id = cinema
                composed_message += f"\n{cinema_name.title()} (<code>{cinema_id}</code>)"  # noqa: E501
            bot.reply_to(message, composed_message, parse_mode='HTML')

    else:
        bot.reply_to(message, 'Non hai specificato il codice provincia!')

bot.remove_webhook()
bot.set_my_commands([
    telebot.types.BotCommand("tl", "Lista i cinema presenti in webtic (e i loro ID), per provincia. (/tl MI)"),  # noqa: E501
])

def schedule_db_cleanup():

    schedule.every(1).weeks.do(db.database_cleanup)

    while True:
        schedule.run_pending()
        time.sleep(1)
        
threading.Thread(target=schedule_db_cleanup, daemon=True).start()

bot.polling()