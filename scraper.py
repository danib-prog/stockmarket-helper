import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import numpy as np

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'}
aspects = ('AssetType', 'Description', 'Exchange', 'Country',
           'Sector', 'Industry', 'Address', 'FullTimeEmployees',
           'FiscalYearEnd', 'PEGRatio', 'OperatingMarginTTM',
           'ReturnOnEquityTTM', 'DilutedEPSTTM', 'AnalystTargetPrice',
           'ForwardPE', 'PriceToSalesRatioTTM', 'EVToEBITDA',
           'Beta', '50DayMovingAverage', '200DayMovingAverage',
           'SharesFloat', 'SharesShort', 'SharesShortPriorMonth',
           'ShortRatio', 'ShortPercentOutstanding', 'ShortPercentFloat',
           'ForwardAnnualDividendRate', 'ForwardAnnualDividendYield',
           'DividendDate', 'ExDividendDate', 'LastSplitFactor',
           'LastSplitDate')


class Stock():
    url = 'https://www.alphavantage.co/query'

    def __init__(self, symbol):
        self.symbol = symbol

        self.overview = 0
        self.incomeStatement = 0
        self.balanceSheet = 0

    def get_overview(self, i):
        if self.overview == 0:
            payload = {'function': 'OVERVIEW',
                       'symbol': self.symbol,
                       'apikey': apikey}
            r = requests.get(self.url, headers=headers, params=payload)
            page_html = r.content
            r.close()

            overview_soup = BeautifulSoup(page_html, "html.parser")
            overview_dict = eval(str(overview_soup))

            overview = pd.DataFrame(overview_dict, index=[i,])
            self.overview = overview
            time.sleep(12)
            return overview
        else:
            return self.overview

    def get_incomeStatement(self, i):
        if self.incomeStatement == 0:
            payload = {'function': 'INCOME_STATEMENT',
                       'symbol': self.symbol,
                       'apikey': apikey}
            r = requests.get(self.url, headers=headers, params=payload)
            page_html = r.content
            r.close()

            incomest_soup = BeautifulSoup(page_html, "html.parser")
            incomest_dict = eval(str(incomest_soup))

            latestIncomeStatement_dict = incomest_dict['annualReports'][0]
            latestIncomeStatement = pd.DataFrame(latestIncomeStatement_dict, index=[i,])
            self.incomeStatement = latestIncomeStatement

            time.sleep(12)
            return latestIncomeStatement
        else:
            return self.incomeStatement

    def get_balanceSheet(self, i):
        if self.balanceSheet == 0:
            payload = {'function': 'BALANCE_SHEET',
                       'symbol': self.symbol,
                       'apikey': apikey}
            r = requests.get(self.url, headers=headers, params=payload)
            page_html = r.content
            r.close()

            balancesht_soup = BeautifulSoup(page_html, "html.parser")
            balancesht_dict = eval(str(balancesht_soup))

            latestBalanceSheet_dict = balancesht_dict['annualReports'][0]
            latestBalanceSheet = pd.DataFrame(latestBalanceSheet_dict, index=[i,])
            self.balanceSheet = latestBalanceSheet

            time.sleep(12)
            return latestBalanceSheet
        else:
            return self.balanceSheet

def graham_number(stockOverview):
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

    #These are the columns that we don't need from overview
    bullshit = ['AssetType', 'Description', 'Exchange', 'Country',
                'Sector', 'Industry', 'Address', 'FullTimeEmployees',
                'FiscalYearEnd', 'PEGRatio', 'OperatingMarginTTM',
                'ReturnOnEquityTTM', 'DilutedEPSTTM', 'AnalystTargetPrice',
                'ForwardPE', 'PriceToSalesRatioTTM', 'EVToEBITDA',
                'Beta', '50DayMovingAverage', '200DayMovingAverage',
                'SharesFloat', 'SharesShort', 'SharesShortPriorMonth',
                'ShortRatio', 'ShortPercentOutstanding', 'ShortPercentFloat',
                'ForwardAnnualDividendRate', 'ForwardAnnualDividendYield',
                'DividendDate', 'ExDividendDate', 'LastSplitFactor',
                'LastSplitDate']
    #These are only the columns of incomeStatement that we are interested about
    income_columns = ['extraordinaryItems', 'capitalExpenditures',
                      'totalOperatingExpense', 'interestExpense',
                      'incomeTaxExpense', 'totalOtherIncomeExpense']
    #These are only the columns of balanceSheet that we are interested about
    balance_columns = ['totalAssets', 'totalLiabilities', 'shortTermDebt',
                       'longTermDebt', 'cash', 'cashAndShortTermInvestments',
                       'totalShareholderEquity', 'totalPermanentEquity',
                       'commonStockTotalEquity', 'preferredStockTotalEquity']

    #These tries are only necessary in case of an invalid API request, so thus the absence of raiseErrors
    try:
        overview.drop(labels=bullshit, axis=1, inplace=True)
    except:
        pass
    try:
        incomeStatement = incomeStatement.loc[income_columns]
    except:
        pass
    try:
        balanceSheet = balanceSheet.loc[balance_columns]
    except:
        pass

    overviewb = pd.concat([overview, incomeStatement, balanceSheet], axis=1)
    return overviewb


#Just for testing purposes
if __name__ == '__main__':
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
        stock = Stock(s)
        stocks.append(stock)

    print(overviewboard(stocks))

