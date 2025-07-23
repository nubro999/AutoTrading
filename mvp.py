import os
from dotenv import load_dotenv
load_dotenv()


def auto_trade():
    import pyupbit
    '''import pandas as pd

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)'''

    df = pyupbit.get_ohlcv("KRW-BTC", count=30, interval='day')

    from openai import OpenAI
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {
                "role": "system",
                "content": '''Analyze the provided Bitcoin chart data (OHLCV). Your task is to perform technical analysis and decide whether to buy, sell, or hold.

                Your analysis should consider:
                - Price trends
                - Moving averages
                - RSI and MACD (if data is available)
                - Support and resistance levels
                - Trading volume

                Your final output must be a single JSON object with two keys:
                1. `recommendation`: A string, one of "buy", "sell", or "hold".
                2. `justification`: A concise (1-2 sentences) explanation for your recommendation.

                Do not include your reasoning steps in the output. If the data is insufficient, state it in the justification.'''
            },
            {
                "role": "user",
                "content": df.to_json()
            }
        ],
        response_format={ "type": "json_object" },
        temperature=1,
        max_tokens=2048,
        top_p=1,
    )

    import json
    result = json.loads(response.choices[0].message.content)


    import pyupbit
    access_key = os.getenv("UPBIT_ACCESS_KEY")
    secret_key = os.getenv("UPBIT_SECRET_KEY")
    upbit = pyupbit.Upbit(access_key, secret_key)
    my_krw = upbit.get_balance("KRW")

    print(access_key)
    print(secret_key)

    print("Current KRW balance:", my_krw)
    print("Current BTC balance:", upbit.get_balance("KRW-BTC"))


    #Buy BTC if recommendation is "buy"
    if result.get("recommendation") == "buy":
        print(upbit.buy_market_order(my_krw*0.2))


    #Sell BTC if recommendation is "sell"
    elif result.get("recommendation") == "sell":
        my_btc = upbit.get_balance("KRW-BTC") or 0
        current_price = pyupbit.get_current_price("KRW-BTC")

        if my_btc*current_price > 5000 :
            print(upbit.sell_market_order("KRW-BTC", upbit.get_balance("KRW-BTC")*0.2)) #error
        else:
            print("Insufficient BTC balance to sell, or BTC value is below 5000 KRW.")

    #Hold BTC if recommendation is "hold"
    elif result.get("recommendation") == "hold":
        print("Recommendation: Hold")   

    else :
        print("Error: No valid recommendation found.")

    print("Justification:", result.get("justification"))


while True:
    import time
    auto_trade()
    time.sleep(30)
    