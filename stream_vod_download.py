import m3u8
import requests
import random
import time
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import json
from urllib.parse import urlparse


def input_vod_url():
    vod_url = input("(Example: https://www.twitch.tv/videos/video_id) \nPlease enter the stream vod url: ")
    return vod_url


random_int = random.randint(1, 10000)


def save_network_logs(stream_vod_url):
    # set chromedriver exe path
    service = Service(executable_path='./chromedriver.exe')

    options = webdriver.ChromeOptions()

    # Chrome will start in Headless mode
    options.add_argument('headless')

    # Ignores any certificate errors if there are any
    options.add_argument("--ignore-certificate-errors")

    # Set logging preferences directly in the options
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(service=service, options=options)

    # Send request to the website and let it load
    driver.get(stream_vod_url)

    # Sleeps for 5 seconds to load all urls
    time.sleep(5)

    # Gets all logs from performance in Chrome
    logs = driver.get_log("performance")

    print("\nNetwork logs saving..")

    # Opens a writable JSON file and writes logs in it
    with open(f"network-logs-{random_int}.json", "w", encoding="utf-8") as f:
        f.write("[")

        # iterate every log and parses it using JSON
        for log in logs:
            network_log = json.loads(log["message"])["message"]

            if ("Network.response" in network_log["method"]
                    or "Network.request" in network_log["method"]
                    or "Network.webSocket" in network_log["method"]):
                # writes network log to json file
                f.write(json.dumps(network_log) + ",")
        f.write("{}]")

    driver.quit()

    print("\nNetwork logs were saved successfully")


def get_stream_network_url():
    print("\nReceiving stream vod network url..")

    json_file_path = f"network-logs-{random_int}.json"

    with open(json_file_path, "r", encoding="utf-8") as f:
        logs = json.loads(f.read())

    for log in logs:
        try:
            # get network urls
            url = log["params"]["request"]["url"]

            # Checks vod url
            if ".cloudfront.net" in url and ".cloudfront.net/dist" not in url:
                parsed_url = urlparse(url)

                # Get scheme and netloc
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

                # Get first part of path
                first_path = parsed_url.path.split('/')[1] if len(parsed_url.path.split('/')) > 1 else ""

                # Combine base URL with  first part of path
                result_url = f"{base_url}/{first_path}"

                print(f"\nStream vod network URL was retrieved successfully")

                return result_url

        except Exception as e:
            pass


def save_stream_vod(vod_url):
    print("\nSaving Stream vod..")

    count = 0

    request_url = requests.get(f'{vod_url}/360p30/index-dvr.m3u8')
    # get content url
    m3u8_master = m3u8.loads(request_url.text)

    # get total segment
    total_segment = len(m3u8_master.data['segments'])

    print('\nTotal segment:', total_segment)

    # save stream vod file
    with open(f'stream-vod-{random_int}.ts', 'wb') as file:
        for row in m3u8_master.data['segments']:
            ts_name = row['uri']
            ts_url = f"{vod_url}/chunked/{ts_name}"
            request_ts_url = requests.get(ts_url)

            file.write(request_ts_url.content)

            count += 1

            print(f'Segment: {total_segment}/{count}')

        print("Stream vod successfully saved")
