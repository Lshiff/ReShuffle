import time
import math

def discord_timestamp(sql_timestamp, style="relative time"):
    # date_time = datetime(sql_timestamp)
    date_time = sql_timestamp
    unix_timestamp = math.floor(time.mktime(date_time.timetuple()))

    style_dict = {
        "default": "",
        "short time": ':t',
        "long time": ':T',
        "short date": ':d',
        "long date": ':D',
        "short date/time": ':f',
        "long date/time": ':F',
        "relative time": ':R'
    }

    return f"<t:{unix_timestamp}{style_dict[style]}>"
