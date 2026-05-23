import requests
from langchain.tools import tool
import yfinance as yf
from datetime import datetime



@tool
def get_price(symbol : str) -> float:
    """Get the live price of a stock from NSE using yfinance.
    Args:
        symbol (str): The stock symbol to get the price for.
    Returns:
        float: The live price of the stock.
    """
    stock = yf.Ticker(symbol)
    return f"The latest price of the {symbol} is {stock.fast_info["last_price"]}"

if __name__ == "__main__":
    # Example usage
    symbol = "TCS.NS"
    price_data = get_price.invoke({"symbol": symbol})
    print(f"Price of {symbol}: {price_data} at {datetime.now()}")