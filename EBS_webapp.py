from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import csv
import os

app = Flask(__name__)

def get_page(url):
    response = requests.get(url)

    if not response.ok:
        print('Server status code: ', response.status_code)
        return None
    else:
        soup = BeautifulSoup(response.text, 'lxml')
    return soup

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
    # Title
    h1 = soup.find('h1', class_="x-item-title__mainTitle")
    data['Title'] = h1.get_text(strip=True) if h1 else "N/A"

    # Price
    h2 = soup.find('div', class_="x-price-primary")
    data['Price'] = h2.get_text(strip=True) if h2 else "N/A"

    # Items Sold
    h3 = soup.find('div', class_="x-quantity__availability")
    if h3:
        Avb_Sold = h3.get_text(strip=True)
        Avb_Sold = Avb_Sold.replace("available", "available ").replace("sold", " sold")
        data['Availability / Items Sold'] = Avb_Sold
    else:
        data['Availability / Items Sold'] = "N/A"

    return data

def write_to_csv(data, filename):
    file_exists = os.path.exists(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data.keys())

        if not file_exists or os.path.getsize(filename) == 0:
            writer.writeheader()

        writer.writerow(data)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    # Get user inputs
    search_query = request.form.get('search_query')
    filename = request.form.get('filename') or "output.csv"

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

    # Provide a success message
    return render_template('results.html', data=scraped_data, filename=filename)

if __name__ == '__main__':
    app.run(debug=True)
