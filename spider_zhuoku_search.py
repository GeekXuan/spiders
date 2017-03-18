import urllib.request as u
import urllib.parse as p
import os,re
from bs4 import BeautifulSoup

def search():
    name = input('请输入要下载的壁纸名称：')
    url = 'http://www.zhuoku.com/search/' + p.quote(name.encode('gbk'))
    html = url_open(url).decode('gb2312', 'ignore')
    soup = BeautifulSoup(html, "html.parser")
    lis = soup.find(id = 'liebiao').ul.find_all('li')
    if not lis:
        print('没有搜索到该类壁纸，请重试！')
        search()
    else:
        name = str_del(name)
        try:
            os.mkdir(name)
        except FileExistsError:
            pass
        os.chdir(name)
        for li in lis:
            title = li.a.string
            num = re.findall('共.{1,3}张', str(li))[0][1:-1]
            urls = 'http://www.zhuoku.com' + li.a['href']
            pic_urls = []
            for i in range(int(num)):
                pic_url = urls.replace('.htm', '(%d).htm'%(i+1))
                pic_urls.append(pic_url)
            save_pic(pic_urls,title)

def str_del(string):
    #处理字符串
    ban = ['\\','/',':','*','','"','<','>','|']
    for i in  string:
        if  i in ban:
           string = string.replace(i,'')
    return string

def save_pic(pic_urls,title):
    title = str_del(title)
    #保存图片
    try:
        os.mkdir(title)
        os.chdir(title)
        for i in range(len(pic_urls)):
            #得到每张图片
            html = url_open(pic_urls[i]).decode('gb2312', 'ignore')
            soup = BeautifulSoup(html, "html.parser")
            pic = soup.find(id = 'bizhiimg').p.a.img['src']
            filename = soup.find(id = 'bizhiimg').p.a.img['alt'] + '.jpg'
            filename = str_del(filename)
            #保存
            with open(filename,'wb') as f:
                print('已保存：' + filename)
                img = url_open(pic)
                f.write(img)
        os.chdir('..')
    except FileExistsError:
        pass

def url_open(url):
    #得到并返回转码后的网页列表
    req = u.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')
    req.add_header('Referer', 'http://www.zhuoku.com')
    res = u.urlopen(req)
    html = res.read()
    return html
    
def main():
    #先只下载第一页的壁纸
    url = 'http://www.zhuoku.com/new/index.html'
    #注意，该网页的编码方式是gb2312
    html = url_open(url).decode('gb2312', 'ignore')
    soup = BeautifulSoup(html, "html.parser")
    divs = soup.find_all(id = "xinbizhi")#得到div的列表
    for div in divs:
        #使用BeautifulSoup来得到需要的信息
        title = div.a['title']
        num = re.findall('共有.{1,3}张', str(div))[0][2:-1]
        urls = 'http://www.zhuoku.com' + div.a['href']
        pic_urls = []
        for i in range(int(num)):
            pic_url = urls.replace('.htm', '(%d).htm'%(i+1))
            pic_urls.append(pic_url)
        save_pic(pic_urls,title)


if __name__ == '__main__':
    search()
    print('下载完毕。')
