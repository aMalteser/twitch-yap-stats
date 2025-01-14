import json
import os
import threading
from pathlib import Path


class UserSettings:
    _instance = None
    _lock = threading.Lock()
    settings: dict[str, str | set[str] | list[str] | bool | int]
    file_loc: Path

    def __new__(cls) -> "UserSettings":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(UserSettings, cls).__new__(cls)
                cls.settings = cls.set_default_settings()
                p = Path(__file__)
                cls.file_loc = p.parents[1] / "user_settings.json"
                cls.load_from_file()

        return cls._instance

    @classmethod
    def save_to_file(cls) -> None:
        cls.settings["Excluded Users"] = list(cls.settings["Excluded Users"])
        with open(cls.file_loc, "w") as fp:
            json.dump(cls.settings, fp, indent=4)
        cls.settings["Excluded Users"] = set(cls.settings["Excluded Users"])

    @classmethod
    def load_from_file(cls) -> None:
        if not os.path.exists(cls.file_loc):
            cls.save_to_file()

        with open(cls.file_loc, "r") as fp:
            try:
                cls.settings.update(json.load(fp))
                cls.settings["Excluded Users"] = set(cls.settings["Excluded Users"])
            except json.JSONDecodeError:
                cls.save_to_file()

    @classmethod
    def set_default_settings(cls) -> dict:
        return {
            "App ID": "",
            "App Secret": "",
            "Target Channel": "",
            "Excluded Users": set(),
            "Logging": True,
            "Padding": 0,
        }

    @classmethod
    def clear_settings(cls) -> None:
        cls.settings = cls.set_default_settings()
        if os.path.exists(cls.file_loc):
            os.remove(cls.file_loc)
        cls.save_to_file()
