# write a command line script
# accept a start date, current sleep time, target wake up time
# assume a sleep duration of 8 hours
# assume a 30 minute window for night routine
# assume a 15 minute window between getting into bed and falling asleep

import argparse
import csv
from datetime import datetime 
import os
import sys
from typing import List

HEADERS: List[str] = [
    "Sl No",
    "Date",
    "Night Routine Start Time",
    "Getting Into Bed Time",
    "Falling Asleep Time",
    "Waking Up Time",
]

PARSER = argparse.ArgumentParser()

PARSER.add_argument("--start-date", nargs=1, type=str, required=True,
help="The date on which you want to start working on fixing your sleep cycle. Accepted format: DD-MM-YYYY",
dest="start_date",
)

PARSER.add_argument("--current-sleep-time", nargs=1, type=str, required=True,
help="The time at which you're currently going to bed. Specified as HH:MM in the 24-hour format",
dest="current_sleep_time",
)

PARSER.add_argument("--target-wakeup-time", nargs=1, type=str, required=True,
help="The time at which you want to start waking up. Specified as HH:MM in the 24-hour format",
dest="target_wakeup_time",
)

def parse_start_date(start_date):
    return datetime.strptime(start_date, "%d-%m-%Y").date()

def parse_time(_time):
    return datetime.strptime(_time, "%H:%M")

def generate_sleep_cycle_table(start_date, current_sleep_time, target_wakeup_time):
    return []

if __name__ == "__main__":
    args = PARSER.parse_args()

    start_date = args.start_date[0]
    current_sleep_time = args.current_sleep_time[0]
    target_wakeup_time = args.target_wakeup_time[0]

    start_date = parse_start_date(start_date=start_date)

    try:
        current_sleep_time = parse_time(current_sleep_time)
    except ValueError:
        e = f"Value specified for --current-sleep-time: {current_sleep_time} is invalid! Has to be in the format HH:MM with hours in the 24-hour format!"
        sys.exit(e)

    try:
        target_wakeup_time = parse_time(target_wakeup_time) 
    except ValueError:
        e = f"Value specified for --target-wakeup-time: {target_wakeup_time} is invalid! Has to be in the format HH:MM with hours in the 24-hour format!"
        sys.exit(e)

    filename: str = f"sleep_cycle_reset_table_{args.start_date[0]}_{args.current_sleep_time[0]}_{args.target_wakeup_time[0]}.csv"
    print(f"Cycle generated successfully. File saved at ./{filename}", file=sys.stdout)

    data = generate_sleep_cycle_table(start_date, current_sleep_time, target_wakeup_time)

    with open(filename, 'w') as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(HEADERS)

    sys.exit(os.EX_OK)
    