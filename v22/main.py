import urllib3
import requests as rq
import threadpool
from bs4 import BeautifulSoup as bs
from spiders.v22 import backend

URL = 'http://www.v22q.com/cn/vl_searchbyid.php?keyword=%s'
URL_PAGE = 'http://www.v22q.com/cn/vl_searchbyid.php?keyword=%s&page=%d'
URL_INFO = 'http://www.v22q.com/cn/?v=%s'

HEADERS = {
    'Host': 'www.v22q.com',
    'Cookie': '__cfduid=d6e8301e7b956341d265db1e0def149561536764954; timezone=-480; __qca=P0-343588147-1536764964166; '
              'over18=18; __atuvc=49%7C37; __atuvs=5b9cae72a7c2a4b7008',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/69.0.3497.81 Safari/537.36',
}

LIST = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
        'o', 'p', 'q', 'r', 's', 't', 'v', 'u', 'v', 'w', 'x', 'y', 'z']


def get_keyword():  # 生成keyword存入
    # 2位
    result = []
    for i in LIST:
        for j in LIST:
            keyword = i + j
            result.append(keyword)
            if len(result) > 100:
                backend.insert_keyword(result)
                result = []
    backend.insert_keyword(result)
    # 3位
    result = []
    for i in LIST:
        for j in LIST:
            for p in LIST:
                keyword = i + j + p
                result.append(keyword)
                if len(result) > 100:
                    backend.insert_keyword(result)
                    result = []
    backend.insert_keyword(result)
    # 4位
    result = []
    for i in LIST:
        for j in LIST:
            for p in LIST:
                for q in LIST:
                    keyword = i + j + p + q
                    result.append(keyword)
                    if len(result) > 100:
                        backend.insert_keyword(result)
                        result = []
    backend.insert_keyword(result)


def get_page(keyword):  # 获取每一页的信息
    r = rq.get(URL % keyword, HEADERS, timeout=200)
    # print(r.text)
    soup = bs(r.content, "html.parser")
    # 判断该keyword是否有结果
    result = soup.find('em')
    if result:
        status = 0
        return [status]
    else:
        status = 1
        page_soup = soup.find(class_='page last')
        if page_soup:
            page = int(page_soup['href'].split('page=')[-1])
            urls = get_url(soup)
            for i in range(2, page + 1):
                r = rq.get(URL_PAGE % (keyword, i), HEADERS)
                soup = bs(r.content, "html.parser")
                urls.extend(get_url(soup))
            count = len(urls)
        else:
            page = 1
            urls = get_url(soup)
            count = len(urls)
        return [status, page, count, urls]


def get_url(soup):  # 获取每一条的url
    urls = [each['id'].lstrip('vid_') for each in soup.find_all(class_='video')]
    return urls


def get_info(main_id, url):  # 获取每一条的详细信息
    r = rq.get(URL_INFO % url, HEADERS, timeout=30)
    if r.status_code == 200:
        soup = bs(r.content, "html.parser")
        title = soup.find(id='video_title').find('a').text.replace('\'', '"')
        v_id = soup.find(id='video_id').find(class_='text').text
        v_date = soup.find(id='video_date').find(class_='text').text
        v_length = soup.find(id='video_length').find('span').text
        # 导演
        v_director_soup = soup.find(id='video_director').find('a')
        if v_director_soup:
            v_director = v_director_soup.text.replace('\'', '"')
        else:
            v_director = ''
        # 制造商
        v_maker_soup = soup.find(id='video_maker').find('a')
        if v_maker_soup:
            v_maker = v_maker_soup.text.replace('\'', '"')
        else:
            v_maker = ''
        # 发行商
        v_label_soup = soup.find(id='video_label').find('a')
        if v_label_soup:
            v_label = v_label_soup.text.replace('\'', '"')
        else:
            v_label = ''
        v_review_soup = soup.find(id='video_review')
        if v_review_soup:
            v_review = v_review_soup.find(class_='score').text[1:-1]
        else:
            v_review = ''
        v_genres = ','.join([each.text for each in soup.find(id='video_genres').find_all('a')])
        # 演员
        v_cast_soup = soup.find(id='video_cast').find('a')
        if v_cast_soup:
            v_cast = v_cast_soup.text.replace('\'', '"')
        else:
            v_cast = ''
        image_link = soup.find(id='video_jacket_img')['src']
        image_url = 'http:' + image_link
        image_name = v_id + image_link.split('/')[-1]
        # 存图片
        # image = rq.get(image_url, timeout=30).content
        # with open(os.path.join('image', image_name), 'wb') as f:
        #     f.write(image)
        comment_soup = soup.find(id='video_comments')
        comments = [each.text.replace('\'', '"') for each in comment_soup.find_all('textarea')]
        data = {
            'main_id': main_id,
            'title': title,
            'code': v_id,
            'date': v_date,
            'length': v_length,
            'director': v_director,
            'producer': v_maker,
            'publisher': v_label,
            'score': v_review,
            'type': v_genres,
            'actor': v_cast,
            'img': image_name,
            'img_url': image_url,
            'comments': comments,
        }
        backend.update_main(data)
    elif r.status_code == 404:
        backend.update_main_404(main_id)


def get_keyword_info(keyword_id, keyword):
    info = get_page(keyword)
    info.append(keyword_id)
    backend.update_keyword(info)


def main():
    mutil_num = 100
    while True:
        try:
            keyword_list = backend.query_keyword()
            if keyword_list:
                func_vars = [(each, None) for each in keyword_list]
                pool = threadpool.ThreadPool(mutil_num)
                requests = threadpool.makeRequests(get_keyword_info, func_vars)
                [pool.putRequest(req) for req in requests]
                pool.wait()
                # time.sleep(5)
            else:
                break
        except (rq.exceptions.ConnectionError, urllib3.exceptions.ProtocolError) as e:
            print(e)
            raise SystemExit
        except Exception as e:
            print(e)
            raise SystemExit
    while True:
        try:
            main_list = backend.query_main()
            if main_list:
                func_vars = [(each, None) for each in main_list]
                pool = threadpool.ThreadPool(mutil_num)
                requests = threadpool.makeRequests(get_info, func_vars)
                [pool.putRequest(req) for req in requests]
                pool.wait()
                # time.sleep(5)
            else:
                break
        except (rq.exceptions.ConnectionError, urllib3.exceptions.ProtocolError) as e:
            print(e)
            raise SystemExit
        except Exception as e:
            print(e)
            raise SystemExit


if __name__ == '__main__':
    # get_page('aaaa')
    # get_info('javli4zjry', 1)
    # get_keyword()
    main()
