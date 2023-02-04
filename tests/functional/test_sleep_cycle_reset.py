import csv
from datetime import datetime
import json
import os
import subprocess
import sys
from typing import List

import pytest

script_name = "sleep_cycle_reset.py"

@pytest.fixture(scope="session", autouse=True)
def setup_path():
    sys.path.append(os.getcwd())


@pytest.fixture(scope="session")
def load_stub_data():
    pth: str = "sleep_cycle_reset_table_fixture.json"
    cwd: str = os.getcwd()
    with open(os.path.join(cwd, pth), "r") as f:
        data = json.load(f)
    return data


class TestSleepCycleReset:
    cmd: str = "python sleep_cycle_reset/sleep_cycle_reset.py"
    
    def call_script_and_get_outputs(self, cmd):
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = proc.communicate()

        return out.decode(), err.decode()

    def test_prints_usage_when_called_without_any_arguments(self):
        _, err = self.call_script_and_get_outputs(self.cmd)
        usage_information = [
            "usage: sleep_cycle_reset.py [-h] --start-date START_DATE --current-sleep-time",
            "CURRENT_SLEEP_TIME --target-wakeup-time",
            "TARGET_WAKEUP_TIME",
            "sleep_cycle_reset.py: error: the following arguments are required: --start-date, --current-sleep-time, --target-wakeup-time",
        ]
        for (act, req) in zip(usage_information, err.split("\n")):
            assert act.strip() == req.strip()

    def test_prints_usage_when_args_are_not_specified_completely(self):
        args_list = [
            "--start-date",
            "--current-sleep-time",
            "--target-wakeup-time",
        ]
        usage_information = [
            "usage: sleep_cycle_reset.py [-h] --start-date START_DATE --current-sleep-time",
            "CURRENT_SLEEP_TIME --target-wakeup-time",
            "TARGET_WAKEUP_TIME",
            "sleep_cycle_reset.py: error: the following arguments are required:",
        ]

        for arg in args_list:
            cmd = f"{self.cmd} {arg} 1971-01-01"
            _, err = self.call_script_and_get_outputs(cmd)

            for j, (req, act) in enumerate(zip(usage_information, err.split("\n"))):
                if j < len(usage_information) - 1:
                    assert req.strip() == act.strip()
                else:
                    _args = list(filter(lambda x: x != arg, args_list)) 
                    _req = f"{req} {', '.join(_args)}"
                    assert _req == act.strip()

    def test_prints_correct_message_when_current_sleep_time_is_not_in_proper_range(self):
        # proper range is between: 00:00 and 23:59
        # anytime between this range is valid
        invalid_values = [
            "100:100",
            "24:00",
            "16:71",
        ]

        start_date = datetime.strftime(datetime.now().date(), "%d-%m-%Y")
        _base = self.cmd + " --start-date {start_date} --current-sleep-time {cst} --target-wakeup-time 0"
        for val in invalid_values:
            cmd = _base.format(start_date=start_date, cst=val)
            _, err = self.call_script_and_get_outputs(cmd)
            assert err.strip() == f"Value specified for --current-sleep-time: {val} is invalid! Has to be in the format HH:MM with hours in the 24-hour format!"

    def test_prints_correct_message_when_target_wakeup_time_is_not_in_proper_range(self):
        # proper range is between: 00:00 and 23:59
        # anytime between this range is valid
        invalid_values = [
            "100:100",
            "24:00",
            "16:71",
        ]

        start_date = datetime.strftime(datetime.now().date(), "%d-%m-%Y")
        _base = self.cmd + " --start-date {start_date} --current-sleep-time 00:00 --target-wakeup-time {twt}"
        for val in invalid_values:
            cmd = _base.format(start_date=start_date, twt=val)
            _, err = self.call_script_and_get_outputs(cmd)
            assert err.strip() == f"Value specified for --target-wakeup-time: {val} is invalid! Has to be in the format HH:MM with hours in the 24-hour format!"

    def test_creates_file_with_correct_name_when_inputs_are_correct(self):
        start_date = datetime.strftime(datetime.now().date(), "%d-%m-%Y")
        current_sleep_time = "02:00"
        target_wakeup_time = "07:00"
        cmd = f"{self.cmd} --start-date {start_date} --current-sleep-time {current_sleep_time} --target-wakeup-time {target_wakeup_time}"
        file_name = f"sleep_cycle_reset_table_{start_date}_{current_sleep_time}_{target_wakeup_time}.csv"

        out, err = self.call_script_and_get_outputs(cmd)

        assert err == ""
        assert out.strip() == f"Cycle generated successfully. File saved at ./{file_name}"
        assert os.path.exists(os.path.join(os.getcwd(), file_name))

    def test_creates_file_with_correct_headers(self):
        start_date = datetime.strftime(datetime.now().date(), "%d-%m-%Y")
        current_sleep_time = "02:00"
        target_wakeup_time = "07:00"
        cmd = f"{self.cmd} --start-date {start_date} --current-sleep-time {current_sleep_time} --target-wakeup-time {target_wakeup_time}"
        filename = f"sleep_cycle_reset_table_{start_date}_{current_sleep_time}_{target_wakeup_time}.csv"

        _, _ = self.call_script_and_get_outputs(cmd)

        headers: List[str] = []
        with open(filename, "r") as f:
            reader = csv.reader(f)
            for idx, row in enumerate(reader):
                if idx == 0:
                    headers = row
                    break

        assert headers == [
            "Sl No",
            "Date",
            "Night Routine Start Time",
            "Getting Into Bed Time",
            "Falling Asleep Time",
            "Waking Up Time",
        ]

    def test_creates_table_correctly_for_given_input(self, load_stub_data):
        stubs = load_stub_data

        start_date = datetime.strftime(datetime.now().date(), "%d-%m-%Y")
        for _stub in stubs:
            current_sleep_time = _stub["current_sleep_time"]
            target_wakeup_time = _stub["target_wakeup_time"]
            data = _stub["data"]

            cmd = f"{self.cmd} --start-date {start_date} --current-sleep-time {current_sleep_time} --target-wakeup-time {target_wakeup_time}"
            filename = f"sleep_cycle_reset_table_{start_date}_{current_sleep_time}_{target_wakeup_time}"

            _, _ = self.call_script_and_get_outputs(cmd)

            with open(filename, "r") as f:
                reader = csv.reader(f, delimiter=",")
                for idx, row in reader:
                    if idx == 0:
                        continue
                    assert row == data[idx]