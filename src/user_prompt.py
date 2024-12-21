from usersettings import UserSettings
import os


def clear() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')


def print_settings() -> None:
    settings = UserSettings().settings
    if settings['App ID'] == '':
        print('App ID not set', end=', ')
    else:
        print('App ID set', end=', ')
    if settings['App Secret'] == '':
        print('App Secret not set')
    else:
        print('App Secret set')
    
    print(f'Target Channel: {settings['Target Channel']}')
    print(f'Excluded Users: {list(settings['Excluded Users'])}')
    print(f'Logging: {'Enabled' if settings['Logging'] else 'Disabled'}')
    print(f'Padding: {settings['Padding']}', end='\n\n')


def print_options() -> None:
    print('1. Set App ID')
    print('2. Set App Secret')
    print('3. Set Target Channel')
    print('4. Toggle Excluded User')
    print('5. Toggle Logging')
    print('6. Set Padding', end='\n\n')
    print('r. Run Bot')
    print('q. Quit', end='\n\n')


def handle_option(option: str) -> None:
    clear()
    print('Press enter to cancel')

    user_settings = UserSettings()
    settings = user_settings.settings.copy()
    u: str = ''
    match option:
        case '1':
            u = input('Enter App ID: ')
            settings['App ID'] = u
        case '2':
            u = input('Enter App Secret: ')
            settings['App Secret'] = u
        case '3':
            u = input('Enter Target Channel: ')
            settings['Target Channel'] = u
        case '4':
            u = input('Enter Excluded User: ')
            if u in settings['Excluded Users']:
                settings['Excluded Users'].remove(u)
            else:
                settings['Excluded Users'].add(u)
        case '5':
            settings['Logging'] = not settings['Logging']
            u = 'saved'
        case '6':
            try:
                u = int(input('Enter Padding: '))
                settings['Padding'] = max(0, u)
            except ValueError:
                return

    if u == '':
        return

    user_settings.settings = settings
    user_settings.save_to_file()
    

def prompt_loop() -> None:
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
        
    clear()
