class UserStats:
    def __init__(self, username: str) -> None:
        self.username: str = username
        self.letter_count: int = 0
        self.word_count: int = 0
        self.messages: int = 0
        self.unique_words: set[str] = set()

    def update_stats(self, words: list[str]) -> None:
        self.letter_count += len(''.join(words))
        self.word_count += len(words)
        self.messages += 1
        self.unique_words.update(set(words))
