import dotenv
import os
from tplinkipc import TPLinkIPC

dotenv.load_dotenv()
username = os.getenv("IPC_USERNAME")
password = os.getenv("IPC_PASSWORD")
url = os.getenv("IPC_BASE_URL")

camera1 = TPLinkIPC(url, username, password)