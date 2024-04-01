from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException

import os
import constants
import pandas as pd
import constants

class ScraperReclameAqui:
    def __init__(self, chromedriver_exe_path, chromeapp_exe_path):
        self.chromedriver_exe_path = chromedriver_exe_path
        self.chromeapp_exe_path = chromeapp_exe_path

    def Initialize_WebDriver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('start-maximized')
        options.binary_location = self.chromeapp_exe_path
        self.driver = webdriver.Chrome(self.path_to_webdriver_driver, options = options)

    def Get_Categories(self):
        expand_all_categories = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@class="go2253194569"]'))
        )
        expand_all_categories.click()

        all_categories = {'category':[], 'category_link':[], 'segment':[]}

        for e in self.driver.find_elements(By.XPATH, '//div[@class="go570287992 acordeon"]'):
            segment = e.find_element(By.CLASS_NAME, 'go4236553472').text.strip()
            categories = e.find_elements(By.XPATH, '//a[@class="go273172331"]')
            for cat in categories:
                cat_name = cat.get_attribute('title')
                cat_link = cat.get_attribute('href')
                all_categories['category'].append(cat_name)
                all_categories['category_link'].append(cat_link)
                all_categories['segment'].append(segment)

        dataframe = pd.DataFrame(all_categories)
        dataframe.to_csv('categories.csv', sep=',', index=False)

    
        
if __name__ == '__main__':
    client = ScraperReclameAqui(
        constants.chromedriver_exe_path,
        constants.chrome_exe_path
    )

    client.Initialize_WebDriver()
    client