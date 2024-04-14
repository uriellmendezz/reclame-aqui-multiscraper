from scraper import ScraperReclameAqui
from constants import HEADERS
from functions import random_sleep_time, calculate_process_duration, connect_database
import time, pandas as pd, random

if __name__ == "__main__":
    start = time.time()
    scraper = ScraperReclameAqui()
    sample_company_shortname = 'mercado-livre'

# Query data from Database:
    # ✅ Query a Id from the database of an specific company.
    '''sample_company_shortname = 'inter'
    company_id = scraper.scrape_company_id(sample_company_shortname)
    print(company_id)'''

# Scrape data from the web:

    # ✅ Get companies from an specific category on the website
    '''sample_category_url = "https://www.reclameaqui.com.br/segmentos/apostas/casa-de-aposta/" 
    categories = scraper.get_companies_from_category(sample_category_url)
    print(categories.head())'''

    # ✅ Request the Id from an specific company.
    '''sample_company_shortname = 'inter'
    company_id = scraper.get_company_id(sample_company_shortname)
    print(company_id)'''

    # ✅ Request the Index Evolution of an specific company.
    '''evolution_data = scraper.scrape_company_Evolution(sample_company_shortname)
    print(evolution_data)'''

    # ✅ Request the Main Problems section of an scpecific company.
    '''main_problems = scraper.scrape_company_MainProblems(sample_company_shortname)'''

    # ✅ Request the Problems section of Main Problems from a specific company.
    '''problems_company = scraper.get_MainProblems_problems(main_problems)
    print(problems_company.head(10))'''

    # ✅ Request the Categories problems section of Main Problems from a specific company.
    '''categories_problems_company = scraper.get_MainProblems_categories(main_problems)
    print(categories_problems_company.head(10))'''

    # ✅ Request the Products problems section of Main Problems from a specific company.
    '''products_problems_company = scraper.get_MainProblems_products(main_problems)
    print(products_problems_company.head(10))'''

    # ✅ Scrape the last complains of an specific company. (could be the "pending" or "answered" complains)
    '''answered_complains = scraper.scrape_company_claims(sample_company_shortname, 'answered', n=5)
    pending_complains = scraper.scrape_company_claims(sample_company_shortname, 'pending', n=5)

    print(answered_complains.head())
    print(pending_complains.head())'''

    ids = ['7936', '10023', '12949', '2406']
    evolutions = []
    claims = []
    complains = []

    for id in ids:
        e,cl,c = scraper.pipeline(id)
        evolutions.append(e)
        claims.append(cl)
        complains.append(c)

    evolutions_df = pd.concat(evolutions).reset_index(drop=True)
    claims_df = pd.concat(claims).reset_index(drop=True)
    complains_df = pd.concat(complains).reset_index(drop=True)

    evolutions_df.to_csv('results-dataframes/evolutions.csv', index=False)
    claims_df.to_csv('results-dataframes/claims.csv', index=False)
    complains_df.to_csv('results-dataframes/complains.csv', index=False)








    end = time.time()
    total_time = calculate_process_duration(start, end)
    print(f'\n\n{total_time}')
