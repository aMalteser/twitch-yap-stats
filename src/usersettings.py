import json
import os
import threading
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SettingsData:
    app_id: str = ""
    app_secret: str = ""
    target_channel: str = ""
    excluded_users: set[str] = field(default_factory=set)
    logging: bool = True
    padding: int = 0

    def to_dict(self) -> dict:
        return {
            "App ID": self.app_id,
            "App Secret": self.app_secret,
            "Target Channel": self.target_channel,
            "Excluded Users": list(self.excluded_users),
            "Logging": self.logging,
            "Padding": self.padding,
        }

    def from_dict(self, d: dict):
        self.app_id = d.get("App ID", self.app_id)
        self.app_secret = d.get("App Secret", self.app_secret)
        self.target_channel = d.get("Target Channel", self.target_channel)
        self.excluded_users = set(d.get("Excluded Users", self.excluded_users))
        self.logging = d.get("Logging", self.logging)
        self.padding = d.get("Padding", self.padding)


class UserSettings:
    _instance = None
    _lock = threading.Lock()
    settings: SettingsData
    file_loc: Path

    def __new__(cls) -> "UserSettings":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(UserSettings, cls).__new__(cls)
                cls.settings = SettingsData()
                p = Path(__file__)
                cls.file_loc = p.parents[1] / "user_settings.json"
                cls.load_from_file()

        return cls._instance

    @classmethod
    def save_to_file(cls) -> None:
        with open(cls.file_loc, "w") as fp:
            json.dump(cls.settings.to_dict(), fp, indent=4)

    @classmethod
    def load_from_file(cls) -> None:
        if not os.path.exists(cls.file_loc):
            cls.save_to_file()

        with open(cls.file_loc, "r") as fp:
            try:
                loaded = json.load(fp)
                cls.settings.from_dict(loaded)
            except json.JSONDecodeError:
                cls.save_to_file()

    @classmethod
    def clear_settings(cls) -> None:
        cls.settings = SettingsData()
        if os.path.exists(cls.file_loc):
            os.remove(cls.file_loc)
        cls.save_to_file()
