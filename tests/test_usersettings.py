import json
import os
import unittest

from yap_stats.usersettings import SettingsData, UserSettings


class TestUserSettings(unittest.TestCase):
    def setUp(self) -> None:
        self.us = UserSettings()
        self.original = os.path.abspath(self.us.file_loc)
        self.backup = os.path.abspath(self.original + ".bak")

        if os.path.exists(self.original):
            if os.path.exists(self.backup):
                os.remove(self.original)
            else:
                os.rename(self.original, self.backup)
        self.us.clear_settings()
        self.us.save_to_file()

    def tearDown(self):
        if os.path.exists(self.original):
            os.remove(self.original)
        if os.path.exists(self.backup):
            os.rename(self.backup, self.original)

    def test_singleton(self) -> None:
        us1 = UserSettings()
        self.assertTrue(us1.settings.app_id == "")

        us2 = UserSettings()
        self.assertEqual(us1, us2)

    def test_changed_settings_apply_to_all(self) -> None:
        us1 = UserSettings()
        self.assertTrue(us1.settings.app_id == "")

        us2 = UserSettings()
        us1.settings.app_id = "123"
        self.assertEqual(us2.settings.app_id, "123")

    def test_save_to_file(self) -> None:
        us = UserSettings()
        self.assertTrue(us.settings.app_id == "")

        us.settings.app_id = "123"
        us.save_to_file()
        with open(os.path.abspath(us.file_loc), "r") as f:
            saved = json.load(f)
        self.assertEqual(saved["App ID"], "123")

    def test_load_from_file_overwrites_settings(self) -> None:
        us = UserSettings()
        self.assertTrue(us.settings.app_id == "")

        us.settings.app_id = "123"
        us.save_to_file()
        self.assertEqual(us.settings.app_id, "123")
        us.settings.app_id = "456"
        self.assertEqual(us.settings.app_id, "456")
        us.load_from_file()
        self.assertEqual(us.settings.app_id, "123")

    def test_load_from_file_creates_file_if_not_exists(self) -> None:
        us = UserSettings()
        self.assertTrue(us.settings.app_id == "")
        self.assertTrue(os.path.exists(us.file_loc))
        os.remove(us.file_loc)

        us.load_from_file()
        self.assertTrue(os.path.exists(os.path.abspath(us.file_loc)))


class TestSettingsData(unittest.TestCase):
    def test_empty_init(self) -> None:
        sd = SettingsData()
        self.assertEqual(
            [
                sd.app_id,
                sd.app_secret,
                sd.target_channel,
                sd.excluded_users,
                sd.logging,
                sd.padding,
            ],
            ["", "", "", set(), True, 0],
        )

    def test_to_dict_keys(self):
        sd = SettingsData()
        self.assertEqual(
            list(sd.to_dict().keys()),
            [
                "App ID",
                "App Secret",
                "Target Channel",
                "Excluded Users",
                "Logging",
                "Padding",
            ],
        )

    def test_to_dict_excluded_users_is_list(self):
        sd = SettingsData()
        sd.excluded_users = {"a", "bcd", "ef"}
        d = sd.to_dict()
        self.assertTrue(type(d["Excluded Users"]), list)

    def test_all_dict_values_are_serialisable(self):
        sd = SettingsData()
        d = sd.to_dict()
        try:
            json.dumps(d)
        except TypeError:
            self.fail("Unserialisable type found")

    def test_from_empty_dict_no_overwrite(self):
        sd = SettingsData("123", "456", "abc", {"def", "ghi"}, False, 1)
        d = dict()
        sd.from_dict(d)
        self.assertEqual(
            [
                sd.app_id,
                sd.app_secret,
                sd.target_channel,
                sd.excluded_users,
                sd.logging,
                sd.padding,
            ],
            ["123", "456", "abc", {"def", "ghi"}, False, 1],
        )

    def test_dict_with_invalid_keys(self):
        sd = SettingsData()
        sd.app_id = "123"
        d = {"App ID": "456", "Not A Key": "789"}
        sd.from_dict(d)
        self.assertEqual(
            [
                sd.app_id,
                sd.app_secret,
                sd.target_channel,
                sd.excluded_users,
                sd.logging,
                sd.padding,
            ],
            ["456", "", "", set(), True, 0],
        )
