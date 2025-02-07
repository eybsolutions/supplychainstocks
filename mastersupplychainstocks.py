import yfinance as yf
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta

# Define stocks categorized by industries with names
stock_categories = {
    "Logistics and Transport": {
        "FedEx (FDX)": "FDX",
        "UPS (UPS)": "UPS",
        "XPO Logistics (XPO)": "XPO",
        "C.H. Robinson (CHRW)": "CHRW",
        "Expeditors International (EXPD)": "EXPD"
    },
    "Warehouse Management and 3PLs": {
        "Prologis (PLD)": "PLD",
        "Ryder (R)": "R", 
        "Lineage (LINE)": "LINE"
    },
    "Manufacturing": {
        "Caterpillar (CAT)": "CAT",
        "Deere & Co. (DE)": "DE",
        "General Motors (GM)": "GM"
    },
    "E-commerce and Retail": {
        "Amazon (AMZN)": "AMZN",
        "Walmart (WMT)": "WMT",
        "Target (TGT)": "TGT",
        "Home Depot (HD)": "HD"
    },
    "Technology and Supply Chain Solutions": {
        "Oracle (ORCL)": "ORCL",
        "SAP (SAP)": "SAP",
        "Manhattan Associates (MANH)": "MANH"
    },
    "Shipping and Freight": {
        "Union Pacific (UNP)": "UNP"
    }
}

# Fetch stock data for the past 5 years
def get_stock_data(stock):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=5 * 365)  # 5-year data
    data = yf.download(stock, start=start_date, end=end_date)
    data.reset_index(inplace=True)
    return data

# Identify significant price changes
def add_indicators(data):
    data['Percent Change'] = data['Close'].pct_change() * 100
    data['Indicator'] = data['Percent Change'].apply(lambda x: 'Large Increase' if x > 5 else ('Large Decrease' if x < -5 else 'Normal'))
    data['Month/Year'] = data['Date'].dt.strftime('%b %Y')
    return data

# Streamlit UI setup
st.set_page_config(layout="wide")
st.title("Supply Chain Stock Tracker")
st.write("View the past 5-year stock performance across various industries with indicators for significant price changes.")

# Create tabs for each industry
tabs = st.tabs(list(stock_categories.keys()))
for tab, (category, stocks) in zip(tabs, stock_categories.items()):
    with tab:
        st.header(f"{category} Stocks")
        for company, stock in stocks.items():
            st.subheader(company)
            data = get_stock_data(stock)
            if not data.empty:
                data = add_indicators(data)
                # Display the stock chart with indicators
                chart = alt.Chart(data).mark_line(point=True).encode(
                    x=alt.X('Date:T', title='Date'),
                    y=alt.Y('Close:Q', title='Closing Price', scale=alt.Scale(zero=False)),
                    color=alt.condition(
                        alt.FieldOneOfPredicate('Indicator', ['Large Increase', 'Large Decrease']),
                        alt.value('red'),  # Highlight large changes in red
                        alt.value('steelblue')
                    ),
                    tooltip=['Date:T', 'Close:Q', 'Percent Change:Q', 'Indicator:N']
                ).properties(
                    title=f"{company} - Last 5 Years Performance",
                    width='container',
                    height=400
                ).interactive()

                st.altair_chart(chart, use_container_width=True)

                # Display only records with large changes
                large_changes = data[data['Indicator'].isin(['Large Increase', 'Large Decrease'])]
                st.write(
                    large_changes[['Month/Year', 'Close', 'Percent Change', 'Indicator']].tail(10).rename(
                        columns={
                            'Month/Year': 'Month/Year',
                            'Close': 'Closing Price',
                            'Percent Change': 'Percent Change (%)',
                            'Indicator': 'Change Indicator'
                        }
                    ).style.set_properties(**{'text-align': 'center'})
                )
            else:
                st.write(f"No data available for {stock}.")
