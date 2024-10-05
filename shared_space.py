import json
import requests
import telegrapher

bursa_query_url = "https://www.bursamarketplace.com/index.php"

bursa_query_headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0'
}

bursa_query_params = {
    'tpl':'stock_ajax',
    'type':'gettixdetail'
}

def getinfo_by_bursa_stockcode(stockcode="MBBM"):
    
    query_url       = bursa_query_url
    query_headers   = bursa_query_headers
    query_params    = bursa_query_params
    
    bursa_query_params['code'] = stockcode
    
    r = requests.get(query_url, params=query_params, headers=query_headers)
    
    return r


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


def check_discount_threshold(stock_info_json, t=0.5, return_desired_only=True):
    # This function checks if a stock's current price is lower than the desired threshold.
    
    # The value of the threshold is found using the follwing formula
    # threshold = yrhigh - [(yrhigh - yrlow) * t]

    # Higher value of t, lower the threshold
    # I think of it as a discount - t=0.8 means the stock is desirable at 80% off discount from peak price

    diff = float(stock_info_json['yrhigh']) - float(stock_info_json['yrlow'])
    diff_t = diff * t
    threshold = float(stock_info_json['yrhigh']) - diff_t
    
    threshold = round(threshold, 3)

    print(f"Desired Threshold for {stock_info_json['alias']}: {str(threshold)}")
    
    # If the current price of a stock is lower than the desired threshold,
    # Send an alert
    if float(stock_info_json['last']) <= threshold or return_desired_only == False:
        str_alert = "Name: " + stock_info_json['alias'] + "\n"
        str_alert += "Current Price: " + stock_info_json['last'] + "\n"
        str_alert += "Lot Size: " + stock_info_json['lotsize'] + "\n"
        str_alert += "Dividend: " + stock_info_json['dividend'] + " (" + stock_info_json['yield'] + ")\n\n"
        str_alert += "Desired Threshold: " + str(threshold) + "\n"
        str_alert += "YrHigh/YrLow: " + stock_info_json['yrhigh'] + "/" + stock_info_json['yrlow'] + "\n"
        str_alert += "Ask: " + stock_info_json['ask'] + " (Size: " + stock_info_json['asksize'] + ")\n"
        str_alert += "Bid: " + stock_info_json['bid'] + " (Size: " + stock_info_json['bidsize'] + ")"
        telegrapher.sendMessage(str_alert)