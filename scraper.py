import time, requests, sqlite3, pandas as pd, os
from functions import random_sleep_time, calculate_process_duration
from constants import HEADERS
from bs4 import BeautifulSoup

class ScraperReclameAqui:

    def __init__(self):
        self.connection = self.connect_database()
        self.cursor = self.connection.cursor()

    def connect_database(self):
        if not os.path.exists('database.db'):
            connection = sqlite3.connect("database.db")
            cursor = connection.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS CompaniesData (
                    companyName INTEGER,
                    companyShortname TEXT,
                    companyId TEXT
                )''')

            data = self.crawl_all_companies(7000)
            self.insert_data_into_database(data)

            connection.commit()
            return connection
        else:
            connection = sqlite3.connect("database.db")
            return connection
        
    
    def request_get(self, url):
        """Make a request to a page using cookies and headers predefined."""
        response = requests.request(method='GET', url=url, data="", headers=HEADERS)
        if response.status_code == 200:
            return response
        else:
            raise Exception("failed request", response)

    def parse_html(self, response):
        """Take the response from a request and parse it using BeautifulSoup."""
        try:
            return BeautifulSoup(response.content, 'html.parser')
        except:
            raise Exception("can't parse html")
        
    def crawl_all_companies(self, n_rows:int):
        """
        This function scrape all the existing companies from Reclame AQUI website.
        It iterates each category of the page and saves the results in an array. Then
        convert this array into a pandas DataFrame and return it.
        """
        dfs = []
        url = f"https://iosite.reclameaqui.com.br/raichu-io-site-v1/company/rankings/{n_rows}"
        response = self.request_get(url)
        data_json = response.json()

        if data_json:
            for key in data_json.keys():
                df = pd.json_normalize(data_json[key])[['companyName', 'companyShortname', 'companyId']]
                dfs.append(df)
            try:
                full_dataframe = pd.concat(dfs).drop_duplicates(subset='companyId')
                return full_dataframe
            except Exception as e:
                print(f"Error on getting all companies: {e}")
                return None
        else:
            print("No data found.")
            return None

    def insert_data_into_database(self, full_dataframe):
        if full_dataframe is not None:

            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='CompaniesData'")
            table_exists = self.cursor.fetchone()

            if not table_exists:
                # Si la tabla no existe, la creamos
                print('Creating "CompaniesData" table in "database.db"')
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS CompaniesData
                            (companyName TEXT, companyShortname TEXT, companyId TEXT UNIQUE)''')
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
                print('New companies added to database...')
                self.connection.commit()

        else:
            print('The dataframe is empty. No data was inserted into the database.')

    def get_companies_from_category(self, categoryLink) -> pd.DataFrame:
        """
        Crawl through a specific category to find companies. Return a pandas DataFrame with each company in the category."""
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
        Function to clean a dataframe coming from *gees_from_category* function.
        It removes extra columns and rename anothers."""

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
        '''Scrapes the company ID from its Reclame Aqui page.'''
        
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
        '''Gets the company ID from the database, or scrapes it if not found.'''

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
        '''Searches for company information using its ID.'''

        try:
            self.cursor.execute('''SELECT companyName, companyShortname FROM CompaniesData
                                WHERE companyId = ?''', (id,))
            results = self.cursor.fetchone()
            return str(results[0]), str(results[1])
        except Exception as e:
            print(e)
            print('Id not founded.')

    def scrape_company_Evolution(self, companyLink):
        '''Scrapes the evolution data for a company.'''

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
        '''Scrapes the main problems reported for a company.'''

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
        '''Extracts main problem categories from JSON data.'''

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
        '''Extracts main problem types from JSON data.'''

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
        '''
        Extracts main problem products/services from JSON data.
        '''

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
        '''Concatenates a list of DataFrames into one DataFrame.'''

        try:
            return pd.concat(data).reset_index(drop=True)
        except Exception as e:
            print(e)
            return pd.DataFrame()
    

    def clean_company_MainProblems_dataframe(self, df):
        '''Cleans the DataFrame of main problems reported.'''

        return df[['name', 'count', 'recorrencyPercentual']]
    
    def scrape_company_claims(self, companyLink, status:str, n):
        '''Scrapes claims (complaints) for a company based on status and pagination.'''

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

    def scrape_ranking_lists(self, output, n_rows):
        '''Scrapes ranking lists from Reclame Aqui and saves them to an Excel file.'''

        try:
            url = f"https://iosite.reclameaqui.com.br/raichu-io-site-v1/company/rankings/{n_rows}"
            response = self.request_get(url)
            response_json = response.json()

            print(pd.json_normalize(response_json['topScores']).head(10))
            
            with pd.ExcelWriter(output) as writer:
                for k in response_json.keys():
                    df = pd.json_normalize(response_json[k])
                    df.to_excel(writer, sheet_name=f'{k}', index=False)

            print(f'The file "{output}" was downloaded succesfuly.')    

        except Exception as e:
            print(e)
    
    def close_connection(self):
        '''Closes the SQLite database connection.'''
        self.connection.close()

if __name__ == "__main__":
    start = time.time()
    scraper = ScraperReclameAqui()    

    data = scraper.crawl_all_companies(3000)
    print(data.shape)
    print('')
    print(data.head())

    scraper.close_connection()
    end = time.time()
    print(calculate_process_duration(start, end))

