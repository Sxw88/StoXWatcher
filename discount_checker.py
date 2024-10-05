#!/usr/bin/python3

import requests
from shared_space import update_json_data, getinfo_by_bursa_stockcode, check_discount_threshold

# TODO
# X. Implement a list to read from and iterate through all items in the list
# X. Create and integrate Telegram Bot for sending alerts
# X. Implement threshold based notifications


if __name__ == "__main__":

    # Read list of stock codes to iterate through from stockcodes.txt
    with open('conf/stockcodes.txt', 'r') as sc_file:
        stockcodes = sc_file.readlines()

    for stockcode in stockcodes:
        stockcode = stockcode.strip()
        
        r1 = getinfo_by_bursa_stockcode(stockcode)

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
            check_discount_threshold(r1.json(), t=0.7)

            # Save the JSON data
            update_json_data(r1)
            
        else:
            print("WARNING: Did not get response code 200")
            update_json_data(r1)

