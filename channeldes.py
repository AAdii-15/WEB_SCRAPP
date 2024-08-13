import requests
from bs4 import BeautifulSoup
import json

def extract_channel_desc(soup):
    data = {}
    
    # Find all the divs that contain the information
    elements = soup.find_all("div", {'class': 'flex items-center justify-between gap-4 text-sm font-medium'})
    
    # Iterate through each element and extract the key-value pairs
    for element in elements:
        key = element.find('div', {'class': 'text-vidiq-body-gray inline-flex items-center gap-[6px]'}).text.strip()
        value = element.find('p', {'class': 'mb-0 text-right text-white'}).text.strip()
        data[key] = value
    
    return data

def main():
    # Get the webpage content
    web = requests.get("https://vidiq.com/youtube-stats/channel/UCeVMnSShP_Iviwkknt83cww/")
    soup = BeautifulSoup(web.content, "html.parser")

    # Extract data using the function
    channel_desc = extract_channel_desc(soup)

    # Convert to JSON and print
    json_data = json.dumps(channel_desc, indent=4)
    print(json_data)

if __name__ == "__main__":
    main()
