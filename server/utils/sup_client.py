from supabase import create_client, Client
import os 
from dotenv import load_dotenv

load_dotenv()

SUP_URL = os.getenv("SUP_URL")
SUP_KEY = os.getenv("SUP_KEY")

sb: Client = create_client(SUP_URL, SUP_KEY)
