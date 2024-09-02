import pandas as pd
import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import Json
import re  # Ensure this import is included
import json

# Database connection details
db_params = {
    'dbname': 'web_scraping',
    'user': 'postgres',
    'password': 'cm9oYW5AdHN0LW1vaGl0Cg==',
    'host': '91.203.133.118',
    'port': '5432'
}

def connect_to_db():
    try:
        conn = psycopg2.connect(**db_params)
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def convert_to_int(value):
    """ Convert a value with suffix (K, M, B) to an integer. """
    if isinstance(value, str):
        value = value.replace(',', '').upper()  # Remove commas and convert to uppercase
        match = re.match(r'(\d+\.?\d*)\s*([KMB]?)', value)
        if match:
            number, suffix = match.groups()
            number = float(number)
            if suffix == 'K':
                number *= 1_000
            elif suffix == 'M':
                number *= 1_000_000
            elif suffix == 'B':
                number *= 1_000_000_000
            return int(number)
    return None

def insert_channel_info(conn, channel_id, description, overall_score, additional_metrics):
    with conn.cursor() as cursor:
        insert_query = """
        INSERT INTO channel_info (channel_id, description, overall_score, subscribers, video_views, monthly_earnings, engagement_rate, video_upload_frequency, average_video_length)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            channel_id,
            description.get('description', None),
            overall_score,
            additional_metrics.get('Subscribers', None),
            additional_metrics.get('Video views', None),
            additional_metrics.get('Monthly Earnings', None),
            additional_metrics.get('Engagement rate', None),
            additional_metrics.get('Video Upload Frequency', None),
            additional_metrics.get('Average Video Length', None)
        ))
        conn.commit()

def insert_daily_performance(conn, channel_id, daily_data):
    with conn.cursor() as cursor:
        insert_query = """
        INSERT INTO daily_performance (channel_id, date, subscribers, views, estimated_earnings)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (date) DO NOTHING
        """
        for data in daily_data:
            cursor.execute(insert_query, (
                channel_id,
                data['Date'],
                convert_to_int(data['Subscribers']),
                convert_to_int(data['Views']),
                data['Estimated Earnings']
            ))
        conn.commit()

def insert_graph_data(conn, channel_id, graph_type, graph_data):
    with conn.cursor() as cursor:
        insert_query = """
        INSERT INTO graph_data (channel_id, graph_type, data)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (channel_id, graph_type, Json(graph_data)))
        conn.commit()

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

def fetch_and_insert_channel_data(channel_id, conn):
    url = f'https://vidiq.com/youtube-stats/channel/{channel_id}/'
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

        try:
            # Insert channel information
            insert_channel_info(conn, channel_id, description, overall_score, additional_metrics)

            # Insert daily performance data
            insert_daily_performance(conn, channel_id, daily_performance)

            # Insert graph data
            insert_graph_data(conn, channel_id, "GRAPH 1", script_data_5)
            insert_graph_data(conn, channel_id, "GRAPH 2", script_data_4)
            insert_graph_data(conn, channel_id, "GRAPH 3", script_data_6)
        except Exception as e:
            print(f"Error during database operations for channel {channel_id}: {e}")
    else:
        print(f"Failed to retrieve the webpage for channel {channel_id}. Status code: {response.status_code}")

def main():
    # Path to your CSV file
    file_path = r'C:\Users\Anup\Downloads\channels_test.csv'
    
    # Read the CSV file using pandas
    df = pd.read_csv(file_path)
    
    # Get the list of channel IDs from the 'channelid' column
    channel_ids = df['channelid'].tolist()

    # Connect to PostgreSQL
    conn = connect_to_db()
    if conn:
        try:
            # Iterate over the channel IDs and fetch/insert data for each
            for channel_id in channel_ids:
                fetch_and_insert_channel_data(channel_id, conn)
            print("All channel data have been successfully inserted into the database.")
        except Exception as e:
            print(f"Error during database operations: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    main()
