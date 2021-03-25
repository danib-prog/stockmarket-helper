import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import numpy as np
from copy import copy

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'}

#These are only the columns of balanceSheet that we are interested about
overview_columns = ['Symbol', 'Name', 'Exchange', 'Currency', 'FullTimeEmployees',
                    'LatestQuarter', 'MarketCapitalization', 'EBITDA',
                    'PERatio', 'BookValue', 'DividendPerShare',
                    'DividendYield', 'EPS', 'RevenuePerShareTTM',
                    'ProfitMargin', 'ReturnOnAssetsTTM', 'RevenueTTM',
                    'GrossProfitTTM', 'QuarterlyEarningsGrowthYOY',
                    'QuarterlyRevenueGrowthYOY', 'TrailingPE', 'PriceToBookRatio',
                    'EVToRevenue', '52WeekHigh', '52WeekLow', 'SharesOutstanding',
                    'PercentInsiders', 'PercentInstitutions', 'PayoutRatio',
                    'Graham Number']
#These are only the columns of incomeStatement that we are interested about
income_columns = ['interestExpense', 'operatingExpenses', 'netIncome',
                  'incomeTaxExpense']
#These are only the columns of balanceSheet that we are interested about
balance_columns = ['totalAssets', 'totalLiabilities', 'shortTermDebt',
                   'longTermDebt', 'cashAndShortTermInvestments',
                   'totalShareholderEquity']
#A list of all the columns
all_columns = copy(overview_columns + income_columns + balance_columns)

#A class containing all infos about a publicly traded company
class Stock():
    url = 'https://www.alphavantage.co/query'

    def __init__(self, symbol, apikey):
        self.symbol = symbol
        self.apikey = apikey

        #Setting basic values to back-test and only make an api request if neccessary
        self.overview = ''
        self.incomeStatement = ''
        self.balanceSheet = ''

    def get_overview(self, i):
        if type(self.overview) == type(''):
            payload = {'function': 'OVERVIEW',
                       'symbol': self.symbol,
                       'apikey': self.apikey}
            r = requests.get(self.url, headers=headers, params=payload)
            page_html = r.content
            r.close()

            overview_soup = BeautifulSoup(page_html, "html.parser")
            overview_dict = eval(str(overview_soup))                            #The retrived soup can be implemented as a dictionary

            #Getting the values into a DataFrame I can easily work with
            overview = pd.DataFrame(overview_dict, index=[i,])
            self.overview = overview
            time.sleep(12)
            return overview
        else:
            return self.overview

    def get_incomeStatement(self, i):
        if type(self.incomeStatement) == type(''):
            payload = {'function': 'INCOME_STATEMENT',
                       'symbol': self.symbol,
                       'apikey': self.apikey}
            r = requests.get(self.url, headers=headers, params=payload)
            page_html = r.content
            r.close()

            incomest_soup = BeautifulSoup(page_html, "html.parser")
            incomest_dict = eval(str(incomest_soup))                            #The retrived soup can be implemented as a dictionary

            #Getting the values into a DataFrame I can easily work with
            if incomest_dict:
                latestIncomeStatement_dict = incomest_dict['annualReports'][0]
                latestIncomeStatement = pd.DataFrame(latestIncomeStatement_dict, index=[i,])
                self.incomeStatement = latestIncomeStatement

                time.sleep(12)
                return latestIncomeStatement
            else:
                return pd.DataFrame()

        else:
            return self.incomeStatement

    def get_balanceSheet(self, i):
        if type(self.balanceSheet) == type(''):
            payload = {'function': 'BALANCE_SHEET',
                       'symbol': self.symbol,
                       'apikey': self.apikey}
            r = requests.get(self.url, headers=headers, params=payload)
            page_html = r.content
            r.close()

            balancesht_soup = BeautifulSoup(page_html, "html.parser")
            balancesht_dict = eval(str(balancesht_soup))                        #The retrived soup can be implemented as a dictionary

            #Getting the values into a DataFrame I can easily work with
            if balancesht_dict:
                latestBalanceSheet_dict = balancesht_dict['annualReports'][0]
                latestBalanceSheet = pd.DataFrame(latestBalanceSheet_dict, index=[i,])
                self.balanceSheet = latestBalanceSheet

                time.sleep(12)
                return latestBalanceSheet
            else:
                return pd.DataFrame()

        else:
            return self.balanceSheet


#The Graham Number is an indicator for what is an acceptable price for the given stock
def graham_number(stockOverview):
    if not stockOverview.empty:
        eps = stockOverview['EPS'].iloc[0]
        eps = float(eps)
        bookV = stockOverview['BookValue'].iloc[0]
        bookV = float(bookV)
        grahamsquare = 22.5 * eps * bookV
        graham = np.sqrt(grahamsquare)
        return graham


def overviewboard(stocks):
    overview = None
    incomeStatement = None
    balanceSheet = None

    #Creating tables out of the given information about the given stocks
    #Separate tables are needed, because the filtering is different in the 3 segments
    for i, stock in enumerate(stocks):
        #The first stock has to be initial for the DataFrames, and the rest is just appended to them
        if i == 0:
            overview = stock.get_overview(i)
            overview['Graham Number'] = graham_number(overview)

            incomeStatement = stock.get_incomeStatement(i)

            balanceSheet = stock.get_balanceSheet(i)
        else:
            overview1 = stock.get_overview(i)
            overview1['Graham Number'] = graham_number(overview1)    #The Graham number is a useful indicating measurement of a company's performance
            overview = overview.append(overview1)

            incomeStatement1 = stock.get_incomeStatement(i)
            incomeStatement = incomeStatement.append(incomeStatement1)

            balanceSheet1 = stock.get_balanceSheet(i)
            balanceSheet = balanceSheet.append(balanceSheet1)

    #These tries are only necessary in case of an invalid API request, or if something with the colums lists is messed
    try:
        overview = overview.loc[:, overview_columns]
        #print("overview success")
    except Exception as e:
        print(e)
        print("Failed to sort out Overview")
    try:
        incomeStatement = incomeStatement.loc[:, income_columns]
        #print("incomestatement success")
    except Exception as e:
        print(e)
        print("Failed to sort out IncomeStatement")
    try:
        balanceSheet = balanceSheet.loc[:, balance_columns]
        #print("balancesheet success")
    except Exception as e:
        print(e)
        print("Failed to sort out BalanceSheet")

    overviewb = pd.concat([overview, incomeStatement, balanceSheet], axis=1)
    return overviewb


#Just for testing purposes
if __name__ == '__main__':
    apikey = input("Enter your API key: ")
    symbols = []
    print('You can enter the symbols of the stocks you want to get informed about \n'
          'one by one, or enter 000 if you finished with them.')
    while True:
        symbol = input('Enter a symbol of a stock: ')
        if symbol != '000':
            symbols.append(symbol)
        else:
            break

    stocks = []
    for s in symbols:
        stock = Stock(s, apikey)
        stocks.append(stock)

    print(overviewboard(stocks))

