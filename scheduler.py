import os
import time
from datetime import datetime

from paper_digest import run_once


def main() -> None:
    days = int(os.getenv("DIGEST_DAYS", "7"))
    print("[scheduler] started, run daily at 08:00 local time")

    last_sent_date = None
    while True:
        now = datetime.now()
        if now.hour == 8 and now.minute == 0:
            if last_sent_date != now.date():
                run_once(days=days)
                last_sent_date = now.date()
                print(f"[scheduler] sent digest at {now}")
            time.sleep(60)
        else:
            time.sleep(20)


if __name__ == "__main__":
    while True:
        try:
            main()
            break
        except Exception as e:
            print(f"[scheduler] crashed: {e}, restarting in 10s")
            time.sleep(10)
