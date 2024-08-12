from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


DB_instance = None

def Db_connection():
    global DB_instance
    if DB_instance != None:
        return DB_instance
    else:
        DB_instance  = MongoClient(os.getenv('MONGODB_URI'))
        return DB_instance



    