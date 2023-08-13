import decimal
import json
import os
import re
import datetime
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class SettingsFileManager:
    @staticmethod
    def read_settings():
        with open(resource_path('settings'), 'r') as f:
            settings = json.load(f)
        return settings

    @staticmethod
    def write_settings(settings):
        with open(resource_path('settings'), 'w') as f:
            json.dump(settings, f)


class TypeIdentifier:
    @staticmethod
    def identify_parse(value):
        if type(value) == bool:
            return value
        if not value:
            return None
        elif value == 'None':
            return None
        elif type(value) == int:
            return value
        elif type(value) == datetime.date:
            return value.strftime('%d.%m.%Y')
        elif type(value) == decimal.Decimal:
            return value
        elif all(re.match(r'\d+', i) for i in value):
            return int(value)
        else:
            return str(value)
