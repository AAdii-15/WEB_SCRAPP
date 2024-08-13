import requests
from bs4 import BeautifulSoup
import re
import json


url = 'https://vidiq.com/youtube-stats/channel/UCeVMnSShP_Iviwkknt83cww/'


response = requests.get(url)
html_content = response.text


soup = BeautifulSoup(html_content, 'html.parser')


script_tags = soup.find_all('script')


print(f"Number of script tags found: {len(script_tags)}")


script_content = script_tags[-6].string


print("Raw script content:\n", script_content)

#REGEX
json_pattern = re.compile(r'\{[^}]+\}')
json_strings = json_pattern.findall(script_content)

# Print all extracted JSON-like strings for debugging
print("Extracted JSON-like strings:\n", json_strings)

# Function to clean and decode JSON strings
def clean_and_parse_json(json_str):
    try:
        # Fix escaped quotes
        cleaned_json_str = json_str.replace('\\"', '"')
        # Add braces if necessary
        if not cleaned_json_str.startswith('{'):
            cleaned_json_str = '{' + cleaned_json_str + '}'
        if not cleaned_json_str.endswith('}'):
            cleaned_json_str = cleaned_json_str + '}'
        # Convert cleaned JSON string to dictionary
        data = json.loads(cleaned_json_str)
        return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Problematic JSON string: {json_str}")
        return None

# Extract and print key-value pairs from the cleaned JSON strings
for i, json_str in enumerate(json_strings):
    data = clean_and_parse_json(json_str)
    if data:
        print(f"Key-value pairs for JSON string {i}:")
        for key, value in data.items():
            print(f"{key}: {value}")
