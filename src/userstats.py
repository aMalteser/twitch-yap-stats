import math

class UserStats:
    def __init__(self, username) -> None:
        self.username = username
        self.letter_count = 0
        self.word_count = 0
        self.messages = 0
        self.unique_words = set()
    

    def update_stats(self, words) -> None:
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
        scalar = len(self.unique_words) ** 0.5
        uniq_word_ratio = (len(self.unique_words) ** 1.2) / self.messages
        ln_avg_letters = math.log(self.get_average_message_length())
        return scalar * (uniq_word_ratio + ln_avg_letters)