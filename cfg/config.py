import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path('.env'))


def get_env(key, default_value):
    value = os.environ.get(key)
    return value if value is not None else default_value


DEBUG = get_env(key='DEBUG', default_value=True)
BOT_TOKEN = get_env(key='BOT_TOKEN', default_value='42')
PATH_DIR_DATABASE = Path('./db/').absolute()
DATABASE_NAME = 'fortknox.db'
PATH_DATABASE = PATH_DIR_DATABASE / DATABASE_NAME

CALLBACK_CHOOSE_BET = 'CB'
CALLBACK_MAKE_BET = 'MB'
CALLBACK_SEND_DICE = 'SD'
