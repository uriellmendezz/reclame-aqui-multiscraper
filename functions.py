import os, random, time, datetime, sqlite3, pandas as pd, argparse

def calculate_process_duration(start, end):
    total = end - start
    formatted = datetime.timedelta(seconds=total)
    return  str(formatted)


def random_sleep_time(min, max):
    if max <= min:
        raise ValueError('max must be greater than min')
    
    sleep_time = random.uniform(max, min)
    time.sleep(sleep_time)