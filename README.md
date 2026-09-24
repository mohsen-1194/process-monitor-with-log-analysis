### Problem: Process Monitor with Log Analysis

Objective: Create a Python script that monitors running processes on a Linux system and generates a report on specific criteria, such as CPU and memory usage. Additionally, the script should analyze system logs to report any errors or critical events that occurred within the last 24 hours.

#### Requirements:

1. Process Monitoring:
- Use Python to list all currently running processes with their PID, CPU usage, and memory usage.
- Identify any processes that exceed thresholds defined for CPU (e.g., 50%) and memory usage (e.g., 1GB). These thresholds should be configurable.
- Generate a summary report of high-usage processes and include the command that started each process.

2. Log Analysis:
- Analyze the /var/log/syslog file (or an equivalent system log file on your Linux distribution) to find any error or critical messages logged within the last 24 hours.
- Summarize these messages in the report, including the timestamp, log level, and message content.

3. Report Generation:
- Output the report to a text file, including the date and time the report was generated.
- The report should be easy to read, with clear sections for process monitoring and log analysis.

#### Additional Challenges:

- Implement real-time monitoring where the script runs continuously and checks the system at configured intervals (e.g., every hour).
- Add functionality to email the report to a specified email address instead of or in addition to saving it to a file.
- Include network usage statistics in the process monitoring section, identifying any processes that are using a significant amount of bandwidth.