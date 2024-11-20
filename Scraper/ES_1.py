import bs4
from bs4 import BeautifulSoup
import requests
import csv
from urllib3.util import url
import lxml.html
import os

def get_page(url):
    response = requests.get(url)

    if not response.ok:
        print('server status code: ',  response.status_code)
        return None
    else:
        soup = BeautifulSoup(response.text,
                             'lxml')
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
#Title:
    h1 = soup.find('h1', class_="x-item-title__mainTitle")
    if h1:
        data['Title'] = h1.get_text(strip=True)
    else:
        data['Title'] = "N/A"
#Price:
    h2 = soup.find('div', class_="x-price-primary" )
    if h2:
        data['Price'] = h2.get_text(strip=True)
    else:
        data['Price'] = "N/A"
#Items Sold:
    h3 = soup.find('div', class_= "x-quantity__availability")
    if h3:
        Avb_Sold = h3.get_text(strip=True)
        Avb_Sold = Avb_Sold.replace("available", "available ").replace("sold", " sold")
        data['Availability / Items Sold'] = Avb_Sold
    else:
        data['Availability / Items Sold'] = "N/A"

    return data

#writing data to CSV:

def write_to_csv(data, filename = "SHOE.csv"):
    file_exists = os.path.exists(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames = data.keys())

        if not file_exists or os.path.getsize(filename) == 0:
            writer.writeheader()

        writer.writerow(data)


def main():
    # Get user input
    search_query = input("Enter the search term (e.g., climbing shoes): ")
    filename = input("Enter the CSV filename (default: output.csv): ") or "output.csv"

    # Build the eBay search URL
    listingurl = f"https://www.ebay.com/sch/i.html?_from=R40&_nkw={search_query.replace(' ', '+')}&_sacat=0&_ipg=240"

    # Collect product URLs and scrape data
    product_url = collect_product_urls(listingurl)

    for url in product_url:
        print(f"Collecting data for {url}")
        soup = get_page(url)
        if soup:
            data = get_detail_data(soup)
            print(data)
            write_to_csv(data, filename)

    # Confirm file writing
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        print(f"Data successfully written to {filename}")
    else:
        print(f"Failed to write data to {filename}")


def check_csv_file(filename="SHOE.csv"):
    # Check if the file exists
    if os.path.exists(filename):
        # Check if the file is not empty
        if os.path.getsize(filename) > 0:
            print(f"{filename} was successfully written and is not empty.")
        else:
            print(f"{filename} exists but is empty.")
    else:
        print(f"{filename} does not exist.")


if __name__ == '__main__':
    main()




