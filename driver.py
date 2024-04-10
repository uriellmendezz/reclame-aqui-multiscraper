from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, StaleElementReferenceException
import functions

from bs4 import BeautifulSoup
import datetime, os, constants, pandas as pd, time, random, functions


class ChromeDriverReclameAQUI:
    def __init__(self, driver_path, chrome_path):
        self.driver_path = driver_path
        self.chrome_path = chrome_path

    def Initialize_WebDriver(self) -> None:
        '''
        Function to start and initialize a webdriver from Selenium
        '''

        chromedriver_path = constants.driver_path
        service = Service(chromedriver_path)
        options = webdriver.ChromeOptions()
        options.add_argument('start-maximized')
        options.binary_location = self.chrome_path
        self.driver = webdriver.Chrome(service=service, options=options)

    def Get_HTML_Parsed(self, link) -> BeautifulSoup:
        '''
        Function to get the HTML content of an URL and parse it using BeautifulSoup
        '''

        try:
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            return soup
        except Exception as e:
            print(e)
            return None
        
    def Get_Categories(self) -> pd.DataFrame:
        '''
        Function to get all the existing categories in reclameaqui.com.br website 
        Return a dataframe with the columns "category", "segment" and "category_link"
        '''

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

    def Accept_Cookies(self) -> None:
        '''
        Function to accept the cookies button if is neccesary.
        '''

        try:
            cookies = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@class="cc-btn cc-allow cc-btn-format"]'))
            )
            cookies.click()
        except (NoSuchElementException, TimeoutException):
            pass

    def Next_View(self) -> None:
        '''
        Function to got to the next page
        '''

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

    def Scrape_Companies_Links(self, link_category) -> pd.DataFrame:
        '''
        Funtion to scrape all companies (best and worst) from an especific link category.
        Return a pandas DataFrame with the category name, the segment its represent, the link of the category
        and the ranking that the company has on reclameaqui.com.br

        '''
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
                data['link'] = links
                data['ranking'] = 'best'

                        
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
                    data['link'] = links
                    data['ranking'] = 'worst'
                            
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


    def Scrape_Last_Claims(self, soup):
        quejas_data = {'claim_title':[], 'claim_text':[], 'claim_status':[],'claim_longevity':[]}
        try:
            try:
                ultimas_quejas = soup.find_all('div', 'sc-1pe7b5t-0 eJgBOc')
                for index, sample in enumerate(ultimas_quejas):
                    claim_title = sample.find('h4').text
                    claim_text = sample.find('p').text
                    claim_status = sample.find('span').text
                    claim_longevity = sample.find('span', 'sc-1pe7b5t-5 dspDoZ').text

                    quejas_data['claim_title'].append(claim_title)
                    quejas_data['claim_text'].append(claim_text)
                    quejas_data['claim_status'].append(claim_status)
                    quejas_data['claim_longevity'].append(claim_longevity)

                df = pd.DataFrame(quejas_data)
                return df
            except NoSuchElementException:
                return pd.DataFrame()
    
        except Exception as e:
            print(e)
            return pd.DataFrame()

    def Scrape_Main_Stats(self, soup):
        try:
            tiempo_en_ra = soup.find('div', 'sc-jr2qk-14').find('p').text
            visitas = soup.find('div', 'ra-since').find('a').text
            temporal = soup.find('div', 'sc-jr2qk-9 eBhYhe').text
            reputation = soup.find('span', 'go1306724026').text

            main_stats = {
                'longevity':[tiempo_en_ra],
                'views':[visitas],
                'temporal':[temporal],
                'reputation':[reputation]
            }
            df = pd.DataFrame(main_stats)
            return df

        except Exception as e:
            print(e)
            return pd.DataFrame()
        
    def Scrape_Claims_Categories(self, soup):
        try:
            right_tables = soup.find_all('div', 'sc-1h9pg1g-5 fRkzcV')
            data_tables = []
            for table in right_tables[1:]:
                table_name = table.find('h6').text
                table_values = [e.get('title') for e in table.find_all('div', 'sc-1h9pg1g-7 cxiSan')]
                for v in table_values:
                    data_tables.append((table_name, v))

            df = pd.DataFrame(data_tables, columns=['table', 'value'])
            return df

        except Exception as e:
            print(e)
            return pd.DataFrame()

    def Get_Claims(self, link_company):
        link = link_company + 'lista-reclamacoes/'
        self.driver.get(link)
        try:
            self.Accept_Cookies()
            ver_mas = self.driver.find_elements(By.XPATH, '//button[@class="sc-aXZVg kRkmJn"]')
            for btn in ver_mas:
                btn.click()
                time.sleep(0.18)
        except Exception as e:
            print(e)

        soup = self.Get_HTML_Parsed(link)
        self.driver.implicitly_wait(5)

        stats = self.Scrape_Main_Stats(soup)
        stats['company'] = link_company.split('/')[-2]

        last_claims = self.Scrape_Last_Claims(soup)
        last_claims['company'] = link_company.split('/')[-2]

        claims_categories = self.Scrape_Claims_Categories(soup)
        claims_categories['company'] = link_company.split('/')[-2]

        return [last_claims, stats, claims_categories]

    def Get_About(self, link_company):
        about_link = link_company + 'sobre/'
        self.driver.get(about_link)
        soup = self.Get_HTML_Parsed(about_link)

        try:
            about_company = soup.find('p', 'go1458712046').text
        except:
            about_company = ''
        try:
            cnpj = soup.find('p', 'go1029472829').text
        except:
            about_company = ''
        try:
            legal_name = soup.find('p', 'go509096957').text
        except:
            about_company = ''
        try:
            website_link = soup.find('a', 'sc-118qix7-0 eLwHfG').get('href')
        except:
            about_company = ''

        data = {
            'about':about_company,
            'CNPJ_number': cnpj,
            'legal_name': legal_name,
            'website_link': website_link
        }

        df = pd.DataFrame(data)
        return df

    def Scrape_Company_Performance(self, link_company):
        self.driver.get(link_company)
        self.Accept_Cookies()
        try:
            self.driver.implicitly_wait(5)
            buttons_temporal = self.driver.find_elements(By.XPATH, '//button[contains(@id, "newPerformanceCard-tab-")]')
        except Exception as e:
            print(e)

        data = {
            'period-time': [],
            'Total Claims': [],
            'Reply Percentage': [],
            'Claims Waiting': [],
            'Average Rating': [],
            'Satisfied Clients': [],
            'Solved Claims Percentage': [],
            'Average Response Time': [],
            'Period': []
        }
        
        try:
            for btn in buttons_temporal:
                rango = btn.text
                WebDriverWait(self.driver, 4).until(EC.element_to_be_clickable(btn)).click()
                soup = self.Get_HTML_Parsed(self.driver.page_source)

                '''total_claims = soup.find(string=lambda text:  text and 'Esta empresa recebeu' in text).parent.text
                reply_percentage = soup.find(string=lambda text:  text and 'Respondeu das reclamações recebidas.' in text).parent.text
                claims_waiting = soup.find(string=lambda text:  text and 'aguardando resposta.' in text).parent.text
                nota_media = soup.find(string=lambda text:  text and ' avaliadas, e a nota média dos consumidores' in text).parent.text
                satisfied_clients = soup.find(string=lambda text:  text and 'Dos que avaliaram, ' in text).parent.text
                solved_claims_percentage = soup.find(string=lambda text:  text and 'A empresa resolveu das reclamações recebidas.' in text).parent.text
                average_response_time = soup.find(string=lambda text:  text and 'O tempo médio de resposta é' in text).parent.text
                periodo = soup.find(string=lambda text:  text and 'Os dados correspondem ao período de' in text).parent.text
                
                data['period-time'].append(rango)
                data['Total Claims'].append(total_claims)
                data['Reply Percentage'].append(reply_percentage)
                data['Claims Waiting'].append(claims_waiting)
                data['Average Rating'].append(nota_media)
                data['Satisfied Clients'].append(satisfied_clients)
                data['Solved Claims Percentage'].append(solved_claims_percentage)
                data['Average Response Time'].append(average_response_time)
                data['Period'].append(periodo)'''

                self.random_sleep_time(0.3, 1.6)
        except Exception as e:
            print(e)
    
        df = pd.DataFrame(data)
        return df
    
    def get_id_company(self, company_shortname, connection, cursor):
        cursor.execute('SELECT id FROM CompaniesIds WHERE shortName = ?;', (company_shortname,))
        row = cursor.fetchone()

        if row:
            return row[0]
        else:
            url = f"https://www.reclameaqui.com.br/empresa/{company_shortname}/"
            self.driver.get(url)
            IdCompany = self.driver.find_element(By.ID, 'cta-header-complain').get_attribute('href').split('/')[-2]
            cursor.execute('INSERT INTO CompaniesIds (shortName, id) VALUES (?, ?);', (str(company_shortname), str(IdCompany)))
            connection.commit()
            return IdCompany


if __name__ == '__main__':
    time_start = time.time()
    scraper = ChromeDriverReclameAQUI(
        constants.driver_path,
        constants.chrome_path
    )

    scraper.Initialize_WebDriver()

    scraper.driver.quit()
    time_finish = time.time()
    total_time = functions.calculate_process_duration(time_start, time_finish)
    print(total_time)

