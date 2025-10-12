import logging
import os
import sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# Config
BOT_TOKEN = ""
GUILD_ID = 0
CHANNEL_ID = 0
MESSAGE_IDS = [
    0,
    0
]



# Logger
sys.path.append("../")  
# Jank to get logger in parent directory so it doesn't have to be in eac directory
from diet_logger import setup_logger
log_level = logging.DEBUG

LOG_FILE = "../logs/react_kick_bot.log"
log = setup_logger(LOG_FILE, log_level)
