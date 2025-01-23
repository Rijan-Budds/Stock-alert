import requests
from bs4 import BeautifulSoup

def get_stock_details(ticker):
    try:
        url = f"https://finance.yahoo.com/quote/{ticker}"
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        price = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'}).text
        change = soup.find('fin-streamer', {'data-field': 'regularMarketChangePercent'}).text
        
        return {
            "ticker": ticker,
            "price": price,
            "change": change
        }
    except Exception as e:
        return {"error": str(e)}

def send_to_slack(stock_details, webhook_url):
    if "error" in stock_details:
        message = f"Error fetching stock details: {stock_details['error']}"
    else:
        message = (
            f"*Stock:* {stock_details['ticker']}\n"
            f"*Price:* {stock_details['price']}\n"
            f"*Change:* {stock_details['change']}"
        )
    
    payload = {"text": message}
    
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print("Message sent to Slack!")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send message to Slack: {e}")

def main():
    webhook_url = "https://hooks.slack.com/services/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"
    
    ticker = "AAPL"
    
    stock_details = get_stock_details(ticker)
    
    send_to_slack(stock_details, webhook_url)

if __name__ == "__main__":
    main()



https://hooks.slack.com/services/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