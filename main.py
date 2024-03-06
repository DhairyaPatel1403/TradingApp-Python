import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
import mplfinance as mpf  
from dotenv import load_dotenv
import os


connection_string = "postgresql://DhairyaPatel1403:BY3CpiV1dUgD@ep-blue-pine-a4nxdtlt.us-east-1.aws.neon.tech/tradedata?sslmode=require"


def generate_signals(df):
    # Doing SMA
    df['SMA_5'] = df['Adj Close'].rolling(window=5).mean()
    df['SMA_10'] = df['Adj Close'].rolling(window=10).mean()
    df['SMA_20'] = df['Adj Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Adj Close'].rolling(window=50).mean()
    df['SMA_200'] = df['Adj Close'].rolling(window=200).mean()

    df['Signal'] = ''


    df.loc[(df['SMA_50'] > df['SMA_200']) & (df['SMA_50'].shift(1) <= df['SMA_200'].shift(1)), 'Signal'] = 'Buy'


    df.loc[(df['SMA_20'] < df['SMA_200']) & (df['SMA_20'].shift(1) >= df['SMA_200'].shift(1)), 'Signal'] = 'Sell'

   
    df.loc[(df['SMA_10'] < df['SMA_20']) & (df['SMA_10'].shift(1) >= df['SMA_20'].shift(1)), 'Signal'] = 'Close Buy'


    df.loc[(df['SMA_5'] > df['SMA_10']) & (df['SMA_5'].shift(1) <= df['SMA_10'].shift(1)), 'Signal'] = 'Close Sell'

    return df

def fetch_stock_details(connection_string, selected_stock):

    conn = psycopg2.connect(connection_string)

    cursor = conn.cursor()

    # Updated - only fetch given named stock's data
    cursor.execute(f'SELECT "Date", "Name", "Adj Close", "Open", "Close", "High", "Low", "Volume" FROM stocks WHERE "Name" = %s;', (selected_stock,))


    rows = cursor.fetchall()


    cursor.close()
    conn.close()

    df = pd.DataFrame(rows, columns=["Date", "Name", "Adj Close", "Open", "Close", "High", "Low", "Volume"])
    return df



st.title("Stock Closing Prices")


stock_names = ["AAPL", "HDB", "INR=X", "JIOFIN.NS", "MARA", "TATAMOTORS.NS", "TSLA"]


selected_stock = st.selectbox("Select a stock:", stock_names)



show_candlestick = st.checkbox("Show Candlestick Chart")


data = fetch_stock_details(connection_string, selected_stock)


df = generate_signals(data)


if show_candlestick:
    st.subheader("Candlestick Chart")
    fig, ax = plt.subplots(figsize=(10, 6))
    df['Date'] = pd.to_datetime(df['Date'])
    mpf.plot(df.set_index('Date'), type='candle', ax=ax, volume=ax, style='charles') 
    st.pyplot(fig)
else:
    st.subheader("Regular Chart with Signals")
    fig, ax = plt.subplots(figsize=(10, 6))


    signal_colors = {'Buy': 'green', 'Sell': 'red', 'Close Buy': 'orange', 'Close Sell': 'blue', '': 'black'}


    start_idx = 0
    current_color = ''


    encountered_signals = set()

    # Color chaning instead of labeling
    for i, (date, signal) in enumerate(zip(df.index, df['Signal'])):
        if signal != '' and signal not in encountered_signals:
 
            ax.plot(df.index[start_idx:i], df['Adj Close'][start_idx:i], color=signal_colors[signal], label=f'{signal} Signal')

            encountered_signals.add(signal)

            start_idx = i

    ax.plot(df.index[start_idx:], df['Adj Close'][start_idx:], color=signal_colors[df['Signal'].iloc[-1]], label=f'{df["Signal"].iloc[-1]} Signal')


    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.set_title(f"{selected_stock} Prices with Signals")

    plt.setp(ax.get_xticklabels(), rotation=45)


    ax.legend()


    st.pyplot(fig)



def calculate_profit(df, investment_date):
    try:
        investment_date = pd.to_datetime(investment_date)
        investment_row = df[df['Date'] == investment_date]
        if not investment_row.empty:
            invested_price = investment_row.iloc[0]['Adj Close']
            current_price = df.iloc[-1]['Adj Close']
            shares_bought = 1  # Assuming buying 1 share
            profit = (current_price - invested_price) * shares_bought
            return profit
        else:
            return "Investment date not found in data."
    except Exception as e:
        return str(e)

highest_price = df['Adj Close'].max()
lowest_price = df['Adj Close'].min()

# Calculate overall profit or loss
profit_loss = df['Adj Close'].iloc[-1] - df['Adj Close'].iloc[0]

# Display highest and lowest prices along with profit or loss
st.write(f"Highest Price: {highest_price}")
st.write(f"Lowest Price: {lowest_price}")
st.write(f"Overall Profit/Loss: {profit_loss}")



# Create a container for investment date input
st.subheader("Check Profit on Investment Date")
investment_date = st.date_input("Enter the investment date:")

# Create a button to trigger profit calculation
if st.button("Calculate Profit"):
    if investment_date:
        profit = calculate_profit(data, investment_date)
        st.write(f"Profit Loss from your date : {profit}")