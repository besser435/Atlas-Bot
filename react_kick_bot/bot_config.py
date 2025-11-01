import logging
import os
import sys
from datetime import datetime, timezone
os.chdir(os.path.dirname(os.path.abspath(__file__)))


# Config
BOT_TOKEN = ""
GUILD_ID = 0
CHANNEL_ID = 0
MESSAGE_IDS = [
    0
]

DRY_RUN = True
log_level = logging.DEBUG

EXEMPT_DATE = datetime(2025, 10, 13, tzinfo=timezone.utc)
# Any members who joined after this will be exempt from the reaction check
EXEMPT_USER_IDS = [
    0
]
# Any user IDs will not be kicked


# Logger
sys.path.append("../")  
# Jank to get logger in parent directory so it doesn't have to be in each directory
from diet_logger import setup_logger
LOG_FILE = "../logs/react_kick_bot.log"
log = setup_logger(LOG_FILE, log_level)
