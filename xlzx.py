import requests
import urllib
from bs4 import BeautifulSoup


def get_link(wd):
    url = 'http://xlyy100.com/index.php?m=vod-search-pg-1-wd-%s.html' % urllib.parse.quote(wd)
    headers = {
        'User-Agent':  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                        Chrome/66.0.3359.139 Safari/537.36',
        'Referer': url,
        'Host': 'xlyy100.com',
    }
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")
    num = soup.find(class_='count').text
    if int(num) <= 0:
        return None
    else:
        data = soup.find(class_='link')
        link = data.get('href')
        stext = data.find_all('p')
        info = '\n'.join([each.text for each in stext])
        url2 = 'http://xlyy100.com%s' % link
        r2 = requests.get(url2, headers=headers)
        soup2 = BeautifulSoup(r2.content, "html.parser")
        link_data = soup2.find_all(class_='playlist')
        source1 = link_data[0].find_all('a')
        source2 = link_data[1].find_all('a')
        links1 = '\n'.join([each.get('title') + '：http://xlyy100.com' + each.get('href') for each in source1[-10:]])
        links2 = '\n'.join([each.get('title') + '：http://xlyy100.com' + each.get('href') for each in source2[-10:]])
        return '\n'.join([info, links1, '备用源：', links2])


if __name__ == '__main__':
    # result = get_link('名侦探柯南')
    result = get_link('unnatural')
    print(result)

