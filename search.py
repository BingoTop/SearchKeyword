import requests
import asyncio
from bs4 import BeautifulSoup
import time

from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures



header = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    "cache-control": "max-age=0",
    "cookie": "NNB=T5UX6CGRCUAF4; NRTK=ag#all_gr#1_ma#-2_si#0_en#0_sp#0; _ga_7VKFYR6RV1=GS1.1.1579572292.1.1.1579572294.0; _ga=GA1.2.178968408.1579572292; nx_ssl=2; ASID=70a684e6000001701e60097d00000055; BMR=; page_uid=UCWpQlprvmsssPWpSL0ssssstOs-206545",
    "referer": "https://www.naver.com/",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
}
req = requests.get("https://datalab.naver.com/keyword/realtimeList.naver?where=main", headers=header)
soup = BeautifulSoup(req.text, 'html.parser')
urls = [rank.text for rank in soup.select(".item_title_wrap > .item_title")][:10]


def get_links():
    header = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            "cache-control": "max-age=0",
            "cookie": "NNB=T5UX6CGRCUAF4; NRTK=ag#all_gr#1_ma#-2_si#0_en#0_sp#0; _ga_7VKFYR6RV1=GS1.1.1579572292.1.1.1579572294.0; _ga=GA1.2.178968408.1579572292; nx_ssl=2; ASID=70a684e6000001701e60097d00000055; BMR=; page_uid=UCWpQlprvmsssPWpSL0ssssstOs-206545",
            "referer": "https://www.naver.com/",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-site",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
        }

    req = requests.get("https://datalab.naver.com/keyword/realtimeList.naver?where=main", headers=header)
    soup = BeautifulSoup(req.text,'html.parser')
    urls = [rank.text for rank in soup.select(".item_title_wrap > .item_title")][:10]
    return urls

def get_content(link):
    abs_link = "https://search.naver.com/search.naver?where=news&sm=tab_jum&query=" + link
    req = requests.get(abs_link)
    soup = BeautifulSoup(req.text,"html.parser")

    titles = [title.text for title in soup.select("._sp_each_title")]
    urls = [url.get("href") for url in soup.select("#sp_nws1 > dl > dt > a")]
    images= [image.get("src") for image in soup.select("#sp_nws1 > div > a > img")]
    print(titles)
    # for u,i,t in zip(urls,images,titles):
    #     print(t,i,u)

# -------------------------------------------------------------------------------------------
from functools import partial

async def get_text_from_url(url):
    # print(f'send request to ...{url}')
    loop = asyncio.get_event_loop()
    request = partial(requests.get,url,headers=header)
    res = await loop.run_in_executor(None,request)
    print(f'Get response from ...{url}')
    soup = BeautifulSoup(res.text,"html.parser")
    titles = [title.text for title in soup.select("._sp_each_title")]
    urls = [url.get("href") for url in soup.select("#sp_nws1 > dl > dt > a")]
    images= [image.get("src") for image in soup.select("#sp_nws1 > div > a > img")]

    # for u,i,t in zip(urls,images,titles):
    #     print(f't,i,u)
    print(titles)

async def main():
    base_url = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query=/{keyword}'
    # keywords = ['대구 봉쇄', '이명박', '신천지', '이만희', '타다', '거제도 8남매', '고민정', '손흥민 부상', '청와대 국민청원', '홀란드']


    futures = [asyncio.ensure_future(get_text_from_url(base_url.format(keyword=keyword))) for keyword in urls]

    await asyncio.gather(*futures)

if __name__ == '__main__':
    start = time.time()

    # --------멀티쓰레드----------
    pool = Pool(processes=10)
    pool.map(get_content,urls) # 4초
    # pool.map(get_content,get_links()) # 4.2초
    print(time.time()-start) # 6초
    start = time.time()
    # --------비동기----------
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main()) #7.5초
    print(time.time()-start) # 6초

