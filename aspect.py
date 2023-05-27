import requests
from bs4 import BeautifulSoup
from pathlib import Path
import json
import os

requests.packages.urllib3.disable_warnings()
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,'
              'application/signed-exchange;v=b3;q=0.7',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 '
                  'Safari/537.36 '
}

url = 'https://oboi-aspect.ru'
catalogurl = 'https://oboi-aspect.ru/catalog/'
pagenurl = 'https://oboi-aspect.ru/catalog/?PAGEN_1='
# count of page for pagen
cnt_page = 2

if not os.path.exists(Path('data/images')):
    Path('data/images').mkdir(parents=True)

result = requests.get(url=catalogurl, verify=False, headers=headers)
if result.status_code == 200:
    soup = BeautifulSoup(result.text, 'lxml')

    image_dct = []

    for page in range(1, cnt_page + 1):
        print(f'{page} страница каталога из {cnt_page} страниц.')
        result = requests.get(url=f'{pagenurl}{page}', verify=False)
        soup = BeautifulSoup(result.text, 'lxml')

        # find all collection and download images for collection
        all_products = soup.find_all('div', class_='field-cards__row-item')
        print(f'Найдено {len(all_products)} объектов.')
        for product in all_products:

            # request page of product
            # create new link
            link = url + product.find(class_='goods-card__image').get('href')
            result = requests.get(link, verify=False, headers=headers)
            soup = BeautifulSoup(result.text, 'lxml')

            item = soup.find('div', class_='item')
            item_link = url + item.find(class_='catalog-item inner').get('href')
            result = requests.get(url=item_link, verify=False, headers=headers)
            soup = BeautifulSoup(result.text, 'lxml')

            # find name collection and model
            name = soup.find('h1', class_="h1").get_text('\n', strip=True)
            collection = name.split(' ')[0]
            model = name.split(' ')[-1]
            print(f'Загружается коллекция {collection}.')

            all_image = soup.find('div', class_='swiper-wrapper').find_all('div', class_='swiper-slide')
            for image in all_image:
                imgurl = url + image.find('img').get('src')
                name = imgurl.split('/')[-1]
                res = requests.get(url=imgurl, headers=headers, verify=False)
                content = res.content
                image_dct.append({name: (model, collection)})
                with open(Path(f'data/images/{name}'), 'wb') as file:
                    file.write(content)

    with open(Path('catalog/aspect.json'), 'w', encoding='utf-8') as file:
        json.dump(image_dct, file, indent=4, ensure_ascii=False)
else:
    print(f'Error {result.status_code}')
