class UserStats:
    def __init__(self, username):
        self.username = username
        self.letter_count = 0
        self.word_count = 0
        self.messages = 0
        self.unique_words = set()
    
    def update_stats(self, words):
        self.letter_count += len(''.join(words))
        self.word_count += len(words)
        self.messages += 1
        self.unique_words.update(set(words))
    
    def get_average_message_length(self):
        return float(self.letter_count / self.messages)