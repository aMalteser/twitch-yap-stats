import json
import os
import sys
import unittest

sys.path.append(__file__ + "/../../src")

from usersettings import UserSettings


def preserve_settings(func):
    def wrapper(*args, **kwargs):
        original = os.path.abspath(__file__ + "/../../user_settings.json")
        backup = os.path.abspath(__file__ + "/../../user_settings.json.bak")
        os.rename(original, backup)
        try:
            func(*args, **kwargs)
        finally:
            if os.path.exists(original):
                os.remove(original)
            os.rename(backup, original)

    return wrapper


class UserSettingsTest(unittest.TestCase):
    def test_singleton(self) -> None:
        us1 = UserSettings()
        us2 = UserSettings()
        self.assertEqual(us1, us2)

    @preserve_settings
    def test_changed_settings_apply_to_all(self) -> None:
        us1 = UserSettings()
        us2 = UserSettings()
        us1.settings["App ID"] = "123"
        self.assertEqual(us2.settings["App ID"], "123")

    @preserve_settings
    def test_save_to_file(self) -> None:
        us = UserSettings()
        us.settings["App ID"] = "123"
        us.save_to_file()
        with open(os.path.abspath(__file__ + "/../../user_settings.json"), "r") as f:
            saved = json.load(f)
        self.assertEqual(saved["App ID"], "123")

    @preserve_settings
    def test_load_from_file_overwrites_settings(self) -> None:
        us = UserSettings()
        us.settings["App ID"] = "123"
        us.save_to_file()
        self.assertEqual(us.settings["App ID"], "123")
        us.settings["App ID"] = "456"
        self.assertEqual(us.settings["App ID"], "456")
        us.load_from_file()
        self.assertEqual(us.settings["App ID"], "123")

    @preserve_settings
    def test_load_from_file_creates_file_if_not_exists(self) -> None:
        us = UserSettings()
        us.load_from_file()
        self.assertTrue(
            os.path.exists(os.path.abspath(__file__ + "/../../user_settings.json"))
        )
