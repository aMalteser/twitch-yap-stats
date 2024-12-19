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
    

    def get_average_message_length(self) -> float:
        return float(self.letter_count / self.messages)
    
    '''
    Calculate 'yap' factor based on collected stats, many magic numbers are found here
    '''
    def calc_yap_factor(self) -> float:
        scalar = self.letter_count ** 0.75
        uniq_word_ratio = (len(self.unique_words) ** 1.2) / self.messages
        return scalar * (uniq_word_ratio + self.get_average_message_length())