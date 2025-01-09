import json
import os
import sys
import unittest

sys.path.append(__file__ + "/../../src")

from usersettings import UserSettings


class UserSettingsTest(unittest.TestCase):
    def setUp(self) -> None:
        original = os.path.abspath(__file__ + "/../../user_settings.json")
        backup = os.path.abspath(__file__ + "/../../user_settings.json.bak")
        if os.path.exists(original) and not os.path.exists(backup):
            os.rename(original, backup)
        else:
            os.remove(original)
        UserSettings._instance = None

    def tearDown(self):
        original = os.path.abspath(__file__ + "/../../user_settings.json")
        backup = os.path.abspath(__file__ + "/../../user_settings.json.bak")
        if os.path.exists(original):
            os.remove(original)
        os.rename(backup, original)
        UserSettings._instance = None

    def test_singleton(self) -> None:
        us1 = UserSettings()
        self.assertTrue(us1.settings["App ID"] == "")

        us2 = UserSettings()
        self.assertEqual(us1, us2)

    def test_changed_settings_apply_to_all(self) -> None:
        us1 = UserSettings()
        self.assertTrue(us1.settings["App ID"] == "")

        us2 = UserSettings()
        us1.settings["App ID"] = "123"
        self.assertEqual(us2.settings["App ID"], "123")

    def test_save_to_file(self) -> None:
        us = UserSettings()
        self.assertTrue(us.settings["App ID"] == "")

        us.settings["App ID"] = "123"
        us.save_to_file()
        with open(os.path.abspath(__file__ + "/../../user_settings.json"), "r") as f:
            saved = json.load(f)
        self.assertEqual(saved["App ID"], "123")

    def test_load_from_file_overwrites_settings(self) -> None:
        us = UserSettings()
        self.assertTrue(us.settings["App ID"] == "")

        us.settings["App ID"] = "123"
        us.save_to_file()
        self.assertEqual(us.settings["App ID"], "123")
        us.settings["App ID"] = "456"
        self.assertEqual(us.settings["App ID"], "456")
        us.load_from_file()
        self.assertEqual(us.settings["App ID"], "123")

    def test_load_from_file_creates_file_if_not_exists(self) -> None:
        us = UserSettings()
        self.assertTrue(us.settings["App ID"] == "")

        us.load_from_file()
        self.assertTrue(
            os.path.exists(os.path.abspath(__file__ + "/../../user_settings.json"))
        )
