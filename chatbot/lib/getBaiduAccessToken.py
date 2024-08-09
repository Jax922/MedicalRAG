
import requests
import json

# APIKEY：
# HI9V7RVRZDPnVq2kkkQFnpTq
# Secret Key：
# B2Z0qhoMCcSPd8Y59f2JV79JGfFVdWxN

def main():
        
    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=HI9V7RVRZDPnVq2kkkQFnpTq&client_secret=B2Z0qhoMCcSPd8Y59f2JV79JGfFVdWxN"
    
    payload = ""
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    print(response.text)
    

if __name__ == '__main__':
    main()
