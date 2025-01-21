import os

from usersettings import UserSettings


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_options_common() -> None:
    settings = UserSettings().settings
    print(f"1. {'Set' if settings.app_id == '' else 'Change'} App ID")
    print(f"2. {'Set' if settings.app_secret == '' else 'Change'} App Secret")


def print_options_all() -> None:
    settings = UserSettings().settings
    print_options_common()

    if settings.target_channel == "":
        print("3. Set Target Channel")
    else:
        print(f"3. Change Target Channel ({settings.target_channel})")

    print(
        f"4. Toggle Excluded User (Currently Excluded: {list(settings.excluded_users)})"
    )
    print(
        f"5. Toggle Console Logging (Currently {
            'Enabled' if settings.logging else 'Disabled'
        })"
    )
    print(f"6. Change Padding (Currently {settings.padding})")
    print_options_quit()


def print_options_quit(type: str = "App") -> None:
    print()
    print(f"r. Run {type}")
    print("q. Quit", end="\n\n")


def print_options_server() -> None:
    print_options_common()
    print_options_quit("Server")


def handle_user_input(option: str, from_server: bool) -> None:
    clear()
    print("Press enter to cancel")

    user_input = get_user_input(option, from_server)

    # Padding option will always return ""
    # should only be changed when not from server settings
    if user_input == "" and (option != "5" and not from_server):
        return

    # No need to check again if from server
    update_option(option, user_input)


def get_user_input(option: str, from_server: bool) -> str:
    settings = UserSettings().settings
    match (option, from_server):
        case "1", _:
            return input("Enter App ID: ")
        case "2", _:
            return input("Enter App Secret: ")
        case "3", False:
            print(f"Current Target Channel: {settings.target_channel}")
            return input("New Target Channel: ")
        case "4", False:
            print(f"Current Excluded Users: {list(settings.excluded_users)}")
            return input("Enter User to Toggle: ")
        case "6", False:
            return input("Enter Padding: ")

    return ""


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
        print_options_all()

        user_option = input("Enter option: ").lower()
        if user_option == "r":
            break
        if user_option == "q":
            exit()
        handle_user_input(user_option, False)

    clear()


def server_prompt_loop() -> None:
    while True:
        print_options_server()

        user_option = input("Enter option: ").lower()
        if user_option == "r":
            break
        if user_option == "q":
            exit()
        handle_user_input(user_option, True)
