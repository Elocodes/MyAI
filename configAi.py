import os
import openai
import sys

#v upgrade sqlite to  >3.0 version
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

sys.path.append('../..')

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = os.environ['OPENAI_API_KEY']
