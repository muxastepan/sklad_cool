import json


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
