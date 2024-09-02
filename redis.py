import requests
from bs4 import BeautifulSoup
import re
import json
import psycopg2
from psycopg2.extras import Json
import redis
import multiprocessing as mp

# Database connection details
db_params = {
    'dbname': 'web_scrapping',
    'user': 'postgres',
    'password': 'Adityaraj@2013',
    'host': 'localhost',
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

def insert_channel_info(conn, description, overall_score, additional_metrics):
    with conn.cursor() as cursor:
        insert_query = """
        INSERT INTO channel_info (description, overall_score, subscribers, video_views, monthly_earnings, engagement_rate, video_upload_frequency, average_video_length)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
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

def insert_daily_performance(conn, daily_data):
    with conn.cursor() as cursor:
        insert_query = """
        INSERT INTO daily_performance (date, subscribers, views, estimated_earnings)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (date) DO NOTHING
        """
        for data in daily_data:
            cursor.execute(insert_query, (
                data['Date'],
                convert_to_int(data['Subscribers']),
                convert_to_int(data['Views']),
                data['Estimated Earnings']
            ))
        conn.commit()

def insert_graph_data(conn, graph_type, graph_data):
    with conn.cursor() as cursor:
        insert_query = """
        INSERT INTO graph_data (graph_type, data)
        VALUES (%s, %s)
        """
        cursor.execute(insert_query, (graph_type, Json(graph_data)))
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

def process_channel(channel_id):
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

        # Connect to PostgreSQL
        conn = connect_to_db()
        if conn:
            try:
                # Insert channel information
                insert_channel_info(conn, description, overall_score, additional_metrics)

                # Insert daily performance data
                insert_daily_performance(conn, daily_performance)

                # Insert graph data
                insert_graph_data(conn, "GRAPH 1", script_data_5)
                insert_graph_data(conn, "GRAPH 2", script_data_4)
                insert_graph_data(conn, "GRAPH 3", script_data_6)
            except Exception as e:
                print(f"Error during database operations: {e}")
            finally:
                conn.close()

        print(f"Data transfer for {channel_id} completed successfully.")
    else:
        print(f"Failed to retrieve the webpage for {channel_id}. Status code: {response.status_code}")

def worker(redis_conn):
    while True:
        channel_json = redis_conn.lpop('channel_queue')
        if channel_json is None:
            break  # No more items in the queue
        channel = json.loads(channel_json)
        process_channel(channel['channelid'])

def main():
    redis_conn = redis.StrictRedis(host='localhost', port=6379, db=0)

    # Create a pool of workers
    num_processes = 4
    pool = mp.Pool(processes=num_processes)

    # Start the worker processes
    pool.map(worker, [redis_conn] * num_processes)

    pool.close()
    pool.join()

if __name__ == "__main__":
    main()
