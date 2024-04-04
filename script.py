from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, StaleElementReferenceException

from bs4 import BeautifulSoup
import os
import constants
import pandas as pd
import constants
import time


class ScraperReclameAqui:
    def __init__(self, driver_path, chrome_path):
        self.driver_path = driver_path
        self.chrome_path = chrome_path

    def InitializeDriver(self):
        chromedriver_path = constants.chromedriver_exe_path
        service = Service(chromedriver_path)
        options = webdriver.ChromeOptions()
        options.add_argument('start-maximized')
        options.binary_location = self.chrome_path
        self.driver = webdriver.Chrome(service=service, options=options)
        return self.driver

    def Get_HTML(self, url):
        self.driver.get(url)
        try:
            html = self.driver.page_source
            return html
        except:
            return None

    def Parse_HTML(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        return soup