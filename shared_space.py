import requests


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