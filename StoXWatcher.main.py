#!/usr/bin/python3

import json
import requests
import telg_bot

# TODO
# X. Implement a list to read from and iterate through all items in the list
# X. Create and integrate Telegram Bot for sending alerts
# X. Implement threshold based notifications
# 4. Ideas for interactive components for the Telegram Bot
#   4a. Do an ad-hoc check on followed companies
#   4b. Pull data for specific company
#   4c. Add company cashtag to followed companies
# 5. Logging

# Note:
# 1. Stockcodes(Cashtags) can be searched at https://www.bursamarketplace.com/mkt/themarket/stock

def save_raw_json(json_response):
    print("\nSaving contents of response to raw_json_response.txt")
    parsed_json = json.loads(json_response.text) 
    
    with open('raw_json_response.txt', 'w') as raw_file:
        json.dump(parsed_json, raw_file, indent=4)

def update_json_data(json_response):
    parsed_json = json.loads(json_response.text)
    print('\n---Saving data for stockcode ' + parsed_json['stockcode'] + '---\n')

    # get the filepath for the data to be saved to
    # by default it will be data/STOCKCODE.json
    save_filepath = 'data/' + parsed_json['stockcode'][1:] + '.json'
    
    with open(save_filepath, 'w') as save_file:
        json.dump(parsed_json, save_file, indent=4)

def check_threshold(stock_info_json, t=0.5):
    # This function checks if a stock's current price is lower than the desired threshold.
    
    # The value of the threshold is found using the follwing formula
    # threshold = yrhigh - [(yrhigh - yrlow) * t]

    # Higher value of t, lower the threshold
    # I think of it as a discount - t=0.8 means the stock is desirable at 80% off discount from peak price

    diff = float(stock_info_json['yrhigh']) - float(stock_info_json['yrlow'])
    diff_t = diff * t
    threshold = float(stock_info_json['yrhigh']) - diff_t

    print("Desired Threshold: " + str(threshold))
    
    # If the current price of a stock is lower than the desired threshold,
    # Send an alert
    if float(stock_info_json['last']) <= threshold:
        str_alert = "Buy Alert: " + stock_info_json['alias'] + "\n"
        str_alert += "Current Price: " + stock_info_json['last'] + "\n"
        str_alert += "Lot Size: " + stock_info_json['lotsize'] + "\n"
        str_alert += "Dividend: " + stock_info_json['dividend'] + " (" + stock_info_json['yield'] + ")\n\n"
        str_alert += "Desired Threshold: " + str(threshold) + "\n"
        str_alert += "YrHigh/YrLow: " + stock_info_json['yrhigh'] + "/" + stock_info_json['yrlow'] + "\n"
        str_alert += "Ask: " + stock_info_json['ask'] + " (Size: " + stock_info_json['asksize'] + ")\n"
        str_alert += "Bid: " + stock_info_json['bid'] + " (Size: " + stock_info_json['bidsize'] + ")"
        telg_bot.sendMessage(str_alert)


telg_bot.sendMessage("Helloworld")

# Start a session and initialize constant variables
session = requests.Session()
    
query_url = "https://www.bursamarketplace.com/index.php"

query_headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
}

# Read list of stock codes to iterate through from stockcodes.txt
with open('stockcodes.txt', 'r') as sc_file:
    stockcodes = sc_file.readlines()

for stockcode in stockcodes:
    stockcode = stockcode.strip()

    query_params = {
        'tpl':'stock_ajax',
        'type':'gettixdetail',
        'code':stockcode
    }

    # Make the actual query
    r1 = session.get(query_url, params=query_params, headers=query_headers)

    if r1.status_code == 200:
        # Parse JSON response data
        r1_data = r1.json()

        print("Company     : " + r1_data['alias'])
        print("Stock Price : " + r1_data['last'] + " (lot size: " + r1_data['lotsize'] + ")")
        print("Dividend    : " + r1_data['dividend'] + " (yield: " + r1_data['yield'] + ")\n")
        print("Most Recent Dividend and Date:")
        print("Dividend    : " + r1_data['findividend']['dividendmostrecent'])
        print("Date        : " + r1_data['findividend']['dividendpaydate'])    
        
        # Check threshold and send notification if stock price is below desired threshold
        check_threshold(r1.json(), t=0.7)

        # Save the JSON data
        update_json_data(r1)
        
    else:
        print("WARNING: Did not get response code 200")
        update_json_data(r1)

