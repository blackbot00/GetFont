# config.py
import os

class Config:
    API_ID = int(os.environ.get("API_ID", "0"))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
    
    # Bot Info
    BOT_NAME = "Font Changer Bot"
    BOT_VERSION = "2.0"
    
    # MongoDB (Optional - for stats)
    MONGO_URI = os.environ.get("MONGO_URI", None)
