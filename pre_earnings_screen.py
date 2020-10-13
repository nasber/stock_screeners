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
def __getHtmlData(url):
  header = {
  "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
  "X-Requested-With": "XMLHttpRequest"
}
  try:
    r = requests.get(url, headers=header)
    if r.status_code==200:
      return r.text
    else:
      return False
  except requests.exceptions.RequestException as e:
    print(e)
    return False
def getStockData(ticker):
  try:
    result=pd.read_html(__getHtmlData('https://www.alphaquery.com/stock/' + ticker + '/earnings-history'))
    AnnouncementDates = result[0].loc[ : , 'Announcement Date' ]
    tot_er_dates = len(AnnouncementDates.values)
    made_cut = False
    df = si.get_data(ticker)
    i = 3  
    prev_pct_pos = 0.0
    while i < 15:
      deltas = []

      pos_count = 0
      neg_count = 0
      for AnncDates in AnnouncementDates.values:
          er_close = df['adjclose'].iloc[df.index.get_loc(AnncDates)-2]
          prev_close = df['adjclose'].iloc[df.index.get_loc(AnncDates)-i]
          
          delta = ((er_close - prev_close)/prev_close) * 100
          deltas.append(delta)
          if delta > (er_close * .02):
            pos_count = pos_count + 1
          elif delta < (er_close * -.02):
            neg_count = neg_count + 1
          else:
            pass
      pct_pos = pos_count/tot_er_dates * 100
      pct_neg = neg_count/tot_er_dates * 100
      if (pct_pos > 80 and tot_er_dates > 7):
        made_cut = True
        if pct_pos > prev_pct_pos:
          avg_delta = stats.mean(deltas)
          max_delta = max(deltas)
          min_delta = min(deltas)
          new_row = {'Stock': ticker,'Earnings Count':tot_er_dates, "Percent Positive": pct_pos,"Percent Negative": pct_neg, "Days Before ER": i, "AVG Delta": avg_delta, "Max Delta": max_delta, "Worst Delta": min_delta}
          prev_pct_pos = pct_pos
          if i < 14:
            i = i + 1
          else:
            return new_row
        else:
          if i < 14:
            i=i+1
          else:
            return new_row
      else:
        if i < 14:
          i=i+1
        else:
          return new_row
    if made_cut == True:
      return new_row
    else:
      return False
  except:
    return False
if __name__ == "__main__":
    THREAD_NO=200
    tickers = si.tickers_sp500()
    # tickers.extend(si.tickers_nasdaq())
    # tickers = list(dict.fromkeys(tickers))
    df_screened = pd.DataFrame(columns=['Stock','Earnings Count', "Percent Positive","Percent Negative", "Days Before ER", "AVG Delta", "Max Delta", "Worst Delta"])
    threads_start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_NO) as executor:
        results = executor.map(getStockData, tickers) 
        for result in results:
            if result !=False:
                df_screened = df_screened.append(result, ignore_index=True)
    print("With threads time:", time.time() - threads_start)
    print(df_screened)
    # df_screened.to_csv(r'14DaysNas_and_SP500_pre_ER.csv')