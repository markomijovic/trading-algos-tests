import sys
import numpy as np
import pandas as pd
import requests
import xlsxwriter
import math
COLUMNS = ['Ticker', 'Price', 'Market Cap', 'Shares to Buy']


def main():
    companies = get_companies()
    # list of lists each containing 100 tickers
    ticker_chunks = list(chunks(companies['Symbol'], 100))
    # prepare the pandas dataframe
    df = make_pandas()
    api_key = get_api_key()
    df = api_call(api_key, comma_separate(ticker_chunks), df)


def get_companies():
    return pd.read_csv(r'data\constituents_csv.csv')


def get_api_key():
    from data.secrets import IEX_CLOUD_API_TOKEN
    return IEX_CLOUD_API_TOKEN


def api_call(api_key, tics, df):
    for tic in tics:
        batch_api_call_url = f'https://sandbox.iexapis.com/stable/stock/market/batch/?types=quote&symbols=' \
                             f'{tic}&token={api_key}'
        data = requests.get(batch_api_call_url)
        if (data.status_code != 200):
            sys.exit("Api call failed.")
        data = data.json()
        # write to .xlx row by row
        for t in tic.split(','):
            df = df.append(
                pd.Series([t,
                           data[t]['quote']['latestPrice'],
                           data[t]['quote']['marketCap'],
                           'N/A'],
                          index=COLUMNS),
                ignore_index=True)
    return buy_shares(df)


def buy_shares(df):
    size = input("Capital = ")
    try:
        val = float(size)
    except:
        print("That's not a number! \n Try again:")
        size = input("Enter the value of your portfolio:")
    size = float(size) / len(df.index)
    for i in range(0, len(df['Ticker'])):
        df.loc[i, 'Shares to Buy'] = math.floor(size / df['Price'][i])
    return df


def make_pandas():
    df = pd.DataFrame(columns=COLUMNS)
    return df


# helper function that chunks the provided list into
# into n-sized chunks from that list
def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def comma_separate(lst):
    tic = []
    for i in range(0, len(lst)):
        tic.append(','.join(lst[i]))
    return tic


if __name__ == "__main__":
    main()
