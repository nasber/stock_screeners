from urllib.request import urlopen, Request
from bs4 import BeautifulSoup as soup
from yahoo_fin import stock_info as si
import pandas as pd
import pandas_datareader.data as web
import datetime as dt
import time
import concurrent.futures
import statistics as stats
import requests


def getStockData(ticker):
    
    try:
        s = float(si.get_stats(ticker).Value[15].replace('%',''))
        new_row =  {'Stock': ticker, 'Short Percentage': s}
    
        
        if (s > 30):
            return new_row
        else:
            return False
    except:
        return False
if __name__ == "__main__":
    THREAD_NO=100
    tickers = si.tickers_sp500()
    tickers.extend(si.tickers_nasdaq())
    tickers = list(dict.fromkeys(tickers))
    
    dfShorts = pd.DataFrame(columns=['Stock', "Short Percentage"])
    threads_start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_NO) as executor:
        results = executor.map(getStockData, tickers) 
        for result in results:
            if result !=False:
                dfShorts = dfShorts.append(result, ignore_index=True)
                

print(dfShorts)
    

