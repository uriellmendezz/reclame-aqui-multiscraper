from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
from concurrent.futures import ThreadPoolExecutor

import datetime
import os
import constants
import pandas as pd
import constants
import time

class ScraperReclameAqui:
    def __init__(self, driver_path, chrome_path):
        self.driver_path = driver_path
        self.chrome_path = chrome_path

    def Initialize_WebDriver(self):
        chromedriver_path = constants.driver_path
        service = Service(chromedriver_path)
        options = webdriver.ChromeOptions()
        options.add_argument('start-maximized')
        options.binary_location = self.chrome_path
        self.driver = webdriver.Chrome(service=service, options=options)
        
    def Get_Categories(self):
        segments_link = "https://www.reclameaqui.com.br/segmentos/"
        self.driver.get(segments_link)
        self.driver.implicitly_wait(5)
        expand_all_categories = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[@class="go2253194569"]'))
        )
        expand_all_categories.click()

        all_categories = {'category':[], 'segment':[], 'category_link':[]}

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
        return dataframe
        # dataframe.to_csv('categories.csv', sep=',', index=False)

    def Accept_Cookies(self):
        try:
            cookies = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@class="cc-btn cc-allow cc-btn-format"]'))
            )
            cookies.click()
        except (NoSuchElementException, TimeoutException):
            pass

    def Next_View(self):
        self.driver.implicitly_wait(2)
        try:    
            siguiente_boton = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//li[@aria-label="botão de próxima página"]'))
            )
            siguiente_boton.click()
        except ElementClickInterceptedException as error_intercepted:
            self.Accept_Cookies()

        except NoSuchElementException:
            pass
    
    def Find_Element_By_Xpath(self, element, xpath):
        try:
            result = element.find_element(By.XPATH, xpath).text
            return result
        except NoSuchElementException:
            return '-'
        except StaleElementReferenceException:
            return '--'
        
    def Find_Element_By_Class(self, element, _class_):
        try:
            result = element.find_element(By.CLASS_NAME, _class_).text
            return result
        except NoSuchElementException:
            return '-'
        except StaleElementReferenceException:
            return '--'

    def Get_Companies_From_Category(self, link_category):
        data = {
            'company_name': [],
            'ranking': [],
            'reputation_label': [],
            'reputation_number': [],
            'total_claims_solved': [],
            'total_claims_unsolved': [],
            'solved_percentage': [],
            'company_points': [],
            'company_ra_link': []}
        
        self.driver.get(link_category)
        self.Accept_Cookies()

        companies_elements = self.driver.find_elements(By.XPATH, '//div[@class="go2321486396"]')
        while True:
            for company in companies_elements:
                company_name = self.Find_Element_By_Xpath(company, '//span[@class="sc-bfhvDw gqNpHh"]')
                ranking = self.Find_Element_By_Class(company,'go2391406422')
                reputation_label = self.Find_Element_By_Class(company, 'go891998899')
                reputation_number = self.Find_Element_By_Class(company, 'go685678325 reputation-label')
                total_claims_solved = self.Find_Element_By_Class(company, 'go4274162446')
                total_claims_unsolved = self.Find_Element_By_Class(company, 'go148473862')
                solved_percentage = self.Find_Element_By_Class(company, 'go148473862')
                company_points = self.Find_Element_By_Class(company, 'go2806989190')
                try:
                    company_ra_link = company.find_element(By.XPATH, '//a[@class="go805020176"]').get_attribute('href')
                except NoSuchElementException:
                    company_ra_link = '--'
                except StaleElementReferenceException:
                    company_ra_link = '--'
                    continue

                # Agrega los datos al diccionario
                data['company_name'].append(company_name)
                data['ranking'].append(ranking)
                data['reputation_label'].append(reputation_label)
                data['reputation_number'].append(reputation_number)
                data['total_claims_solved'].append(total_claims_solved)
                data['total_claims_unsolved'].append(total_claims_unsolved)
                data['solved_percentage'].append(solved_percentage)
                data['company_points'].append(company_points)
                data['company_ra_link'].append(company_ra_link)

            try:    
                siguiente_boton = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//li[@aria-label="botão de próxima página"]'))
                )
                siguiente_boton.click()
                time.sleep(1.5)
            except ElementClickInterceptedException as error_intercepted:
                self.Accept_Cookies()

            except TimeoutException:
                break

        try:
            worst_companies_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="ranking-button-WORST"]'))
            )
            worst_companies_button.click()
            time.sleep(2)
            companies_elements = self.driver.find_elements(By.XPATH, '//div[@class="go2321486396"]')
            while True:
                for company in companies_elements:
                    company_name = self.Find_Element_By_Xpath(company, '//span[@class="sc-bfhvDw gqNpHh"]')
                    ranking = self.Find_Element_By_Class(company,'go2391406422')
                    reputation_label = self.Find_Element_By_Class(company, 'go891998899')
                    reputation_number = self.Find_Element_By_Class(company, 'go685678325 reputation-label')
                    total_claims_solved = self.Find_Element_By_Class(company, 'go4274162446')
                    total_claims_unsolved = self.Find_Element_By_Class(company, 'go148473862')
                    solved_percentage = self.Find_Element_By_Class(company, 'go148473862')
                    company_points = self.Find_Element_By_Class(company, 'go2806989190')
                    try:
                        company_ra_link = company.find_element(By.XPATH, '//a[@class="go805020176"]').get_attribute('href')
                    except NoSuchElementException:
                        company_ra_link = '--'
                    except StaleElementReferenceException:
                        company_ra_link = '--'
                        continue

                    # Agrega los datos al diccionario
                    data['company_name'].append(company_name)
                    data['ranking'].append(ranking)
                    data['reputation_label'].append(reputation_label)
                    data['reputation_number'].append(reputation_number)
                    data['total_claims_solved'].append(total_claims_solved)
                    data['total_claims_unsolved'].append(total_claims_unsolved)
                    data['solved_percentage'].append(solved_percentage)
                    data['company_points'].append(company_points)
                    data['company_ra_link'].append(company_ra_link)
                try:    
                    siguiente_boton = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, '//li[@aria-label="botão de próxima página"]'))
                    )
                    siguiente_boton.click()
                    time.sleep(1.5)

                except ElementClickInterceptedException as error_intercepted:
                    self.Accept_Cookies()

                except TimeoutException:
                    break

        except NoSuchElementException:
            pass

        try:
            dataframe = pd.DataFrame(data)
            dataframe.to_csv('output_categories.csv', index=False)
            return dataframe
        except:
            print('No se puedo crear el dataframe')

    def Next_Page(self):
        try:    
            siguiente_boton = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//li[@aria-label="botão de próxima página"]'))
            )
            siguiente_boton.click()
            time.sleep(1.5)

        except ElementClickInterceptedException as error_intercepted:
            self.Accept_Cookies()

    def Scrape_Companies_Links(self, link_category):
        start = time.time()
        segment = link_category.split('/')[-3].replace('-', ' ').capitalize().strip()
        category = link_category.split('/')[-2].replace('-', ' ').capitalize().strip()
        self.driver.get(link_category)
        time.sleep(2)
        dfs = []
        while True:
            try:
                companies_elements = self.driver.find_elements(By.CLASS_NAME, 'see-company-link')
                links = [e.get_attribute('href') for e in companies_elements]

                data = {}
                data['category'] = [category for x in range(len(links))]
                data['segment'] = [segment for x in range(len(links))]
                data['links'] = links
                        
                dataframe = pd.DataFrame(data)
            except Exception as e:
                dataframe = pd.DataFrame()

            dfs.append(dataframe)

            try:
                self.Next_Page()
            except TimeoutException:
                break

        try:
            worst_companies_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@data-testid="ranking-button-WORST"]'))
            )
            worst_companies_button.click()
            time.sleep(2)
            while True:
                try:
                    companies_elements = self.driver.find_elements(By.CLASS_NAME, 'see-company-link')
                    links = [e.get_attribute('href') for e in companies_elements]

                    data = {}
                    data['category'] = [category for x in range(len(links))]
                    data['segment'] = [segment for x in range(len(links))]
                    data['links'] = links
                            
                    dataframe = pd.DataFrame(data)
                except Exception as e:
                    dataframe = pd.DataFrame()

                dfs.append(dataframe)

                try:
                    self.Next_Page()
                except TimeoutException:
                    break

        except:
            pass
    
        full_df = pd.concat(dfs, ignore_index=True)
        return  full_df
        # full_df.to_csv('output_categories.csv', index=False)
        # finish = time.time()
        # total_time = finish - start
        # formatted_total_time = datetime.timedelta(seconds=total_time)
        # print('Proceso Finalizado:', formatted_total_time)
    
    def Quit_Driver(self):
        self.driver.quit()
        
    def Initialize_and_Scrape_Categories(self, link_category):
        driver_instance = self.Initialize_WebDriver()
        data = self.Scrape_Companies_Links(link_category)
        self.driver.quit()
        return data

                
    def Parellels_Drivers(self, max, urls):
        with ThreadPoolExecutor(max_workers=max) as executor:
            results = executor.map(self.Initialize_and_Scrape_Categories, urls)

        full_df = pd.concat(results, ignore_index=True)
        return full_df


if __name__ == '__main__':
    client = ScraperReclameAqui(
        constants.driver_path,
        constants.chrome_exe_path
    )

    client.Initialize_WebDriver()
    # categories = pd.read_csv('categorias.csv', sep=',')
    # df = client.Get_Companies_From_Category(categories.iloc[1].category_link)
    url = "https://www.reclameaqui.com.br/segmentos/bancos-e-financeiras/consorcios/"
    df = client.Scrape_Companies_Links(url)
    print(df.head(15))

