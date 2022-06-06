import os.path
from calendar import monthrange
import json
from datetime import datetime

import requests
import time
import csv

# 1878-01-01 -> 1878-01-31 is the very beginning of all precipitation date


def get_week_day(year, month, day) -> int:
    d = datetime(year, month, day)
    return d.weekday()

def str_to_float(s: str) -> float:
    try:
        s = float(s)
    except ValueError:
        s = 0
    return s

def get_monthly_data(start_date:str, end_date:str) -> dict:
    params = {"elems": [{"name": "maxt", "add": "t"}, {"name": "mint", "add": "t"}, {"name": "avgt", "add": "t"},
                        {"name": "pcpn", "add": "t"}, {"name": "snow", "add": "t"}], "sid": "BOIthr+9", 'sDate': start_date, 'eDate': end_date}
    return requests.get(f"https://data.rcc-acis.org/StnData?params={json.dumps(params)}&output=json").json()['data']


def write_to_csv(file_name: str, data: list) -> None:
    if not os.path.exists(file_name):
        with open(file_name, 'w', newline='') as csvfile:
            headers = ['year', 'month', 'day', 'precipitation', 'weekday']
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(headers)
            writer.writerow(data)
    else:
        with open(file_name, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(data)


def calculate_weekday_vs_weekend_rain(start_date: str, end_date:str):
    weekend_rain_count = 0
    weekday_rain_count = 0

    start_date = start_date.split("-")
    end_date = end_date.split("-")

    start = {
        'year': int(start_date[0]),
        'month': int(start_date[1]),
        'day':int(start_date[2])
    }

    end = {
        'year': int(end_date[0]),
        'month': int(end_date[1]),
        'day': int(end_date[2])
    }

    for x in range(start['year'], end['year']+1):
        for y in range(1,12+1):
            data = get_monthly_data(f"{str(x)}-{str(y)}-{str(1)}", f"{str(x)}-{str(y)}-{str(monthrange(x, y)[1])}")
            time.sleep(1.5)
            for z in range(1, len(data)+1):
                print(f"{str(x)}-{str(y)}-{str(z)}")
                rained = True if str_to_float(data[z-1][4][0]) != 0 else False
                weekday = get_week_day(x, y, z)
                is_weekend = (weekday > 4)
                print(f"    rained: {'yes' if rained else 'no'}\n"
                      f"    weekend: {'yes' if is_weekend else 'no'}") # 4 = sat, sun | 5 includes friday

                if rained:
                    if is_weekend:
                        weekend_rain_count += 1
                    else:
                        weekday_rain_count += 1

                write_to_csv("weather.csv", [x, y, z, str_to_float(data[z-1][4][0]), weekday])
                if end['year'] == x and end['month'] == y and end['day'] == z:
                    total_count = weekday_rain_count+weekend_rain_count
                    print(f"Total days rained: {total_count}\n"
                          f"Weekend rain days: {weekend_rain_count} ({weekend_rain_count/total_count*100}%)\n"
                          f"Weekday rain days: {weekday_rain_count} ({weekday_rain_count/total_count*100}%)")
                    return


#print(get_monthly_data("1878-01-01", "1878-01-31"))


calculate_weekday_vs_weekend_rain("1975-01-01", "2022-06-5")