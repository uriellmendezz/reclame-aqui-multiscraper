import argparse
from scraper import ScraperReclameAqui

class ArgumentsParse:
    def arguments(self):
        parser = argparse.ArgumentParser(description='Scraping Reclamaqui')

        company_choices = ['last complains','problems','index evolution']
        
        parser.add_argument('-e','--extract', choices=['category', 'categories', 'company', 'companies'], metavar='CHOICE', type=str, help='Extract data')
        parser.add_argument('-d', '--data', choices=company_choices, metavar='DATA', type=str, help='Data you want to scrape')
        parser.add_argument('-l', '--link', metavar='METHOD', type=str, help='Chose a method')
        parser.add_argument('-o', '--output', metavar='FILENAME', type=str, help='Output filename', required=True)

        self.args = parser.parse_args()

    def execute_arguments(self, scraper:ScraperReclameAqui):

        extract = self.args.extract
        data_ = self.args.data
        link = self.args.link if self.args.link[-1] == '/' else  self.args.link + '/'
        output = self.args.output

        if extract == 'category':
            if link:
                try:
                    data = scraper.get_companies_from_category(link)
                    if output:
                        if '.csv' in output:
                            data.to_csv(output, index=False)
                        elif any(x in output for x in ['.xlsx', '.xls']):
                            data.to_excel(output, index=False)
                        else:
                            print('Only CSV files and Excel are allowed as output file format')

                except Exception as e:
                    print(e)
            else:
                print('Insert the category link please.')

        # Company
        if extract == 'company':
            if any(e in output for e in ['.csv', '.xlsx', '.xls']):
                if data_:
                    if link:
                        if data_.lower() == 'last complains':
                            try:
                                pending = scraper.scrape_company_claims(link, 'pending', 10)
                                answered = scraper.scrape_company_claims(link, 'answered', 10)
                                data = scraper.concat_dataframes([pending, answered])
                                if '.csv' in output:
                                    data.to_csv(output, index=False)
                                elif any(x in output for x in ['.xlsx', '.xls']):
                                    data.to_excel(output, index=False)
                                else:
                                    print('Only CSV files and Excel are allowed as output file format')
                            except Exception as e:
                                print(e)

                        elif data_.lower() == 'problems':
                            try:
                                data = scraper.scrape_company_MainProblems(link)
                                problems = scraper.get_MainProblems_problems(data, link)
                                categories = scraper.get_MainProblems_categories(data, link)
                                products = scraper.get_MainProblems_products(data, link)

                                full_concated = scraper.concat_dataframes([problems, categories, products])
                                if '.csv' in output:
                                    full_concated.to_csv(output, index=False)
                                elif any(x in output for x in ['.xlsx', '.xls']):
                                    full_concated.to_excel(output, index=False)
                                else:
                                    print('Only CSV files and Excel are allowed as output file format')
                            except Exception as e:
                                print(e)

                        else:
                            try:
                                data = scraper.scrape_company_Evolution(link)
                                if '.csv' in output:
                                    data.to_csv(output, index=False)
                                elif any(x in output for x in ['.xlsx', '.xls']):
                                    data.to_excel(output, index=False)
                                else:
                                    print('Only CSV files and Excel are allowed as output file format')
                            except Exception as e:
                                print(e)

                    else:
                        print('Insert the following argument please: [-l LINK]')

            else:
                print('Only CSV files and Excel are allowed as output file format (.csv, .xlsx, .xls)')


        if extract == 'companies':
            if link:
                pass
            else:
                print('Insert [-v VALUE] please.')

        if extract == 'categories':
            if link:
                pass
            else:
                print('Insert [-v VALUE] please.')