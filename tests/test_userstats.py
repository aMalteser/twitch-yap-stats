import sys
import unittest

sys.path.append(__file__ + "/../../src")

from userstats import UserStats


class TestUserStats(unittest.TestCase):
    def setUp(self) -> None:
        self.test_user1 = UserStats("test1")
        self.test_user1.letter_count = 100
        self.test_user1.word_count = 10
        self.test_user1.messages = 10
        self.test_user1.unique_words = {"hello", "world"}

    def test_update_stats(self):
        self.test_user1.update_stats(["hello", "world", "bye"])
        self.assertEqual(self.test_user1.letter_count, 113)
        self.assertEqual(self.test_user1.word_count, 13)
        self.assertEqual(self.test_user1.messages, 11)
        self.assertEqual(self.test_user1.unique_words, {"hello", "world", "bye"})

    def test_update_stats_empty(self):
        self.test_user1.update_stats([])
        self.assertEqual(self.test_user1.messages, 10)

    def test_new_user(self):
        test_user2 = UserStats("test2")
        self.assertEqual(
            [
                test_user2.letter_count,
                test_user2.word_count,
                test_user2.messages,
                test_user2.unique_words,
            ],
            [0, 0, 0, set()],
        )
