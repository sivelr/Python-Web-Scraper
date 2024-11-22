from celery import Celery
from bs4 import BeautifulSoup
import requests
import csv
import os

# Initialize Celery
redis_url = os.environ.get('REDIS_URL', 'redis://red-csvv58m8ii6s73ff506g:6379')
celery_app = Celery('tasks', broker=redis_url)

# Helper Functions
def get_page(url):
    response = requests.get(url)
    if not response.ok:
        return None
    return BeautifulSoup(response.text, 'lxml')

def collect_product_urls(listingurl):
    soup = get_page(listingurl)
    product_urls = []
    if soup:
        links = soup.select('.s-item__link')
        for link in links:
            product_url = link.get('href')
            if product_url and product_url.startswith('http'):
                product_urls.append(product_url)
    return product_urls

def get_detail_data(soup):
    data = {}
    h1 = soup.find('h1', class_="x-item-title__mainTitle")
    data['Title'] = h1.get_text(strip=True) if h1 else "N/A"
    h2 = soup.find('div', class_="x-price-primary")
    data['Price'] = h2.get_text(strip=True) if h2 else "N/A"
    h3 = soup.find('div', class_="x-quantity__availability")
    if h3:
        Avb_Sold = h3.get_text(strip=True).replace("available", "available ").replace("sold", " sold")
        data['Availability / Items Sold'] = Avb_Sold
    else:
        data['Availability / Items Sold'] = "N/A"
    return data

def write_to_csv(data, filename):
    file_exists = os.path.exists(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

# Celery Task for Scraping
@celery_app.task
def scrape_task(search_query, filename="output.csv"):
    # Build the eBay search URL
    listingurl = f"https://www.ebay.com/sch/i.html?_from=R40&_nkw={search_query.replace(' ', '+')}&_sacat=0&_ipg=240"

    # Collect product URLs and scrape data
    product_urls = collect_product_urls(listingurl)
    scraped_data = []

    for url in product_urls:
        soup = get_page(url)
        if soup:
            data = get_detail_data(soup)
            scraped_data.append(data)
            write_to_csv(data, filename)

    return scraped_data  # This result will be available after the task completes

