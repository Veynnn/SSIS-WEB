
from dotenv import load_dotenv
from os import getenv

load_dotenv() 

DB_HOST = getenv("DB_HOST")
DB_USER = getenv("DB_USER")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_NAME = getenv("DB_NAME")
SECRET_KEY = getenv("SECRET_KEY")
CLOUD_NAME = getenv("CLOUD_NAME")
API_KEY = getenv("API_KEY")
API_SECRET = getenv("API_SECRET")


