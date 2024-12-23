from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.chat import Chat, EventData, ChatMessage
from usersettings import UserSettings
from userstats import UserStats
from collections import defaultdict
from user_prompt import prompt_loop
from save_stats import save_yap_word_stats
from datetime import datetime
import asyncio
import pytz
import validators


USER_SCOPE = [AuthScope.CHAT_READ]

YAP_STATS: dict[str, UserStats] = {}
WORD_APPEARANCES: dict[str, int] = defaultdict(int)

START_TIME: str


def check_url(word_list: list[str]) -> list[bool]:
    return map(lambda x: validators.url(x), word_list)


def filter_word_list(word_list: list[str]) -> list[str]:
    url_check = check_url(word_list)
    return [word for word, is_url in zip(word_list, url_check) if not is_url]


def handle_message(username: str, words: list[str]) -> None:
    settings = UserSettings().settings

    if username not in YAP_STATS:
        YAP_STATS[username] = UserStats(username)
    user_stats = YAP_STATS[username]
    user_stats.update_stats(words)

    for w in words:
        WORD_APPEARANCES[w] += 1

    if settings['Logging']:
        print(f'{username} has now sent {user_stats.messages} messages')


async def on_message(msg: ChatMessage) -> None:
    settings = UserSettings().settings

    if msg.user.name in settings['Excluded Users']:
        return

    words = filter_word_list(msg.text.strip().lower().split())
    if len(words) == 0:
        return

    handle_message(msg.user.name, words)


async def on_ready(ready_event: EventData) -> None:
    global START_TIME
    tz_UTC = pytz.timezone('UTC')
    START_TIME = datetime.now(tz_UTC).strftime('%y-%m-%d-%H-%M')

    settings = UserSettings().settings
    print(f'Bot is ready for work, joining channel {settings["Target Channel"]}')
    await ready_event.chat.join_room(settings['Target Channel'])


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
        global START_TIME
        save_yap_word_stats(YAP_STATS, WORD_APPEARANCES, START_TIME)


if __name__ == '__main__':
    while True:
        prompt_loop()

        settings = UserSettings().settings
        if settings['App ID'] == '':
            print('App ID not set, exiting')
            exit()
        if settings['App Secret'] == '':
            print('App Secret not set, exiting')
            exit()
        if settings['Target Channel'] == '':
            print('Target Channel not set, exiting')
            exit()

        asyncio.run(run_bot())

