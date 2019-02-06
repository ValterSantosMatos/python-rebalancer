import time

import pandas as pd
import requests

import keys


def getPrices(symbol):
    print("getting price for " + symbol)
    url = "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=" + \
          symbol + "&apikey=" + keys.ALPHA_VANTAGE_KEY

    while True:
        resp = requests.get(url=url)
        data = resp.json()

        if 'Note' in data:
            print('Maximum number of calls reached waiting 1 min...')
            time.sleep(60)
        else:
            print("received price for " + symbol + ": " +
                  data['Global Quote']['05. price'])
            return float(data['Global Quote']['05. price'])


# Generates the pandas data frame
d = {'symbols': keys.symbols,
     'model_allocation': keys.model_allocation,
     'qtt': keys.qtt}
df = pd.DataFrame(data=d)

# Get the prices from alphavantage
df['prices'] = df.symbols.apply(
    lambda x: keys.cash_price if x == keys.cash_symbol[0] else getPrices(x))

# Gets the current mv and allocations
df['market_value'] = df.prices * df.qtt
total_market_value = df.market_value.sum()
df['current_allocation'] = df.prices * df.qtt * 100 / total_market_value

# Gets the difference
df['diff_allocation'] = df.current_allocation - \
    df.model_allocation
df['diff_amount'] = df.diff_allocation * total_market_value / 100
df['diff_shares'] = (df.diff_amount / df.prices).round()
df['diff'] = df.diff_shares.apply(
    lambda x: ('Buy ' + str(x * -1).strip(".0") if x < 0 else 'Sell ' + str(x).strip(".0")))

print(df)
