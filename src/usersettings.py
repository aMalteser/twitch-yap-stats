import os
import json

class UserSettings:
    _instance = None
    settings: dict
    file_loc: os.path
    defaults: bool

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserSettings, cls).__new__(cls)
            cls.file_loc = os.path.join(os.path.abspath(__file__), os.pardir, 'settings.json')
            cls.load_from_file()

        return cls._instance
    

    def save_to_file(cls) -> None:
        with open(cls.file_loc, 'w') as fp:
            json.dump(cls.settings, fp, sort_keys=True, indent=4)
        cls.defaults = False
    

    def load_from_file(cls) -> None:
        if os.path.exists(cls.file_loc):
            cls.create_defaults_file()
            cls.defaults = False
        
        with open(cls.file_loc, 'r') as fp:
            cls.settings = json.load(fp)
        cls.settings['Excluded Users'] = set(cls.settings['Excluded Users'])

    def create_defaults_file(cls) -> None:
        cls.settings = {
            'App ID': '',
            'App Secret': '',
            'Target Channel':'',
            'Excluded Users': []
        }
        cls.save_to_file()