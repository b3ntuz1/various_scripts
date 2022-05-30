'''
Весь цей код був написаний щоб подивитися як зберігати дані в csv.
Більшу частину написаного знайшов в інтернеті. Працювати з coinmaketcap
краще через api, а не парсити їхню сторінку у веб.
'''
import requests
import csv
from bs4 import BeautifulSoup


url = 'https://coinmarketcap.com'

def get_html(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.text
    return "Something were wrong"


def get_all_links(html):
    soup = BeautifulSoup(html, 'lxml')
    div = soup.find_all('div', class_='sc-16r8icm-0 escjiH')
    all_links = [link.find('a', class_='cmc-link') for link in div]
    return [url + i.get('href') for i in all_links]


def get_page_data(html):
    soup = BeautifulSoup(html, 'lxml')

    try:
        h1 = soup.find('h2', class_='sc-1q9q90x-0 jCInrl h1')
        h1 = h1.get_text('|', strip=True).split('|')[0]
    except Exception as e:
        h1 = ''

    try:
        price = soup.find('div', class_='priceValue').get_text()
        price = float(price[1:].replace(',', ''))
    except Exception as e:
        price = ''

    return {
        'name': h1,
        'price': price,
    }


def write_csv(data):
    with open('coinmarketcap.csv', 'a') as fh:
        writer = csv.writer(fh)
        writer.writerow((data['name'], data['price']))
        print(f"{data['name']} -> {data['price']}")


def main():
    html = get_html(url)
    all_links = get_all_links(html)

    for i in all_links:
        page = get_html(i)
        write_csv(get_page_data(page))


if __name__ == "__main__":
	main()

