#!/usr/bin/env python3
"""
Morning catch-up: runs at 8AM to recover missed night-before template generation.
If templates weren't generated last night, generates them now for today.
"""

import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(SCRIPT_DIR, 'morning_catchup.log')

sys.path.insert(0, SCRIPT_DIR)


def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line)
    with open(LOG_PATH, 'a') as f:
        f.write(line + '\n')


def main():
    from catchup_check import needs_catchup, record_run
    needed, today, reason = needs_catchup()
    log(reason)

    if not needed:
        return

    log(f'Running catch-up template generation for {today}...')
    try:
        from workflow_nightbefore import run
        run(target_date=today)
        record_run(today)
        log('Catch-up complete.')
    except Exception as e:
        log(f'Catch-up failed: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
