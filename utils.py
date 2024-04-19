import argparse, pandas as pd
from scraper import ScraperReclameAqui
from functions import random_sleep_time
import datetime

class ArgumentsParse:
    def arguments(self):
        parser = argparse.ArgumentParser(description='Scraping Reclamaqui')

        company_choices = ['last complains','problems','index evolution']
        
        parser.add_argument('-e','--extract',
                            choices=['category', 'categories', 'company', 'companies'],
                            metavar='CHOICE',
                            type=str,
                            help='Specify the name of the group from which you want to extract data.',
                            required=True)
        
        parser.add_argument('-d', '--data',
                            choices=company_choices,
                            metavar='DATA',
                            type=str,
                            help='What type of information do you want to extract from the company.',
                            required=False)
        
        parser.add_argument('-l', '--link',
                            metavar='METHOD',
                            type=str,
                            help='Chose a method',
                            required=False)
        
        parser.add_argument('-o', '--output',
                            metavar='FILENAME',
                            type=str,
                            help='Output filename',
                            required=True)
        
        parser.add_argument('-f', '--filename',
                            metavar='FILENAME',
                            type=str,
                            help='Filename to read.',
                            required=False)
        
        self.args = parser.parse_args()

    def execute_arguments(self, scraper:ScraperReclameAqui):

        if self.args.extract is not None:
            extract = self.args.extract
        if self.args.data is not None:
            data_ = self.args.data
        if self.args.link is not None:
            link = self.args.link if self.args.link[-1] == '/' else  self.args.link + '/'
        output = self.args.output
        if self.args.filename is not None:
            filename = self.args.filename

        # Category & Categories
        if extract == 'category':
            if output.endswith(('.csv', '.xlsx')):
                if link:
                    try:
                        data = scraper.get_companies_from_category(link)
                        print(data.head(10))
                        data.to_csv(output, index=False) if output.endswith('.csv') else data.to_excel(output, index=False)

                    except Exception as e:
                        print(e)

                else:
                    print('[-l LINK] argument is mandatory to scrape "category"')
            else:
                print('Only CSV files and Excel are allowed as output file format (.csv, .xlsx)')


        if extract == 'categories':
            if output.endswith(('.csv', '.xlsx')):
                if filename.endswith(('.csv', '.xlsx')):
                    categories_df = pd.read_csv(filename) if filename.endswith('.csv') else pd.read_excel(filename)

                    resutls = []
                    links = categories_df.link.dropna().unique().tolist()
                    for link in links:
                        companies = scraper.get_companies_from_category(link)
                        resutls.append(companies)
                        random_sleep_time(1.6, 3.7)
                    
                    try:
                        concated = scraper.concat_dataframes(resutls)
                        now = str(datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d-%H-%M-%S'))
                        if output.endswith('.csv'):
                            outfile = output.split('.csv')[0] + '-' + now + '.csv'
                            concated.to_csv(outfile, index=False)
                        else:
                            outfile = output.split('.xlsx')[0] + '-' + now + '.xlsx'
                            concated.to_excel(outfile, index=False)
                    
                    except Exception as e:
                        print(e)
                        print(f'Fail to download {output}')
                else:
                    print('[-f FILENAME] only accept CSV (.csv) or Excel (.xlsx) files.')


            else:
                print('Only CSV files and Excel are allowed as output file format (.csv, .xlsx)')
                


        # Company & Companies
        if extract == 'company':
            if output.endswith(['.csv', '.xlsx']):
                if data_:
                    if link:
                        if data_.lower() == 'last complains':
                            try:
                                pending = scraper.scrape_company_claims(link, 'pending', 10)
                                answered = scraper.scrape_company_claims(link, 'answered', 10)
                                data = scraper.concat_dataframes([pending, answered])
                                print(data.head(10))
                                data.to_csv(output, index=False) if output.endswith('.csv') else data.to_excel(output, index=False)
                                
                            except Exception as e:
                                print(e)

                        elif data_.lower() == 'problems':
                            try:
                                data = scraper.scrape_company_MainProblems(link)
                                problems = scraper.get_MainProblems_problems(data, link)
                                categories = scraper.get_MainProblems_categories(data, link)
                                products = scraper.get_MainProblems_products(data, link)

                                full_concated = scraper.concat_dataframes([problems, categories, products])
                                print(full_concated.head(10))
                                full_concated.to_csv(output, index=False) if output.endswith('.csv') else full_concated.to_excel(output, index=False)

                            except Exception as e:
                                print(e)

                        else:
                            try:
                                data = scraper.scrape_company_Evolution(link)
                                print(data.head(10))
                                data.to_csv(output, index=False) if output.endswith('.csv') else data.to_excel(output, index=False)

                            except Exception as e:
                                print(e)

                    else:
                        print('Insert the following argument please: [-l LINK]')

            else:
                print('Only CSV files and Excel are allowed as output file format (.csv, .xlsx)')


        if extract == 'companies':
            print('Empezando a scrapear companies')
            if output.endswith(('.csv', '.xlsx')):
                if filename:
                    if filename.endswith(('.csv', '.xlsx')):
                        input_data = pd.read_excel(filename) if filename.endswith('.xlsx') else pd.read_csv(filename)
                        companies = input_data.link.dropna().unique().tolist()

                        lastComplains = []
                        problemsTypes = []
                        indexEvolution = []

                        for companyLink in companies:
                            try:
                                random_sleep_time(0.6, 3.5)
                                pending = scraper.scrape_company_claims(companyLink, 'pending', 10)
                                answered = scraper.scrape_company_claims(companyLink, 'answered', 10)
                                concated = scraper.concat_dataframes([pending, answered])
                                lastComplains.append(concated)
                            except Exception as e:
                                print(e)
                                print('Error:', companyLink)
                                pass

                           
                            try:
                                random_sleep_time(0.6, 3.5)
                                data = scraper.scrape_company_MainProblems(companyLink)
                                problems = scraper.get_MainProblems_problems(data, companyLink)
                                categories = scraper.get_MainProblems_categories(data, companyLink)
                                products = scraper.get_MainProblems_products(data, companyLink)

                                full_concated = scraper.concat_dataframes([problems, categories, products])
                                problemsTypes.append(full_concated)
                            except Exception as e:
                                print(e)
                                print('Error:', companyLink)
                                pass

                            try:
                                random_sleep_time(0.6, 3.5)
                                data = scraper.scrape_company_Evolution(companyLink)
                                indexEvolution.append(data)        
                            except Exception as e:
                                print(e)
                                print('Error:', companyLink)
                                pass
                            
                        dataframe_lastClaims = scraper.concat_dataframes(lastComplains)
                        dataframe_problemsTypes = scraper.concat_dataframes(problemsTypes)
                        dataframe_indexEvolution = scraper.concat_dataframes(indexEvolution)

                        print(dataframe_lastClaims.head(10))
                        print(dataframe_problemsTypes.head(10))
                        print(dataframe_indexEvolution.head(10)) 

                        now = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d-%H-%M-%S')
                        if output.endswith('.csv'):
                            filename_output = output.split('.csv')[0] + '-CHANGE-' + str(now) + '.csv'
                            dataframe_lastClaims.to_csv(filename_output.replace('-CHANGE-', '-lastClaims-'), index=False)
                            dataframe_problemsTypes.to_csv(filename_output.replace('-CHANGE-', '-problems-'), index=False)
                            dataframe_indexEvolution.to_csv(filename_output.replace('-CHANGE-', '-indexEvolution-'), index=False)
                        else:
                            filename_output = output.split('.xlsx')[0] + '-CHANGE-' + str(now) + '.xlsx'
                            dataframe_lastClaims.to_csv(filename_output.replace('-CHANGE-', '-lastClaims-'), index=False)
                            dataframe_problemsTypes.to_csv(filename_output.replace('-CHANGE-', '-problems-'), index=False)
                            dataframe_indexEvolution.to_csv(filename_output.replace('-CHANGE-', '-indexEvolution-'), index=False)
                                          
                else:
                    print('[-f FILENAME] is mandatory for [-e "companies"]')
            else:
                print('Only CSV files and Excel are allowed as output file format (.csv, .xlsx)')
