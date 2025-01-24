from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json
import time
import threading
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)

def get_stock_price(symbol):
    url = f"https://merolagani.com/CompanyDetail.aspx?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    price = soup.find("span", id="ctl00_ContentPlaceHolder1_CompanyDetail1_lblMarketPrice").text.strip()
    return float(price.replace(",", ""))

def send_to_slack_via_response_url(response_url, message):
    payload = {
        "response_type": "in_channel",  
        "text": message
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(response_url, data=json.dumps(payload), headers=headers)
    return response.status_code

def monitor_stock(symbol, target_price, response_url):
    logging.info(f"Monitoring {symbol} for target price Rs {target_price}...")
    
    while True:
        try:
            current_price = get_stock_price(symbol)
            logging.info(f"Current price of {symbol}: Rs {current_price}")

            if current_price >= target_price:
                message = f":bell: *Alert!* {symbol} has reached your target price of Rs {target_price}. Current price: Rs {current_price}"
                send_to_slack_via_response_url(response_url, message)
                logging.info("Notification sent to Slack!")
                break

            time.sleep(60) 

        except Exception as e:
            logging.error(f"Error: {e}")
            break

@app.route('/')
def home():
    return "Hello, Flask Server is Running!"

@app.route('/stock', methods=['POST'])
def stock_command():
    data = request.form
    text = data.get('text', '').strip().split()
    
    if len(text) != 2:
        return jsonify({
            "response_type": "ephemeral",  
            "text": "Usage: /stock <SYMBOL> <TARGET_PRICE> (e.g., /stock NABIL 1500)"
        })
    
    symbol = text[0].upper()
    try:
        target_price = float(text[1])
    except ValueError:
        return jsonify({
            "response_type": "ephemeral",  
            "text": "Invalid target price. Please enter a valid number."
        })
    
    response_url = data.get('response_url')  
    threading.Thread(target=monitor_stock, args=(symbol, target_price, response_url)).start()
    
    return jsonify({
        "response_type": "in_channel", 
        "text": f"Started monitoring {symbol} for target price Rs {target_price}. You will be notified when the target is reached."
    })

if __name__ == '__main__':
    app.run(port=3000)
