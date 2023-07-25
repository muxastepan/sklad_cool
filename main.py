from frames import MainFrame
import json


class App:
    def __init__(self):
        settings = self._read_settings()
        self.main_frame = MainFrame(
            width=settings["window_settings"]["width"],
            height=settings["window_settings"]["height"],
            db_name=settings["sql_settings"]["db_name"],
            host=settings["sql_settings"]["host"],
            port=settings["sql_settings"]["port"],
            user_name=settings["sql_settings"]["user_name"],
            password=settings["sql_settings"]["password"]
        )

    def _read_settings(self):
        with open('settings', 'r') as f:
            s = json.load(f)
        return s

    def run(self):
        self.main_frame.show()


if __name__ == '__main__':
    app = App()
    app.run()
