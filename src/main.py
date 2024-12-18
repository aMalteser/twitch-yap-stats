import math
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
import scipy.stats as stats
from tabulate import tabulate
from datetime import datetime
import pytz
import typing
import validators


load_dotenv()
APP_ID = os.getenv('APP_ID')
APP_SECRET = os.getenv('APP_SECRET')
TARGET_CHANNEL = os.getenv('TARGET_CHANNEL')
EXCLUDED_USERS = set(os.getenv('EXCLUDED_USERS').split(','))

USER_SCOPE = [AuthScope.CHAT_READ]

YAP_STATS: dict[str, UserStats] = {}
WORDS_COUNT: dict[str, int] = defaultdict(int)

START_TIME: str


def save_df(df_full: pd.DataFrame, df_brief: pd.DataFrame, name: str, encode_type: str) -> None:
    # equivalent of ./src/../output/TARGET_CHANNEL
    abs_path = os.path.abspath(__file__)
    output_path = os.path.join(os.path.dirname(abs_path), os.pardir, 'output', TARGET_CHANNEL)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        
    # Full log file
    df_full.to_csv(os.path.join(output_path, f'{START_TIME}-{name}.csv'), mode='w', encoding=encode_type, index=False)
    
    # df_brief overwrites the same file, is more consise so that it can be put in OBS
    with open(os.path.join(output_path, f'{name}.txt'), 'w', encoding=encode_type) as f:
        f.write(tabulate(df_brief, headers='keys', tablefmt='psql', showindex=False))


def curve(x: float):
    return math.pow(2, x)


def save_yap_stats() -> None:
    users_stats = list(YAP_STATS.values())
    usernames = [u.username for u in users_stats]
    letter_counts = [u.letter_count for u in users_stats]
    message_counts = [u.messages for u in users_stats]
    unique_counts = [len(u.unique_words) for u in users_stats]
    avg_msg_lens = [u.get_average_message_length() for u in users_stats]

    yap_factors = [u.calc_yap_factor() for u in users_stats]
    # Yap factors are by nature exponentional, taking the logarithm produces nicer results
    scaled_yap_factors = list(map(lambda x: math.log(x), yap_factors))
    yap_scaled = stats.zscore(scaled_yap_factors)
    yap_costs = list(map(lambda x: curve(x), yap_scaled))

    yap_data = {
        "username": usernames,
        "yap cost": yap_costs,
        "letters": letter_counts,
        "messages": message_counts,
        "avg. message len": avg_msg_lens,
        "vocab": unique_counts
    }
    yap_df = pd.DataFrame(yap_data)
    yap_df.sort_values(by=['yap cost'], inplace=True, ascending=False)
    yap_df_brief = yap_df.filter(['username', 'yap cost', 'avg. message len', 'vocab'], axis=1)
    save_df(yap_df, yap_df_brief, 'yap', 'UTF-8')


def save_word_stats() -> None:
    # Relies on dictionaries being ordered
    words, counts = list(WORDS_COUNT.keys()), list(WORDS_COUNT.values())
    words_data = {
        "word": words,
        "count": counts
    }
    words_df = pd.DataFrame(words_data)
    words_df.sort_values(by=['count'], inplace=True, ascending=False)
    save_df(words_df, words_df, 'words', 'UTF-16') # UTF-16 needed for certain emojis


def check_url(word_list: list[str]) -> list[bool]:
    return map(lambda x: validators.url(x), word_list)


def filter_word_list(word_list: list[str]) -> list[str]:
    url_filter = check_url(word_list)
    overall_filter = [all(i) for i in zip(url_filter)]
    return list(filter(overall_filter, word_list))


async def on_ready(ready_event: EventData) -> None:
    global START_TIME
    tz_UTC = pytz.timezone('UTC')
    START_TIME = datetime.now(tz_UTC).strftime('%y-%m-%d-%H-%M')
    print(f'Bot is ready for work, joining channel {TARGET_CHANNEL}')
    await ready_event.chat.join_room(TARGET_CHANNEL)


async def on_message(msg: ChatMessage) -> None:
    if msg.user.name in EXCLUDED_USERS:
        return
    if msg.user.name not in YAP_STATS:
        YAP_STATS[msg.user.name] = UserStats(msg.user.name)
    user_stats = YAP_STATS[msg.user.name]

    words = msg.text.strip().lower().split()
    user_stats.update_stats(words)

    for w in words:
        WORDS_COUNT[w] += 1
    # Uncomment for logging
    # print(f'{msg.user.name}\'s letter count is now: {user_stats.letter_count}, with {user_stats.messages} messages')


async def run() -> None:
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
        # Save once the twitch thread has closed, to not get anymore writes to dictionaries
        save_yap_stats()
        save_word_stats()


if __name__ == '__main__':
    asyncio.run(run())