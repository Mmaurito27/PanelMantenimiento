import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'entorno.txt')
CONFIG = {}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line:
                key, value = line.strip().split('=', 1)
                CONFIG[key.strip()] = value.strip()

load_config()
