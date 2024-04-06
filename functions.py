import datetime
import time
import pandas as pd
import random
from concurrent.futures import ThreadPoolExecutor

def calculate_process_duration(start, end):
    total = end - start
    formatted = datetime.timedelta(seconds=total)
    return  str(formatted)

def Parellels_Drivers(self, max, urls):
    with ThreadPoolExecutor(max_workers=max) as executor:
        results = executor.map(self.Initialize_and_Scrape_Categories, urls)

    full_df = pd.concat(results, ignore_index=True)
    return full_df

def Random_Sleep_Time(self, min: float, max: float):
    if max <= min:
        raise ValueError('max must be greater than min')
    
    sleep_time = random.uniform(max, min)
    time.sleep(sleep_time)

