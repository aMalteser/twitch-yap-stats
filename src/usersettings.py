import os
import json
import threading


class UserSettings:
    _instance = None
    _lock = threading.Lock()
    settings: dict
    file_loc: os.path

    def __new__(cls) -> 'UserSettings':
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(UserSettings, cls).__new__(cls)
                cls.settings = {
                    'App ID': '',
                    'App Secret': '',
                    'Target Channel': '',
                    'Excluded Users': set(),
                    'Logging': True,
                    'Padding': 0
                }
                cls.file_loc = os.path.join(os.path.abspath(__file__), os.pardir, os.pardir, 'user_settings.json')
                cls.load_from_file(cls)

        return cls._instance

    def save_to_file(cls) -> None:
        cls.settings['Excluded Users'] = list(cls.settings['Excluded Users'])
        with open(cls.file_loc, 'w') as fp:
            json.dump(cls.settings, fp, indent=4)
        cls.settings['Excluded Users'] = set(cls.settings['Excluded Users'])

    def load_from_file(cls) -> None:
        if not os.path.exists(cls.file_loc):
            cls.save_to_file(cls)

        with open(cls.file_loc, 'r') as fp:
            try:
                cls.settings.update(json.load(fp))
                cls.settings['Excluded Users'] = set(cls.settings['Excluded Users'])
            except json.JSONDecodeError:
                cls.save_to_file(cls)
