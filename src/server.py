# Taken from: https://pytwitchapi.dev/en/stable/tutorial/user-auth-headless.html

import asyncio
from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, TwitchAPIException
from flask import Flask, redirect, request
from usersettings import UserSettings


TARGET_SCOPE = [AuthScope.CHAT_EDIT, AuthScope.CHAT_READ]
MY_URL = 'http://localhost:17563/login/confirm'


app = Flask(__name__)
twitch: Twitch
auth: UserAuthenticator


@app.route('/login')
def login():
    return redirect(auth.return_auth_url())


@app.route('/login/confirm')
async def login_confirm():
    state = request.args.get('state')
    if state != auth.state:
        return 'Bad state', 401
    code = request.args.get('code')
    if code is None:
        return 'Missing code', 400
    try:
        token, refresh = await auth.authenticate(user_token=code)
        await twitch.set_user_authentication(token, TARGET_SCOPE, refresh)
    except TwitchAPIException as e:
        return 'Failed to generate auth token', 400
    return 'Sucessfully authenticated!'


async def twitch_setup():
    global twitch, auth
    twitch = await Twitch(UserSettings.settings['App ID'], UserSettings.settings['App Secret'])
    auth = UserAuthenticator(twitch, TARGET_SCOPE, url=MY_URL)


if __name__ == '__main__':
    user_settings = UserSettings()
    if user_settings.settings['App ID'] == '':
        user_settings.settings['App ID'] = input('Enter App ID (Do not expose): ')
        user_settings.save_to_file()
    if user_settings.settings['App Secret'] == '':
        user_settings.settings['App Secret'] = input('Enter App Secret (Do not expose): ')
        user_settings.save_to_file()

    asyncio.run(twitch_setup())
    print('If no errors printed, server is running')
