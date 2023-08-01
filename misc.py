import json
import re
import datetime


class SettingsFileManager:
    @staticmethod
    def read_settings(path):
        with open(path, 'r') as f:
            settings = json.load(f)
        return settings

    @staticmethod
    def write_settings(path, settings):
        with open(path, 'w') as f:
            json.dump(settings, f)


class TypeIdentifier:
    @staticmethod
    def identify_parse(value):
        if not value:
            return None
        elif type(value) == int:
            return value
        elif type(value) == datetime.date:
            return value
        elif all(re.match(r'\d{4}-\d{2}-\d{2}', i) for i in value):
            return datetime.datetime.strptime(value, '%d.%m.%Y')
        elif all(re.match(r'\d+', i) for i in value):
            return int(value)
        else:
            return str(value)

