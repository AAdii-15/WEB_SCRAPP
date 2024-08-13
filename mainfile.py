import requests
from bs4 import BeautifulSoup
import re
import json

def extract_script_data(soup, index):
    script_tags = soup.find_all('script')
    if len(script_tags) > index:
        script_content = script_tags[index].string
        json_pattern = re.compile(r'\{[^}]+\}')
        json_strings = json_pattern.findall(script_content)
        return [clean_and_parse_json(js) for js in json_strings if clean_and_parse_json(js)]
    return []

def clean_and_parse_json(json_str):
    try:
        cleaned_json_str = json_str.replace('\\"', '"')
        return json.loads(cleaned_json_str)
    except json.JSONDecodeError:
        return None

def extract_channel_description(soup):
    data = {}
    elements = soup.find_all("div", class_='flex items-center justify-between gap-4 text-sm font-medium')
    for element in elements:
        key = element.find('div', class_='text-vidiq-body-gray inline-flex items-center gap-[6px]').text.strip()
        value = element.find('p', class_='mb-0 text-right text-white').text.strip()
        data[key] = value
    return data

def extract_daily_performance(soup):
    data = []
    rows = soup.find_all('tr', class_='hover:bg-vidiq-dark-300 transition duration-150 ease-in-out')
    for row in rows:
        columns = row.find_all('td')
        if len(columns) >= 4:
            date = columns[0].text.strip()
            subscribers = columns[1].text.strip().replace("\u00A0", " ")
            views = columns[2].text.strip().replace("\u00A0", " ")
            earnings = columns[3].text.strip()
            data.append({
                'Date': date,
                'Subscribers': subscribers,
                'Views': views,
                'Estimated Earnings': earnings
            })
    return data

def extract_overall_score(soup):
    score = "Not Available"
    score_div = soup.find('p', class_='mb-8 text-center text-[88px] font-extrabold leading-[68px]')
    if score_div:
        score = score_div.text.strip()
    return score

def extract_additional_metrics(soup):
    metrics = {}
    elements = soup.find_all("p", class_="mb-1 text-xl font-extrabold text-white lg:text-[26px] lg:leading-[30px]")
    if len(elements) >= 6:
        metrics = {
            "Subscribers": elements[0].text.strip(),
            "Video views": elements[1].text.strip(),
            "Monthly Earnings": elements[2].text.strip(),
            "Engagement rate": elements[3].text.strip(),
            "Video Upload Frequency": elements[4].text.strip(),
            "Average Video Length": elements[5].text.strip()
        }
    return metrics

def main():
    url = 'https://vidiq.com/youtube-stats/channel/UCeVMnSShP_Iviwkknt83cww/'
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        description = extract_channel_description(soup)
        daily_performance = extract_daily_performance(soup)
        overall_score = extract_overall_score(soup)
        additional_metrics = extract_additional_metrics(soup)
        
        # Extract JSON data from script tags
        script_data_5 = extract_script_data(soup, -5)
        script_data_4 = extract_script_data(soup, -4)
        script_data_6 = extract_script_data(soup, -6)

        print("GRAPH 1 DATA:")
        print(json.dumps(script_data_5, indent=4))

        print("\nGRAPH 2 DATA:")
        print(json.dumps(script_data_4, indent=4))

        print("\nGRAPH 3 DATA:")
        print(json.dumps(script_data_6, indent=4))

        print("\nOVERALL SCORE:")
        print(overall_score)

        print("\nCHANNEL DESCRIPTION:")
        print(json.dumps(description, indent=4))

        print("\nDAILY PERFORMANCE DATA:")
        print(json.dumps(daily_performance, indent=4))

        print("\nADDITIONAL METRICS:")
        print(json.dumps(additional_metrics, indent=4))

    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

if __name__ == "__main__":
    main()
