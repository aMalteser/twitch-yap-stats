from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage
from usersettings import UserSettings
from userstats import UserStats
from collections import defaultdict
from tabulate import tabulate
from datetime import datetime
import pandas as pd
import scipy.stats as stats
import asyncio
import os
import math
import pytz
import typing
import validators


USER_SCOPE = [AuthScope.CHAT_READ]

YAP_STATS: dict[str, UserStats] = {}
WORDS_COUNT: dict[str, int] = defaultdict(int)

START_TIME: str


def save_df(df_full: pd.DataFrame, df_brief: pd.DataFrame, name: str, encode_type: str) -> None:
    settings = UserSettings().settings
    # equivalent of ./src/../output/TARGET_CHANNEL
    abs_path = os.path.abspath(__file__)
    output_path = os.path.join(os.path.dirname(abs_path), os.pardir, 'output', settings['Target Channel'])
    if not os.path.exists(output_path):
        os.makedirs(output_path)
        
    # Full log file
    df_full.to_csv(os.path.join(output_path, f'{START_TIME}-{name}.csv'), mode='w', encoding=encode_type, index=False)
    
    # df_brief overwrites the same file, is more consise so that it can be put in OBS
    with open(os.path.join(output_path, f'{name}.txt'), 'w', encoding=encode_type) as f:
        if UserSettings.settings['Padding'] > 0:
            f.write('\n' * UserSettings.settings['Padding'])

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
    url_check = check_url(word_list)
    return [word for word, is_url in zip(word_list, url_check) if not is_url]


async def on_ready(ready_event: EventData) -> None:
    global START_TIME
    tz_UTC = pytz.timezone('UTC')
    START_TIME = datetime.now(tz_UTC).strftime('%y-%m-%d-%H-%M')

    settings = UserSettings().settings
    print(f'Bot is ready for work, joining channel {settings["Target Channel"]}')
    await ready_event.chat.join_room(settings['Target Channel'])


async def on_message(msg: ChatMessage) -> None:
    if msg.user.name in set(UserSettings().settings['Excluded Users']):
        return
    
    words = filter_word_list(msg.text.strip().lower().split())
    if len(words) == 0:
        return
    
    if msg.user.name not in YAP_STATS:
        YAP_STATS[msg.user.name] = UserStats(msg.user.name)
    user_stats = YAP_STATS[msg.user.name]
    user_stats.update_stats(words)

    for w in words:
        WORDS_COUNT[w] += 1
    
    if UserSettings().settings['Logging']:
        print(f'{msg.user.name} has now sent {user_stats.messages} messages')


async def run_bot() -> None:
    settings = UserSettings().settings

    twitch = await Twitch(settings['App ID'], settings['App Secret'])
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
        print('Saving stats')
        save_yap_stats()
        save_word_stats()


def clear() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')


def print_settings() -> None:
    user_settings = UserSettings()
    if user_settings.settings['App ID'] == '':
        print('App ID not set', end=', ')
    else:
        print('App ID set', end=', ')
    if user_settings.settings['App Secret'] == '':
        print('App Secret not set')
    else:
        print('App Secret set')
    
    print(f'Target Channel: {user_settings.settings['Target Channel']}')
    print(f'Excluded Users: {list(user_settings.settings['Excluded Users'])}')
    print(f'Logging: {'Enabled' if user_settings.settings['Logging'] else 'Disabled'}')
    print(f'Padding: {user_settings.settings['Padding']}', end='\n\n')


def handle_option(option: str) -> None:
    user_settings = UserSettings()
    settings = user_settings.settings
    match option:
        case '1':
            settings['App ID'] = input('Enter App ID (Do not expose): ')
        case '2':
            settings['App Secret'] = input('Enter App Secret (Do not expose): ')
        case '3':
            settings['Target Channel'] = input('Enter Target Channel: ').lower()
        case '4':
            settings['Excluded Users'].symmetric_difference_update([input('Enter user to toggle: ').lower()])
        case '5':
            settings['Logging'] = not settings['Logging']
        case '6':
            try:
                new_padding = max(0, int(input('Enter padding: ')))
                settings['Padding'] = new_padding
            except ValueError:
                print('Invalid padding')

    user_settings.save_to_file()
    

def print_options() -> None:
    print('1. Set App ID')
    print('2. Set App Secret')
    print('3. Set Target Channel')
    print('4. Toggle Excluded User')
    print('5. Toggle Logging')
    print('6. Set Padding', end='\n\n')
    print('r. Start Bot')
    print('q. Quit', end='\n\n')


if __name__ == '__main__':
    user_input: str = ''
    while True:
        clear()
        print_settings()
        print_options()
        user_input = input('Enter option: ').lower()
        if user_input == 'r':
            break
        if user_input == 'q':
            exit()
        handle_option(user_input)
        
    if UserSettings().settings['App ID'] == '':
        print('App ID not set, exiting')
        exit()
    if UserSettings().settings['App Secret'] == '':
        print('App Secret not set, exiting')
        exit()
    if UserSettings().settings['Target Channel'] == '':
        print('Target Channel not set, exiting')

    asyncio.run(run_bot())