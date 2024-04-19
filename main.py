from scraper import ScraperReclameAqui
from constants import HEADERS
from functions import calculate_process_duration
from utils import ArgumentsParse
import time

if __name__ == "__main__":
    start = time.time()
    scraper = ScraperReclameAqui()
    args = ArgumentsParse()
    
    args.arguments()
    args.execute_arguments(scraper)

    end = time.time()
    total_time = calculate_process_duration(start, end)

    print(f'\nProcess duration: ----> {total_time}')
