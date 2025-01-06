# Taken from: https://pytwitchapi.dev/en/stable/tutorial/user-auth-headless.html

import asyncio

from flask import Flask, redirect, request
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.twitch import Twitch
from twitchAPI.type import AuthScope, TwitchAPIException

from user_prompt import server_prompt_loop
from usersettings import UserSettings

TARGET_SCOPE = [AuthScope.CHAT_EDIT, AuthScope.CHAT_READ]
MY_URL = "http://localhost:17563/login/confirm"


app = Flask(__name__)
twitch: Twitch
auth: UserAuthenticator


@app.route("/login")
def login():
    return redirect(auth.return_auth_url())


@app.route("/login/confirm")
async def login_confirm():
    state = request.args.get("state")
    if state != auth.state:
        return "Bad state", 401
    code = request.args.get("code")
    if code is None:
        return "Missing code", 400
    try:
        token, refresh = await auth.authenticate(user_token=code)
        await twitch.set_user_authentication(token, TARGET_SCOPE, refresh)
    except TwitchAPIException:
        return "Failed to generate auth token", 400
    return "Sucessfully authenticated!"


async def twitch_setup():
    global twitch, auth
    twitch = await Twitch(
        UserSettings.settings["App ID"], UserSettings.settings["App Secret"]
    )
    auth = UserAuthenticator(twitch, TARGET_SCOPE, url=MY_URL)


def server_main():
    us = UserSettings()
    while us.settings["App ID"] == "" or us.settings["App Secret"] == "":
        print("App ID or Secret not set, running setup\n")
        server_prompt_loop()

    try:
        asyncio.run(twitch_setup())
        print("Server successfully started.")
        exit()
    except Exception as e:
        print(e)
        print("Something went wrong")
        server_prompt_loop()
        server_main()


if __name__ == "__main__":
    server_main()
