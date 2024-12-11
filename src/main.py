from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage
import asyncio
from dotenv import load_dotenv
import os
from userstats import UserStats
from collections import defaultdict
import pandas as pd
import numpy as np
import scipy.stats as stats
from tabulate import tabulate
from datetime import datetime
import pytz


load_dotenv()
APP_ID = os.getenv('APP_ID')
APP_SECRET = os.getenv('APP_SECRET')
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL')
EXCLUDED_USERS = set(os.getenv('EXCLUDED_USERS').split(','))

USER_SCOPE = [AuthScope.CHAT_READ]

YAP_STATS = {}
WORDS_COUNT = defaultdict(int)

START_TIME = str()


def save_df(df, name):
    abs_path = os.path.abspath(__file__)
    output_path = os.path.join(os.path.dirname(abs_path), os.pardir, 'output', TARGET_CHANNEL)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        
    # UTF-16 is needed to encode emojis and most other text
    with open(os.path.join(output_path, f'{START_TIME}-{name}'), 'w', encoding='UTF-16') as f:
        f.write(tabulate(df, headers='keys', tablefmt='psql', showindex=False))


def save_yap_stats():
    users_stats = list(YAP_STATS.values())
    usernames = [u.username for u in users_stats]
    letter_counts = [u.letter_count for u in users_stats]
    message_counts = [u.messages for u in users_stats]
    unique_counts = [len(u.unique_words) for u in users_stats]
    avg_letter_counts = [u.get_average_message_length() for u in users_stats]

    a = np.array(letter_counts)
    z_scores = stats.zscore(a)
    yap_data = {
        "username": usernames,
        "z_yap": z_scores,
        "letter count": letter_counts,
        "messages sent": message_counts,
        "average letter count": avg_letter_counts,
        "unique words": unique_counts
    }
    yap_df = pd.DataFrame(yap_data)
    yap_df.sort_values(by=['letter count', 'username'], inplace=True, ascending=False)
    save_df(yap_df, 'yap.txt')


def save_word_stats():
    words, counts = list(WORDS_COUNT.keys()), list(WORDS_COUNT.values())
    words_data = {
        "word": words,
        "count": counts
    }
    words_df = pd.DataFrame(words_data)
    words_df.sort_values(by=['count'], inplace=True, ascending=False)
    save_df(words_df, 'words.txt')


async def on_ready(ready_event: EventData):
    global START_TIME
    tz_UTC = pytz.timezone('UTC')
    START_TIME = datetime.now(tz_UTC).strftime('%y-%m-%d-%H-%M')
    print(f'Bot is ready for work, joining channel {TARGET_CHANNEL}')
    await ready_event.chat.join_room(TARGET_CHANNEL)


async def on_message(msg: ChatMessage):
    if msg.user.name in EXCLUDED_USERS:
        return
    if msg.user.name not in YAP_STATS:
        YAP_STATS[msg.user.name] = UserStats(msg.user.name)
    user_stats = YAP_STATS[msg.user.name]

    words = msg.text.strip().split()
    user_stats.update_stats(words)

    for w in words:
        WORDS_COUNT[w] += 1
    # Uncomment for logging
    print(f'{msg.user.name}\'s letter count is now: {user_stats.letter_count}, with {user_stats.messages} messages')


async def run():
    twitch = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(twitch, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await twitch.set_user_authentication(token, USER_SCOPE, refresh_token)
    
    chat = await Chat(twitch)

    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)

    chat.start()

    # lets run till we press enter in the console
    try:
        input('press ENTER to stop\n')
    finally:
        # now we can close the chat bot and the twitch api client
        chat.stop()
        await twitch.close()
        save_yap_stats()
        save_word_stats()


if __name__ == '__main__':
    asyncio.run(run())