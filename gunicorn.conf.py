import os
from dotenv import read_dotenv

env = os.path.join(os.getcwd(), ".env")
print('env', env)
if os.path.exists(env):
    read_dotenv(env)
