import os
import getpass
from datetime import datetime

LOG_PATH = os.path.join('logs', 'panel.log')
os.makedirs('logs', exist_ok=True)

def log(message: str, level: str = 'INFO') -> None:
    user = getpass.getuser()
    timestamp = datetime.now().strftime('[%Y-%m-%d %H:%M:%S]')
    entry = f"{timestamp} [{level}] ({user}) {message}\n"
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(entry)
