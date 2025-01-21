import math
import os

import pandas as pd
from scipy import stats
from tabulate import tabulate

from usersettings import UserSettings
from userstats import UserStats


def avg_message_length(user_stats: UserStats) -> float:
    return user_stats.letter_count / user_stats.messages


def curve(x: float):
    return math.pow(2, x)


# Calculate 'yap' factor based on collected stats, many magic numbers are found here
def calc_yap_factor(user_stats: UserStats) -> float:
    scalar = user_stats.letter_count**0.75
    uniq_word_ratio = (len(user_stats.unique_words) ** 1.2) / user_stats.messages
    avg_ltrs = avg_message_length(user_stats)
    return math.log(scalar * (uniq_word_ratio + avg_ltrs))


def save_df(
    df_full: pd.DataFrame,
    df_display: pd.DataFrame,
    name: str,
    encode_type: str,
    start_time: str,
) -> None:
    settings = UserSettings().settings
    output_path = os.path.abspath(__file__ + f"/../../output/{settings.target_channel}")
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Full log file
    df_full.to_csv(
        os.path.join(output_path, f"{start_time}-{name}.csv"),
        mode="w",
        encoding=encode_type,
        index=False,
    )

    # df_brief overwrites the same file, is more consise so that it can be put in OBS
    with open(os.path.join(output_path, f"{name}.txt"), "w", encoding=encode_type) as f:
        if UserSettings.settings.padding > 0:
            f.write("\n" * UserSettings.settings.padding)

        f.write(tabulate(df_display, headers="keys", tablefmt="psql", showindex=False))


def get_df_yap_stats(yap_stats: dict[str, UserStats]) -> pd.DataFrame:
    all_user_stats = list(yap_stats.values())

    yap_factors = [calc_yap_factor(u) for u in all_user_stats]
    yap_scaled = stats.zscore(yap_factors)
    yap_costs = list(map(lambda x: curve(x), yap_scaled))

    yap_data = {
        "username": [u.username for u in all_user_stats],
        "yap cost": yap_costs,
        "letters": [u.letter_count for u in all_user_stats],
        "messages": [u.messages for u in all_user_stats],
        "avg. message len": [avg_message_length(u) for u in all_user_stats],
        "vocab": [len(u.unique_words) for u in all_user_stats],
    }
    yap_df = pd.DataFrame(yap_data)
    yap_df.sort_values(by=["yap cost"], inplace=True, ascending=False)
    return yap_df


def get_df_word_stats(word_apperances: dict[str, int]) -> pd.DataFrame:
    # Relies on dictionaries being ordered
    words, counts = list(word_apperances.keys()), list(word_apperances.values())
    words_data = {"word": words, "count": counts}
    words_df = pd.DataFrame(words_data)
    words_df.sort_values(by=["count"], inplace=True, ascending=False)
    return words_df


def save_yap_word_stats(
    yap_stats: dict[str, UserStats], word_apperances: dict[str, int], start_time: str
) -> None:
    yap_df = get_df_yap_stats(yap_stats)
    yap_df_display = yap_df.filter(
        ["username", "yap cost", "avg. message len", "vocab"], axis=1
    )

    words_df = get_df_word_stats(word_apperances)

    save_df(yap_df, yap_df_display, "yap", "UTF-8", start_time)
    save_df(
        words_df, words_df, "words", "UTF-16", start_time
    )  # UTF-16 needed for certain emojis
