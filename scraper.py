import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'}
apikey = input("What's your Alpha Vantage API key? ")


class Stock():
    url = 'https://www.alphavantage.co/query'

    def __init__(self, symbol):
        self.symbol = symbol

    def get_overview(self, i):
        payload = {'function': 'OVERVIEW',
                   'symbol': self.symbol,
                   'apikey': apikey}
        r = requests.get(self.url, headers=headers, params=payload)
        page_html = r.content
        r.close()

        overview_soup = BeautifulSoup(page_html, "html.parser")
        overview_dict = eval(str(overview_soup))
        #cut the shit
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
        for shit in bullshit:
            overview_dict.pop(shit)

        overview = pd.DataFrame(overview_dict, index=[i,])
        return overview


def overviewboard(symbols):
    overview = None
    for i, symbol in enumerate(symbols):
        stock = Stock(symbol)
        if i == 0:
            overview = stock.get_overview(i)
        else:
            overview1 = stock.get_overview(i)
            overview = overview.append(overview1)
        time.sleep(13)
    return overview


#Just for testing purposes
if __name__ == '__main__':
    symbols = ['AAPL', 'MSFT', 'NVDA']
    print(overviewboard(symbols))

