from yahoo_fin import stock_info as si
import pandas as pd
import numpy
import datetime
import requests
import time
import concurrent.futures
def getStockData(stock_ticker):
    start_date = datetime.datetime.now() - datetime.timedelta(days=365)
    end_date = datetime.date.today()
    try:
        df = si.get_data(stock_ticker, start_date=start_date, end_date=end_date)
        current,ma50,ma150,ma200,ma200_30,high52wk,low52wk = df['adjclose'][-1],df['adjclose'][-50:].mean(),df['adjclose'][-150:].mean(),df['adjclose'][-200:].mean(),df['adjclose'][-230:-30].mean(),df['high'].max(),df['low'].min()
        avgVolume21days = df['volume'][-21:].mean()
        avgVolume100days = df['volume'][-150:].mean()
        low21day = df['adjclose'][-21:].min()
        high21day = df['adjclose'][-21:].max()
        delta = high21day - low21day
        
        

        if (ma50 > ma150 > ma200 > ma200_30):
            if (avgVolume100days > 1000000):
                if (current > ma50):
                    if (current > (low52wk * 1.3)):
                        if (current > (high52wk * .6)):
                            if ((avgVolume100days * .6) > (avgVolume21days)):
                                    if (delta < (current * .08)):
                                        return stock_ticker
                                    else:
                                        return False
                            else:
                                    return False
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
    except:
        return False
if __name__ == "__main__":
    THREAD_NO=200
    tickers = si.tickers_sp500()
    tickers.extend(si.tickers_nasdaq())
    tickers = list(dict.fromkeys(tickers))
    # print(stock_list)
    # stock_list = si.tickers_others()
    
    mmlist = []
    threads_start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_NO) as executor:
        results = executor.map(getStockData, tickers) 
        for result in results:
            if result !=False:
                mmlist.append(result)

print(mmlist)