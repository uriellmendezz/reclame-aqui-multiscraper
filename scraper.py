import random, time, requests, json, os, sqlite3, pandas as pd, datetime
from functions import random_sleep_time, calculate_process_duration, connect_database
from constants import HEADERS
from bs4 import BeautifulSoup

class ScraperReclameAqui:

    def __init__(self):
        self.connection = sqlite3.connect('database.db')
        self.cursor = self.connection.cursor()

    def request_get(self, url):
        """
        Make a request to a page using cookies and headers predefined.
        """
        response = requests.request(method='GET', url=url, data="", headers=HEADERS)
        if response.status_code == 200:
            return response
        else:
            raise Exception("failed request", response)

    def parse_html(self, response):
        """
        Take the response from a request and parse it using BeautifulSoup.
        """
        try:
            return BeautifulSoup(response.content, 'html.parser')
        except:
            raise Exception("can't parse html")
        
    def get_all_companies(self, max:int):
        """
        This function scrape all the existing companies from Reclame AQUI website.
        It iterates each category of the page and saves the results in an array. Then
        convert this array into a pandas DataFrame and return it.
        """
        dfs = []
        data_json = self.scrape_ranking_lists(max)
        for key in data_json.keys():
            df = pd.json_normalize(data_json[key])[['companyName', 'companyShortname', 'companyId']]
            dfs.append(df)

        full_dataframe = pd.concat(dfs).drop_duplicates(subset='companyId')

        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='CompaniesData'")
        table_exists = self.cursor.fetchone()

        if not table_exists:
            # Si la tabla no existe, la creamos
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS CompaniesData
                           (companyName text, companyShortname text, companyId text UNIQUE)''')
            self.cursor.executemany('''INSERT INTO CompaniesData VALUES (?,?,?)''', full_dataframe.values)
            self.connection.commit()

        else:
            self.cursor.execute('''SELECT DISTINCT companyId FROM CompaniesData''')
            in_database = self.cursor.fetchall()

            in_database_list = [c[0] for c in in_database]
            no_tracked_companies = full_dataframe[~full_dataframe.companyId.isin(in_database_list)]

            self.cursor.executemany('''INSERT OR IGNORE INTO CompaniesData
                               (companyName, companyShortname, companyId) VALUES (?, ?, ?)''',
                               no_tracked_companies.values)
            print('New Companies added to database...')
            self.connection.commit()

    def get_companies_from_category(self, categoryLink) -> pd.DataFrame:
        """
        Crawl through a specific category to find companies.
        Return a pandas DataFrame with each company in the category.
        """
        if '/' in categoryLink:
            if categoryLink[-1] == '/':
                categoryLink = categoryLink.split('/')[-2]
            else:
                categoryLink = categoryLink.split('/')[-1]
            

        results = []
        for score in ['best', 'worst']:
            for n in range(1, 20):
                url = f"https://iosearch.reclameaqui.com.br/raichu-io-site-search-v1/segments/ranking/{score}/{categoryLink}/{n}/10"

                response = requests.request("GET", url, data="", headers=HEADERS)
                if response.status_code == 200:
                    data = response.json()
                    for row in data['companies']:
                        results.append(row)

                    random_sleep_time(1.23, 2.45)
                else:
                    break

        dataframe = pd.json_normalize(results)
        dataframe = self.clean_dataframe(dataframe)
        return dataframe.sort_values('companyName', ascending=True).reset_index(drop=True)

    def clean_dataframe(self, dataframe):
        """
        Function to clean a dataframe coming from *get_companies_from_category* function.
        It removes extra columns and rename anothers.
        """
        columns_to_drop = [
            'logo',
            'promotionValueUnit',
            'promotionValue',
            'promotionText',
            'promotionLink',
            'ctaLink',
            'ctaText',
            'hasLeadButton',
            'id'
        ]

        column_to_rename = {
            "mainSegmentName": "segmentName",
            "mainSegmentShortname": "segmentShortName",
            "secondarySegmentName": "categoryName",
            "secondarySegmentShortname": "categoryShortName",
            "companyIndex": "companyReputation",
            "points": "companyPoints"
        }

        return dataframe.drop(columns=columns_to_drop).rename(columns=column_to_rename)
    
    def scrape_company_id(self, companyShortname):
        url = f"https://www.reclameaqui.com.br/empresa/{companyShortname}/"
        response = requests.request('GET', url=url, data="", headers=HEADERS)
        if response.status_code == 200:
            soup = self.parse_html(response)
            if soup is not None:
                try:
                    company_id = soup.find('a', {'id':'cta-header-complain'}).get('href').split('/')[-2]
                    if company_id is not None:
                        self.cursor.execute('INSERT INTO CompaniesIds (shortName, id) VALUES (?, ?);',
                                    (str(companyShortname), str(company_id)))
                        self.connection.commit()
                    return company_id
                except Exception as e:
                    print(e)
                    return None
        else:
            print('bad requests.', response)
            return None
       
    def get_company_id(self, companyShortname):
        try:
            self.cursor.execute('SELECT companyId FROM CompaniesData WHERE companyShortname = ?;',
                           (companyShortname,))
            return self.cursor.fetchone()[0]
        except Exception as e:
            try:
                return self.scrape_company_id(companyShortname)
            except Exception as e:
                print(e)
                return None
                
    def search_info_company(self, id):
        try:
            self.cursor.execute('''SELECT companyName, companyShortname FROM CompaniesData
                                WHERE companyId = ?''', (id,))
            results = self.cursor.fetchone()
            return str(results[0]), str(results[1])
        except Exception as e:
            print(e)
            print('Id not founded.')

    def scrape_company_Evolution(self, companyLink):
        companyShortname = companyLink.split('/')[-2]
        companyId = self.get_company_id(companyShortname)
        url = f"https://iosite.reclameaqui.com.br/raichu-io-site-v1/company/indexevolution/{companyId}"

        try:
            response = self.request_get(url)
            data = response.json()['snapshots']
            data = pd.json_normalize(data)
            data['companyId'] = companyId
            data['companyShortname'] = companyShortname
            return data.drop(columns=['deleted', 'id', 'legacyId', 'ip', 'modified']).reset_index(drop=True)
        
        except Exception as e:
            print(e)
            return None

    def scrape_company_MainProblems(self, companyLink):
        companyShortname = companyLink.split('/')[-2]
        companyId = self.get_company_id(companyShortname)
        url = f"https://iosearch.reclameaqui.com.br/raichu-io-site-search-v1/query/companyMainProblems/{companyId}"

        try:
            response = self.request_get(url)
            data = response.json()
            data['companyId'] = companyId
            data['companyShortname'] = companyShortname
            return data
        
        except Exception as e:
            print(e)
            return None

    def get_MainProblems_categories(self, json_data, companyLink):
        try:
            companyShortname = companyLink.split('/')[-2]
            id = self.get_company_id(companyShortname)
            data = json_data['complainResult']['complains']['categories']
            data = self.clean_company_MainProblems_dataframe(pd.json_normalize(data))
            data['companyId'] = id
            data['type'] = 'category'
            return data
        except Exception as e:
            print(e)
            return None

    def get_MainProblems_problems(self, json_data, companyLink):
        try:
            companyShortname = companyLink.split('/')[-2]
            id = self.get_company_id(companyShortname)
            data = json_data['complainResult']['complains']['problems']
            data = self.clean_company_MainProblems_dataframe(pd.json_normalize(data))
            data['type'] = 'problem_type'
            data['companyId'] = id
            return data

        except Exception as e:
            print(e)
            return None

    def get_MainProblems_products(self, json_data, companyLink):
        try:
            companyShortname = companyLink.split('/')[-2]
            id = self.get_company_id(companyShortname)
            data = json_data['complainResult']['complains']['products']
            data = self.clean_company_MainProblems_dataframe(pd.json_normalize(data))
            data['companyId'] = id
            data['type'] = 'pruduct&service'
            return data
        except Exception as e:
            print(e)
            return None
        
    def concat_dataframes(self,data:list):
        try:
            return pd.concat(data).reset_index(drop=True)
        except Exception as e:
            print(e)
            return pd.DataFrame()
    

    def clean_company_MainProblems_dataframe(self, df):
        return df[['name', 'count', 'recorrencyPercentual']]
    
    def scrape_company_claims(self, companyLink, status:str, n):
        companyShortname = companyLink.split('/')[-2]
        if status in ['pending', 'Pending', 'PENDING']:
            companyId = self.get_company_id(companyShortname)
            url = f'''https://iosearch.reclameaqui.com.br/raichu-io-site-search-v1/complains?company={companyId}&status=PENDING&evaluated=bool%3Afalse&index=0&offset={n}&order=created&orderType=desc&deleted=bool%3Afalse&fields=evaluated,title,solved,status,created,description'''
            
            try:
                response = self.request_get(url)
                data = response.json()['data']
                data = pd.json_normalize(data)
                data['companyId'] = companyId
                data['companyShortname'] = companyShortname
                return data
            
            except Exception as e:
                print(e)
                return None

        elif status in ['answered', 'Answered', 'ANSWERED']:
            companyId = self.get_company_id(companyShortname)
            url = f'''https://iosearch.reclameaqui.com.br/raichu-io-site-search-v1/complains?company={companyId}&status=ANSWERED&evaluated=bool%3Afalse&index=0&offset={n}&order=created&orderType=desc&deleted=bool%3Afalse&fields=evaluated,title,solved,status,created,description'''
            
            try:
                response = self.request_get(url)
                data = response.json()['data']
                data = pd.json_normalize(data)
                data['companyId'] = companyId
                data['companyShortname'] = companyShortname
                return data
            
            except Exception as e:
                print(e)

        else:
            print('valid status values: "pending" or "answered"')

    def scrape_ranking_lists(self, n_rows):
        try:
            url = f"https://iosite.reclameaqui.com.br/raichu-io-site-v1/company/rankings/{n_rows}"
            response = self.request_get(url)
            response_json = response.json()
            return response_json
        except Exception as e:
            print(e)
            return None
        
    def scrape_company_info(self, companyLink):
        companyShortname = companyLink.split('/')[-2]
        id = self.get_company_id(companyShortname)
        url = f'https://www.reclameaqui.com.br/empresa/{companyShortname}/'
        response = self.request_get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            tiempo = soup.find('div', class_='ra-since').text
            cnpj = soup.find('a', class_='sc-1915fv4-7 fBlHuG').find('span').text
            sobre = soup.find('ul', class_='sc-1915fv4-2 idgfcC').find('li').text
            website = soup.find('a', {'title':'site', 'class':'sc-118qix7-0 eLwHfG'}).get('href')

            print(tiempo)
            print(cnpj)
            print(sobre)
            print(website)
        else:
            print(response)

    def pipeline(self, companyId):
        companyName, companyShortname = self.search_info_company(companyId)

        evolution = self.scrape_company_Evolution(companyShortname)
        random_sleep_time(min=1.2, max=3.7)

        pending_claims = self.scrape_company_claims(companyShortname, 'pending',n=10)
        random_sleep_time(min=1.2, max=3.7)

        answered_claims = self.scrape_company_claims(companyShortname, 'answered',n=10)
        random_sleep_time(min=1.2, max=3.7)

        complains_general = self.scrape_company_MainProblems(companyShortname)
        random_sleep_time(min=1.2, max=3.7)

        complains_problems = self.get_MainProblems_problems(complains_general, companyId)
        complains_categories = self.get_MainProblems_categories(complains_general, companyId)
        complains_products = self.get_MainProblems_products(complains_general, companyId)

        complains = pd.concat([complains_categories, complains_problems, complains_products]).reset_index(drop=True)
        claims = pd.concat([pending_claims, answered_claims]).reset_index(drop=True)

        return evolution, claims, complains
    
    def close_connection(self):
        self.connection.close()

if __name__ == "__main__":
    start = time.time()
    scraper = ScraperReclameAqui()    

    data = scraper.scrape_company_Evolution("https://www.reclameaqui.com.br/empresa/extrafarma/")
    print(data)

    scraper.close_connection()
    end = time.time()
    print(calculate_process_duration(start, end))

