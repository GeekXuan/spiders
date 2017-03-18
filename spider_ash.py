import urllib.request as u
from bs4 import BeautifulSoup
import re,os,codecs,threading

except_links = []

def url_open(url,decode = True):
    #得到并返回转码后的网页列表
    req = u.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36')
    req.add_header('Referer', 'http://www.ashvsash.com/')
    res = u.urlopen(req)
    html = res.read()
    if decode:
        return html.decode('utf-8')
    else:
        return html

def get_source(url):
    #获取资源
    global except_links
    try:
        html = url_open(url)
        soup = BeautifulSoup(html,"html.parser")
        type_ = soup.find(rel="category tag").string
        title = soup.find('title').string.split('|')[0]
        p = r'(?:https*://pan\.baidu\.com/s/[A-z|0-9]{6,8})'
        links = re.findall(p,html)
        print(title, type_,links)
        if len(links) != 0:
            with codecs.open('movie.txt','a','utf-8') as f:
                f.write('------------------------------------------------------------\r\n')
                f.write(title + '('+ type_ + '):\r\n')
                f.write('网页链接：' + url + '\r\n')
                for i in range(len(links)):
                    a = html.find(links[i])
                    b = html.find('密码',a-255,a+255)
                    psw = html[b:b+8]
                    psw = psw.partition('<')[0]
                    #合集找小标题
                    title_l = ''
                    if len(links) > 1:
                        c = html.find('>',a+1,a+255)
                        title_l = html[c:c+64]
                        if title_l != '' and title_l.find('>') != -1:
                            title_l = title_l.split('>')[1].split('<')[0].strip()
                        if title_l.endswith('点我'):
                            title_l = title_l[:-2]
                    if title_l != '':
                        f.write(title_l + '\t')
                        print(title_l,end = '  ')
                    f.write(links[i] + '\t' + psw + '\r\n')
                    print(links[i] + '\t' + psw)
                f.write('\r\n')
            f.close()
    except Exception as e:
        print(Exception,'in get_source:',e)
        if url not in except_links:
            except_links.append(url)

def get_links(url):
    html = url_open(url)
    soup = BeautifulSoup(html,"html.parser")
    end_page = soup.find(class_ = 'extend')['href']
    end_num = int(end_page.split('/')[-1])
    links = []
    for i in range(1,end_num + 1):
    #for i in range(25,27):
        links = []
        print('=======================第',i,'页，共',end_num,'页======================')
        url_n = 'http://www.ashvsash.com/page/' + str(i)
        html_n = url_open(url_n)
        soup_n = BeautifulSoup(html_n,"html.parser")
        article = soup_n.find_all(class_ = 'thumbnail')
        for each in article:
            links.append(each.a['href'])
        #print(links)
        threads(links,get_source)
        

def threads(link_list,func):
    threadpool = []
    global except_links
    for each in link_list:
        try:
            th = threading.Thread(target = func, args = (each,))
            threadpool.append(th)
        except Exception as e:
            print(Exception,':',e)
            if url not in except_links:
                except_links.append(url)
    for th in threadpool:
        th.start()
    for th in threadpool:
        threading.Thread.join(th)

def main():
    global except_links
    url = 'http://www.ashvsash.com'
    try:
        get_links(url)
        while len(except_links) != 0:
            print('==================出错重试,共',len(except_links),'个。=================')
            print()
            print(except_links)
            get_source(except_links.pop())
        print('爬取完毕。')
    except Exception as e:
        print(Exception ,'in main:',e)
    
    

if __name__=='__main__':
    print('请选择：\r\n1.完整爬取。')
    flag = True
    while(flag):
        flag = False
        choice = input()
        if choice == '1':
            main()
        else:
            print('输入错误，请重新选择：')
            flag = True
