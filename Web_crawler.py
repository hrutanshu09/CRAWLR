import csv
import requests
from bs4 import BeautifulSoup
import argparse
import re
import time
from tqdm import tqdm
from colorama import Fore, Style

def create_ascii_banner():
    banner = f"""
{Fore.YELLOW}{Style.BRIGHT}
+====================================================+
|                                                    |
|                                                    |
|   _______  ______ _______ _  _  _         ______   |
|   |       |_____/ |_____| |  |  | |      |_____/   |
|   |_____  |    \_ |     | |__|__| |_____ |    \_   |
|  BY : HRUTANSHU KURANKAR                           |
|                                                    |
+====================================================+
{Style.RESET_ALL}
    """
    print(banner)

def create_file(file_path, output_file, urls_file):
    try:
        with open(file_path, 'w') as file:
            pass
        with open(output_file, 'w') as file:
            pass
        with open(urls_file, 'w') as file:
            pass
        print(f"{Fore.GREEN}{Style.BRIGHT}Files created: {file_path}, {output_file}, {urls_file}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}{Style.BRIGHT}An Error occurred: {Style.RESET_ALL}", e)
        exit()

def get_data(url):
    try:
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        table_of_contents = soup.find("div", id="toc")
        if not table_of_contents:
            print(f"No table of contents found for {url}")
            return []

        headings = table_of_contents.find_all("li")
        data = []
        for heading in headings:
            heading_text = heading.find("span", class_="toctext").text
            heading_number = heading.find("span", class_="tocnumber").text
            data.append({
                'heading_number': heading_number,
                'heading_text': heading_text,
            })
        print(f"Data collected from {url}: {data}")
        return data
    except Exception as e:
        print(f"An error occurred while scraping {url}: {e}")
        return []

def export_data(data, file_name):
    try:
        with open(file_name, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=['heading_number', 'heading_text'])
            writer.writeheader()
            writer.writerows(data)
        print(f"Data successfully exported to {file_name}")
    except Exception as e:
        print(f"Failed to write to {file_name}: {e}")

def get_links(seed_url, file_path, urls_file, depth):
    try:
        response = requests.get(seed_url, verify=False)
        html_content = response.text
        link_regex = r"(https?://(?:[^\s\"]+/?))"
        count = 0
        with open(file_path, 'w') as file, open(urls_file, 'w') as urls_file:
            for line in html_content.splitlines():
                new_urls = re.findall(link_regex, line)
                if new_urls:
                    for url in new_urls:
                        stripped_url = url.strip('"')
                        try:
                            link_response = requests.head(stripped_url, verify=False)
                            content_type = link_response.headers.get('Content-Type')
                            if content_type and content_type.startswith('text'):
                                link_response = requests.get(stripped_url, verify=False)
                                if link_response is not None and hasattr(link_response, 'text') and link_response.text.strip():
                                    file.write(stripped_url + '\n')
                                    urls_file.write(stripped_url + '\n')
                                    count += 1
                        except requests.RequestException as e:
                            print(f"Request error for URL {stripped_url}: {e}")
                        if count == depth:
                            break 
                if count == depth:
                    break       
        print(f"Links saved to {file_path} and {urls_file}")
    except Exception as e:
        print(f"{Fore.RED}{Style.BRIGHT}Error message: {Style.RESET_ALL}", e)
        exit()

def crawl(url, output_file):
    try:
        response = requests.get(url, verify=False)
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text(separator=' ', strip=True)
        with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
            csvfile.write(soup.title.text + '\n')
            csvfile.write(text_content.strip() + '\n')
        print(f"Data written to {output_file} for URL {url}")
    except Exception as e:
        print(f"\n{Fore.RED}{Style.BRIGHT}Error message for url{Style.RESET_ALL} {url}: ", e)
    else:
        print("\n")
        with tqdm(desc=f"{Fore.YELLOW}{Style.BRIGHT}Crawling url:-{Style.RESET_ALL} {url}", total=100) as pbar:
            for i in range(100): 
                time.sleep(0.02)  
                pbar.update(1)

def main():
    create_ascii_banner()
    parser = argparse.ArgumentParser(description="Web Crawler")
    parser.add_argument('-u', '--url', required=True, help='Seed URL to start crawling from')
    parser.add_argument('-d', '--depth', required=True, type=int, help='Crawl depth (number of links to follow)')
    args = parser.parse_args()

    seed_url = args.url
    crawl_depth = args.depth

    file_path = 'url.txt'
    output_file = 'output_data.csv'
    urls_file = 'output_urls.txt'

    create_file(file_path, output_file, urls_file)

    print(f"Starting crawl at {seed_url} with depth {crawl_depth}")
    get_links(seed_url, file_path, urls_file, crawl_depth)

    with open(file_path, 'r') as file:
        urls = file.readlines()
        if not urls:
            print(f"{Fore.RED}{Style.BRIGHT}No URLs found in {file_path}{Style.RESET_ALL}")
        for line in urls:
            url = line.strip()
            if url:
                time.sleep(2)
                data = get_data(url)
                if data:
                    file_name = f"output_{url.replace('/', '_').replace(':', '_')}.csv"
                    export_data(data, file_name)
                crawl(url, output_file)
                print(f"Crawled {url}")

    print(f"\n{Fore.RED}{Style.BRIGHT}CRAWLING AND DATA EXTRACTION COMPLETE. DATA SAVED IN FILES '{output_file}' AND '{urls_file}'{Style.RESET_ALL}")

if __name__ == '__main__':
    main()
