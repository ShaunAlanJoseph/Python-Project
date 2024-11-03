from os import getenv
from dotenv import load_dotenv

load_dotenv()

DISCORD_API_TOKEN = getenv("DISCORD_API_TOKEN")
ADMIN_CHANNEL_ID = int(getenv("ADMIN_CHANNEL_ID") or 0)

Gemini_API_Key = getenv("Gemini_API_Key")