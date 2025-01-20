# app_config.py
import json
import os

CONFIG_FILE = "app_settings.json"

def load_config():
    """
    Загружает словарь конфигурации из JSON-файла.
    Если файла нет или он пустой, возвращается пустой словарь.
    """
    if not os.path.exists(CONFIG_FILE):
        return {}

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка чтения конфигурации: {e}")
        return {}

def save_config(config_dict):
    """
    Сохраняет словарь конфигурации в JSON-файл.
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_dict, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Ошибка сохранения конфигурации: {e}")
