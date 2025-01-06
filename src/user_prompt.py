import os

from usersettings import UserSettings


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_options() -> None:
    settings = UserSettings().settings
    print(f'1. {'Set' if settings["App ID"] == '' else 'Change'} App ID')
    print(f'2. {'Set' if settings["App Secret"] == '' else 'Change'} App Secret')
    if settings["Target Channel"] == "":
        print("3. Set Target Channel")
    else:
        print(f'3. Change Target Channel ({settings["Target Channel"]})')
    print(
        f"4. Toggle Excluded User (Currently Excluded: {list(settings['Excluded Users'])})"
    )
    print(
        f"5. Toggle Console Logging (Currently {'Enabled' if settings['Logging'] else 'Disabled'})"
    )
    print(f"6. Change Padding (Currently {settings['Padding']})", end="\n\n")
    print("r. Run Bot")
    print("q. Quit", end="\n\n")


def handle_option(option: str) -> None:
    clear()
    print("Press enter to cancel")

    user_settings = UserSettings()
    settings = user_settings.settings.copy()
    u: str = ""
    match option:
        case "1":
            u = input("Enter App ID: ")
            settings["App ID"] = u
        case "2":
            u = input("Enter App Secret: ")
            settings["App Secret"] = u
        case "3":
            print(f"Current Target Channel: {settings['Target Channel']}")
            u = input("New Target Channel: ")
            settings["Target Channel"] = u
        case "4":
            print(f"Current Excluded Users: {settings['Excluded Users']}")
            u = input("Enter User to Toggle: ")
            settings["Excluded Users"] ^= set(u)
        case "5":
            settings["Logging"] = not settings["Logging"]
        case "6":
            try:
                u = int(input("Enter Padding: "))
                settings["Padding"] = max(0, u)
            except ValueError:
                return

    if u == "" and option != "5":
        return

    user_settings.settings = settings
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
        handle_option(user_input)

    clear()


def print_options_server() -> None:
    settings = UserSettings().settings
    print(f'1. {'Set' if settings["App ID"] == '' else 'Change'} App ID')
    print(f'2. {'Set' if settings["App Secret"] == '' else 'Change'} App Secret\n')
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
            settings["App ID"] = u
        case "2":
            u = input("Enter App Secret: ")
            settings["App Secret"] = u

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
