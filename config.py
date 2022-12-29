import os
import dotenv

dotenv.load_dotenv()

def get_token():
  return str(os.getenv("TOKEN"))


def get_key():
  return os.getenv('KEY')
