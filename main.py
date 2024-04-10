import random, time, requests, json, os, sqlite3, pandas as pd, datetime
from driver import ChromeDriverReclameAQUI
import constants, functions
from constants import HEADERS
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

payload = ""

class ScraperReclameAqui:

    def request_get(self, url):
        """
        Make a request to a page using cookies and headers predefined.
        """

        response = requests.request(method='GET', url=url, data=payload, headers=HEADERS)
        if response.status_code == 200:
            return response
        else:
            raise Exception("failed request")

    def parse_html(self, response):
        """
        Take the response from a request and parse it using BeautifulSoup.
        """
        try:
            return BeautifulSoup(response.content, 'html.parser')
        except:
            raise Exception("can't parse html")
        
    def get_all_companies(self):
        """
        This function scrape all the existing companies from Reclame AQUI website.
        It iterates each category of the page and saves the results in an array. Then
        convert this array into a pandas DataFrame and return it.
        """
        results = []

        with open('categories.json', 'r') as jfile:
            categories_links = json.load(jfile)

        for category_url in categories_links:
            if category_url[-1] == '/':
                category_name = category_url.split('/')[-2]
            else:
                category_url = category_url.split('/')[-1]

            for score in ['best', 'worst']:
                for n in range(1, 20):
                    url = f"https://iosearch.reclameaqui.com.br/raichu-io-site-search-v1/segments/ranking/{score}/{category_name}/{n}/10"

                    response = requests.request("GET", url, data=payload, headers=HEADERS)
                    if response.status_code == 200:
                        data = response.json()
                        for row in data['companies']:
                            results.append(row)

                        functions.random_sleep_time(0.5, 2.15)

                    else:
                        break

        dataframe = pd.json_normalize(results)
        dataframe = self.clean_dataframe(dataframe)
        dataframe.to_csv('all_companies.csv', index=False)

    def get_companies_from_category(self, company_link):
        """
        Crawl through a specific category to find companies.
        Return a pandas DataFrame with each company in the category.
        """
        if company_link[-1] == '/':
            category_name = company_link.split('/')[-2]
        else:
            company_link = company_link.split('/')[-1]

        results = []
        for score in ['best', 'worst']:
            for n in range(1, 20):
                url = f"https://iosearch.reclameaqui.com.br/raichu-io-site-search-v1/segments/ranking/{score}/{category_name}/{n}/10"

                response = requests.request("GET", url, data=payload, headers=HEADERS)
                if response.status_code == 200:
                    data = response.json()
                    for row in data['companies']:
                        results.append(row)

                    functions.random_sleep_time(0.55, 2.15)
                else:
                    break

        dataframe = pd.json_normalize(results)
        dataframe = self.clean_dataframe(dataframe)
        return dataframe

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
            'hasLeadButton'
        ]

        column_to_rename = {
            "id": "idCompany",
            "mainSegmentName": "segmentName",
            "mainSegmentShortname": "segmentShortName",
            "secondarySegmentName": "categoryName",
            "secondarySegmentShortname": "categoryShortName",
            "companyIndex": "companyReputation",
            "points": "companyPoints"
        }

        return dataframe.drop(columns=columns_to_drop).rename(columns=column_to_rename)
    
    def scrape_company_id(self, company_shortname, connection, cursor):
        url = f"https://www.reclameaqui.com.br/empresa/{company_shortname}/"
        response = requests.request('GET', url=url, data=payload, headers=HEADERS)
        if response.status_code == 200:
            soup = self.parse_html(response)
            try:
                company_id = soup.find('a', {'id':'cta-header-complain'}).get('href').split('/')[-2]
                if company_id != None:
                    cursor.execute('INSERT INTO CompaniesIds (shortName, id) VALUES (?, ?);',
                                (str(company_shortname), str(company_id)))
                    connection.commit()
                return company_id
            except Exception as e:
                print(e)

        else:
            print('bad requests.', response)
            
    def get_company_id(self, company_shortname, connection, cursor):
        try:
            cursor.execute('SELECT id FROM CompaniesIds WHERE shortName = ?;', (company_shortname,))
            return cursor.fetchone()[0]
        except:
            print('Id company not in database.')

    def scrape_company(self, company_shortname, connection, cursor):
        id_company = self.get_company_id(company_shortname, connection, cursor)
        url = f"https://iosite.reclameaqui.com.br/raichu-io-site-v1/company/indexevolution/{id_company}"

        try:
            response = self.request_get(url)
            data = response.json()['snapshots']
            return pd.json_normalize(data)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    start = time.time()
    url = "https://www.reclameaqui.com.br/segmentos/bancos-e-financeiras/bancos-digitais/"
    companies_shortnames = pd.read_csv('all_companies.csv').companyShortname.unique()

    scraper = ScraperReclameAqui()    

    '''connection = functions.connect_database()
    cursor = connection.cursor()
    cursor.execute("SELECT shortName FROM CompaniesIds")
    already_tracked = cursor.fetchall()
    no_tracked_companies = [c for c in companies_shortnames if (c,) not in already_tracked]
    
    for index, company in enumerate(no_tracked_companies[:1000]):
        id = scraper.scrape_company_id(company, connection=connection, cursor=cursor)
        print(f'{index} --- company: {company} --- id: {id} --- {datetime.datetime.now()}')
        functions.random_sleep_time(2.3, 4.2)'''
    
    connection = functions.connect_database()
    cursor = connection.cursor()

    data = scraper.scrape_company('inter', connection, cursor)
    print(data.head(7))


    end = time.time()
    print(functions.calculate_process_duration(start, end))

