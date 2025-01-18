import os

from usersettings import UserSettings


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_options() -> None:
    settings = UserSettings().settings
    print(f"1. {'Set' if settings.app_id == '' else 'Change'} App ID")
    print(f"2. {'Set' if settings.app_secret == '' else 'Change'} App Secret")
    if settings.target_channel == "":
        print("3. Set Target Channel")
    else:
        print(f"3. Change Target Channel ({settings.target_channel})")
    print(
        f"4. Toggle Excluded User (Currently Excluded: {
            list(settings.excluded_users)})"
    )
    print(
        f"5. Toggle Console Logging (Currently {
            'Enabled' if settings.logging else 'Disabled'
        })"
    )
    print(f"6. Change Padding (Currently {settings.padding})", end="\n\n")
    print("r. Run Bot")
    print("q. Quit", end="\n\n")


def print_option(option: str) -> None:
    clear()
    print("Press enter to cancel")

    settings = UserSettings().settings
    u: str = ""
    match option:
        case "1":
            u = input("Enter App ID: ")
        case "2":
            u = input("Enter App Secret: ")
        case "3":
            print(f"Current Target Channel: {settings.target_channel}")
            u = input("New Target Channel: ")
        case "4":
            print(f"Current Excluded Users: {list(settings.excluded_users)}")
            u = input("Enter User to Toggle: ")
        case "5":
            u
        case "6":
            u = input("Enter Padding: ")
        case _:
            return

    if u == "" and option != "5":
        return
    update_option(option, u)


def update_option(option: str, new_val: str):
    user_settings = UserSettings()
    settings = user_settings.settings
    match option:
        case "1":
            settings.app_id = new_val
        case "2":
            settings.app_secret = new_val
        case "3":
            settings.target_channel = new_val.lower()
        case "4":
            if new_val in settings.excluded_users:
                settings.excluded_users.remove(new_val.lower())
            else:
                settings.excluded_users.add(new_val.lower())
        case "5":
            settings.logging = not (settings.logging)
        case "6":
            try:
                settings.padding = max(0, int(new_val))
            except ValueError:
                return
    user_settings.save_to_file()


def prompt_loop() -> None:
    while True:
        clear()
        print_options()

        user_input = input("Enter option: ").lower()
        if user_input == "r":
            break
        if user_input == "q":
            exit()
        print_option(user_input)

    clear()


def print_options_server() -> None:
    settings = UserSettings().settings
    print(f"1. {'Set' if settings.app_id == '' else 'Change'} App ID")
    print(
        f"2. {'Set' if settings.app_secret ==
          '' else 'Change'} App Secret\n"
    )
    print("r. Run server")
    print("q. Quit\n")


def handle_option_server(option: str) -> None:
    clear()
    print("Press enter to cancel")

    user_settings = UserSettings()
    settings = user_settings.settings.copy()
    u: str = ""
    match option:
        case "1":
            u = input("Enter App ID: ")
            settings.app_id = u
        case "2":
            u = input("Enter App Secret: ")
            settings.app_secret = u

    if u == "":
        return
    user_settings.settings = settings
    user_settings.save_to_file()


def server_prompt_loop() -> None:
    while True:
        print_options_server()

        user_input = input("Enter option: ").lower()
        if user_input == "r":
            break
        if user_input == "q":
            exit()
        handle_option_server(user_input)
