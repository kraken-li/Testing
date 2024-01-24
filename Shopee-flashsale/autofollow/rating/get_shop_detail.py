import asyncio
import aiohttp
import async_timeout

import pandas as pd
from bs4 import BeautifulSoup
import json
import time
import datetime
import os


class Crawler_shop_detail:
    def __init__(self):
        self.basepath = os.path.abspath(os.path.dirname(__file__))

        self.shop_detail_api = 'https://shopee.vn/api/v2/shop/get?shopid='

        self.shop_detail_dict = {
            'shop_name': [], 
            'shopid': [], 
            'shop_ctime': [], 
            'shop_country': [], 
            'shop_item_count': [], 
            'shop_place': [], 
            'shop_rating_star': [], 
            'shop_rating_bad': [],
            'shop_rating_normal': [],
            'shop_rating_good': [],
        }

    def __call__(self, input_shop_ids):
        async def parser_shop_html(html):
            shop = json.loads(html)

            dateArray = datetime.datetime.utcfromtimestamp(
                shop['data']['ctime'])
            transfor_time = dateArray.strftime("%Y-%m-%d %H:%M:%S")
            self.shop_detail_dict['shop_ctime'].append(transfor_time)
            self.shop_detail_dict['shopid'].append(shop['data']['shopid'])
            self.shop_detail_dict['shop_name'].append(shop['data']['name'])
            self.shop_detail_dict['shop_country'].append(
                shop['data']['country'])
            self.shop_detail_dict['shop_item_count'].append(
                shop['data']['item_count'])
            self.shop_detail_dict['shop_place'].append(shop['data']['place'])
            self.shop_detail_dict['shop_rating_star'].append(
                shop['data']['rating_star'])
            self.shop_detail_dict['shop_rating_bad'].append(
                shop['data']['rating_bad'])
            self.shop_detail_dict['shop_rating_normal'].append(
                shop['data']['rating_normal'])
            self.shop_detail_dict['shop_rating_good'].append(
                shop['data']['rating_good'])

        async def get_shop_detail(client, query_url):
            try:
                async with client.get(query_url) as response:
                    html = await response.text()
                    assert response.status == 200
                    await parser_shop_html(html)
            except Exception as e:
                print('---Exception---:', e)

        async def main(crawler_shop_urls):
            headers = {'User-Agent': 'Googlebot'}
            async with aiohttp.ClientSession(
                    connector=aiohttp.TCPConnector(ssl=False, limit=100),
                    headers=headers,
            ) as client:
                tasks = [
                    get_shop_detail(client, query_url)
                    for query_url in crawler_shop_urls
                ]
                await asyncio.gather(*tasks)

        crawler_shop_urls = []
        for id in range(len(input_shop_ids)):
            crawler_shop_urls.append(self.shop_detail_api +
                                     str(input_shop_ids[id]))
        asyncio.run(main(crawler_shop_urls))

        df = pd.DataFrame(self.shop_detail_dict)
        df.to_csv(self.basepath + '/csv/shop_detail.csv', index=False)
        return df


if __name__ == "__main__":
    # // api example
    # https://shopee.vn/api/v2/shop/get?shopid=31945247

    time_start = time.time()

    input_shop_ids = [
        5547415, 22189057, 1517097, 3323966, 1971812, 8016627, 80078149,
        7314701, 151143321, 47924061, 29951329, 9532352, 15659558, 31945247
    ]

    do = Crawler_shop_detail()
    result = do(input_shop_ids)

    print(result)
    print(time.time() - time_start)
