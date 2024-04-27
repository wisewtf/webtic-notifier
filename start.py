import tools
import theaters
import webtic
import anteo
from pathlib import Path
from datetime import timedelta, datetime

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

webtic.findnew()
anteo.findnew()