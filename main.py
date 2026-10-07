import json
import subprocess
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import psutil

LOG_PATH = "/var/log/syslog"
CPU_THRESHOLD = 50  # percent
MEMORY_THRESHOLD = 800  # MB
INTERVAL = 3600  # seconds
RETRY_DELAY = 60  # seconds


def email_report():
    """Add functionality to email the report to a specified email address
    instead of or in addition to saving it to a file."""


def network_monitoring():
    """Include network usage statistics in the process monitoring section,
    identifying any processes that are using a significant amount of bandwidth."""


# trim the output of 'command' in process monitoring
def trim_command(): ...


def process_monitoring(cpu_limit: float, mem_limit: float):

    # setting a base for cpu usage comparision
    list(psutil.process_iter(["cpu_percent"]))
    time.sleep(1)

    all_proc = []
    for proc in psutil.process_iter(
        ["name", "pid", "cpu_percent", "memory_full_info", "cmdline", "status"]
    ):
        # exluding processes that don't use any cpu memory resources
        if proc.info["status"] == psutil.STATUS_ZOMBIE:
            continue

        if proc.info["memory_full_info"] is None:
            continue

        # memory usage converting bytes to MB
        # script must be run with root access
        mem = proc.info["memory_full_info"].uss
        memory_usage = round(mem / (1024 * 1024), 3)
        cpu_usage = proc.info["cpu_percent"]
        name = proc.info["name"]
        pid = proc.info["pid"]
        command = proc.info["cmdline"]

        process = {
            "name": name,
            "pid": pid,
            "command": command,
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
        }

        all_proc.append(process)

    msg = "---------- High usage processes ----------" + "\n"
    for proc in all_proc:
        if proc["cpu_usage"] > cpu_limit:
            error1 = f"process with PID {proc['pid']} has passed cpu threshold. process command: {proc['command']}"
            msg += error1 + "\n"
        if proc["memory_usage"] > mem_limit:
            error2 = f"process with PID {proc['pid']} has passed memory threshold. process command: {proc['command']}"
            msg += error2 + "\n"

    return msg


def is_within_last_24_hours(timestamp: str) -> bool:
    """This function only works with iso format.
    Classic format timestamps need another implementation.
    """
    log_time = datetime.fromisoformat(timestamp)
    now = datetime.now().astimezone()
    last_24_hours = now - timedelta(hours=24)
    return last_24_hours <= log_time <= now


def log_analysis2(path: str) -> str:
    logs = []

    with open(path, "r") as f:
        for line in f:
            log_data = line.split(maxsplit=3)
            if len(log_data) < 4:  # skip empty or malformed lines
                continue

            timestamp = log_data[0]
            try:
                if not is_within_last_24_hours(timestamp):
                    continue
            except ValueError:  # first word is not a valid timestamp
                continue

            logs.append({"timestamp": timestamp, "message": log_data[3].strip()})

    msg = "---------- log analysis ----------" + "\n"
    for log in logs:
        msg += f"{log['timestamp']} message: {log['message']}" + "\n"

    return msg


def log_analysis():
    """This function is better because the prompt said
    that report should have timestamp, log level and message but
    log level doesn't appear in /var/log/syslog so I used journalctl
    command to read the logs. Also the problem with classic format timestamps
    solved here.
    """
    log_level = {
        "0": "emerg",
        "1": "alert",
        "2": "crit",
        "3": "error",
    }
    result = subprocess.run(
        ["journalctl", "--since", "24 hours ago", "-p", "3", "-o", "json"],
        capture_output=True,
        text=True,
    )

    logs = []
    for line in result.stdout.splitlines():
        raw_log = json.loads(line)

        level = log_level.get(raw_log.get("PRIORITY"), "unknown")
        msg = raw_log.get("MESSAGE")
        # checking if MESSAGE field is str not list of integers and converting it if so
        if isinstance(msg, list):
            msg = bytes(msg).decode("utf-8", errors="replace")
        timestamp_seconds = (
            float(raw_log.get("__REALTIME_TIMESTAMP")) / 1_000_000
        )  # convertin microseconds into seconds
        timestamp = datetime.fromtimestamp(timestamp_seconds).astimezone()

        log = {"timestamp": timestamp, "level": level, "message": msg}
        logs.append(log)

    msg = "---------- log analysis ----------" + "\n"
    for l in logs:
        msg += (
            f"{l['timestamp']} log-level:[{l['level']}] message: {l['message']}" + "\n"
        )

    return msg


def report_generation(monitor: str, log: str):
    path = Path("logs")
    path.mkdir(exist_ok=True)
    now = datetime.now(tz=UTC).strftime("%Y-%m-%d-%H-%M-%S")

    with open(f"{path}/{now}.txt", "w", encoding="utf-8") as file:
        file.write(monitor)
        file.write(log)


def main():

    while True:
        try:
            print("Monitoring processes...")
            monitor_report = process_monitoring(CPU_THRESHOLD, MEMORY_THRESHOLD)

            print("Analyzing logs...")
            # log_report = log_analysis()
            log_report = log_analysis2(LOG_PATH)

            print("Generationg report...")
            report_generation(monitor_report, log_report)
            print("Report generated.\nScript running...")

            time.sleep(INTERVAL)

        except KeyboardInterrupt:
            print("stopping script...")
            break
        except Exception as e:
            print(f"exception: {e}")
            time.sleep(RETRY_DELAY)  # preventing busy-loop problem


if __name__ == "__main__":
    main()
